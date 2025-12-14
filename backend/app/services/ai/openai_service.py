import json
import os
import time
from typing import Any, Dict, Optional

from loguru import logger
from openai import OpenAI
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.interfaces.ai_provider import AiProvider
from app.observability import metrics
from app.services.ai.ai_audit_service import AIAuditService
from app.services.ai.ai_budget import BudgetManager
from app.services.ai.ai_moderation import AIModeration
from app.services.ai.circuit_breaker import AICircuitBreaker
from app.services.ia_usage_service import IAQuotaExceeded, IAUsageService
from app.services.config.tenant_prompt_config import get_tenant_prompt_config
from app.services.prompts.router.prompt_router import PromptRouter
from app.utils.masking import mask_payload
from app.services.pricing import get_plan_limits
from app.models.tenants import BillingStatus, PlanEnum


class OpenAIService(AiProvider):
    """
    Implementación de proveedor IA basada en OpenAI,
    con soporte para:
    - prompts avanzados por flujo (PromptRouter)
    - configuración por tenant (tenant_prompt_config)
    - modelo primario / fallback (stub para control de costes)
    """

    def __init__(self):
        self.settings = get_settings()
        self.api_key = os.getenv("OPENAI_API_KEY")
        disable_db = os.getenv("DISABLE_DB") == "1"
        if disable_db and not os.getenv("REDIS_URL"):
            os.environ["REDIS_URL"] = "memory://"
            self.settings.redis_url = "memory://"
        self.use_ai_env = bool(self.settings.use_ia) or bool(self.api_key) or disable_db
        self.base_enabled = bool(self.api_key and self.use_ai_env) or disable_db
        self.is_enabled = self.base_enabled
        self.model = "gpt-4.1-mini"
        self.budget = BudgetManager()
        self.client = None
        if not disable_db and self.base_enabled:
            try:
                self.client = OpenAI(api_key=self.api_key)
            except Exception:
                self.client = None
        if self.client is None:
            # Stub mínimo para tests sin API real; permite monkeypatch de chat.completions
            class _DummyCompletions:
                def create(self, **kwargs):
                    return None

            class _DummyChat:
                def __init__(self):
                    self.completions = _DummyCompletions()
            class _DummyClient:
                def __init__(self):
                    self.chat = _DummyChat()
            self.client = _DummyClient()
        self.moderation = AIModeration()
        self.audit = AIAuditService()
        self.circuit_breaker = AICircuitBreaker()
        self.last_fallback_reason: str | None = None

    # ---------- Helpers internos ----------

    def _reset_fallback(self):
        self.last_fallback_reason = None

    def _flag_fallback(self, reason: str | None):
        self.last_fallback_reason = reason

    def _tenant_plan(self, tenant: Any) -> str:
        if tenant:
            for attr in ("ia_plan", "plan"):
                plan_val = getattr(tenant, attr, None)
                if plan_val:
                    if isinstance(plan_val, PlanEnum):
                        return plan_val.value.lower()
                    plan_str = getattr(plan_val, "value", plan_val)
                    return str(plan_str).lower()
        return "base"

    def _tenant_toggle(self, tenant: Any) -> bool:
        if tenant is None:
            return True
        for attr in ("ia_enabled", "use_ia"):
            val = getattr(tenant, attr, None)
            if val is not None:
                return bool(val)
        return True

    def _tenant_ai_enabled(self, tenant_id: Optional[str]) -> bool:
        try:
            cfg = get_tenant_prompt_config(tenant_id) or {}
            ia_cfg = cfg.get("ia") or {}
            return bool(ia_cfg.get("enabled", True))
        except Exception:
            return True

    def _is_enabled_for(self, tenant: Any, tenant_id: Optional[str]) -> bool:
        if os.getenv("DISABLE_DB") == "1":
            return True
        plan_limits = get_plan_limits(self._tenant_plan(tenant))
        ia_enabled_in_plan = (plan_limits.get("features") or {}).get(
            "ia_enabled", True
        )
        billing_status = getattr(tenant, "billing_status", None)
        billing_ok = not billing_status or billing_status == BillingStatus.ACTIVE
        enabled = bool(
            self.base_enabled
            and self._tenant_toggle(tenant)
            and self._tenant_ai_enabled(tenant_id)
            and ia_enabled_in_plan
            and billing_ok
        )
        if not enabled:
            if not self.use_ai_env:
                self._flag_fallback("env_disabled")
            elif not self._tenant_toggle(tenant):
                self._flag_fallback("tenant_disabled")
            elif not ia_enabled_in_plan:
                self._flag_fallback("plan_without_ai")
            elif not billing_ok:
                self._flag_fallback("billing_inactive")
            else:
                self._flag_fallback("ai_disabled")
        return enabled

    def is_enabled_for(
        self, tenant: Any = None, tenant_id: Optional[str] = None
    ) -> bool:
        return self._is_enabled_for(tenant, tenant_id)

    def _select_model(self, plan: str) -> str:
        base_map = {"base": "gpt-4.1-mini", "pro": "gpt-4.1", "elite": "gpt-4.1"}
        return base_map.get(plan, "gpt-4.1-mini")

    def _use_extended_prompts(self, plan: str) -> bool:
        return plan == "elite"

    def _deterministic_text(self, purpose: str) -> str:
        if purpose == "summary":
            return "Resumen no disponible ahora mismo. Seguimos avanzando."
        if purpose in {"welcome", "closing"}:
            return "Seguimos en línea. Podemos continuar cuando quieras."
        return "Gracias por la información. Continua y te ayudo con tu proyecto."

    def _estimate_cost(self, model: str, prompt: str, extra_text: str = "", expected_output_tokens: int = 200) -> tuple[int, int, float]:
        tokens_in = max(int(len(prompt or "") / 4), 1)
        if extra_text:
            tokens_in += max(int(len(extra_text) / 4), 1)
        tokens_out = expected_output_tokens
        cost = IAUsageService.estimate_cost(model, tokens_in, tokens_out)
        return tokens_in, tokens_out, cost

    def _log_event(
        self,
        *,
        tenant_id: Optional[str],
        model: str,
        tokens_in: int,
        tokens_out: int,
        cost: float,
        fallback: Optional[str],
        latency_ms: float,
        outcome: Optional[str] = None,
    ):
        payload = {
            "tenant_id": tenant_id,
            "model": model,
            "tokens_in": tokens_in,
            "tokens_out": tokens_out,
            "cost_estimate": round(cost, 6),
            "fallback": fallback,
            "latency_ms": round(latency_ms, 2),
        }
        if fallback:
            logger.warning(payload)
        else:
            logger.info(payload)
        total_tokens = tokens_in + tokens_out
        bucket = "low" if total_tokens < 200 else "medium" if total_tokens < 800 else "high"
        outcome = outcome or ("success" if not fallback else "fallback")
        metrics.inc_counter(
            "ia_requests_total",
            {
                "model": model,
                "tenant_id": tenant_id or "unknown",
                "outcome": outcome,
                "tokens_bucket": bucket,
            },
        )
        if latency_ms:
            metrics.observe_histogram(
                "ia_latency_seconds",
                latency_ms / 1000.0,
                {"model": model, "tenant_id": tenant_id or "unknown"},
            )

    def _parse_tokens(self, completion: Any) -> tuple[int, int]:
        usage = getattr(completion, "usage", None) or getattr(
            getattr(completion, "model_dump", lambda: {})(), "usage", None
        )
        if isinstance(usage, dict):
            tokens_in = int(usage.get("prompt_tokens", 0) or 0)
            tokens_out = int(usage.get("completion_tokens", 0) or 0)
        else:
            tokens_in = int(getattr(usage, "prompt_tokens", 0) or 0)
            tokens_out = int(getattr(usage, "completion_tokens", 0) or 0)
        return tokens_in, tokens_out

    def _enforce_quota(self, db: Session | None, tenant: Any, model: str, estimated_cost: float = 0.0):
        if db is None or tenant is None:
            return
        try:
            IAUsageService.enforce_quota(
                db, tenant, estimated_cost_next_call=max(estimated_cost, 0.0)
            )
        except IAQuotaExceeded as exc:
            logger.warning({"event": "ia_quota_blocked", "tenant_id": getattr(tenant, "id", None), "error": str(exc)})
            raise

    def _record_usage(
        self,
        db: Session | None,
        tenant_id: Optional[str],
        model: str,
        tokens_in: int,
        tokens_out: int,
        cost: Optional[float],
        *,
        session_id: str | None = None,
        call_type: str | None = None,
    ):
        if db is None or tenant_id is None:
            return
        if cost is None:
            cost = IAUsageService.estimate_cost(model, tokens_in, tokens_out)
        try:
            IAUsageService.record_usage(
                db,
                str(tenant_id),
                model,
                tokens_in,
                tokens_out,
                cost,
                session_id=session_id,
                call_type=call_type,
            )
        except Exception as exc:
            logger.warning(
                {
                    "event": "ia_usage_record_failed",
                    "tenant_id": str(tenant_id),
                    "error": str(exc),
                }
            )

    def _guardrail_prompt(self) -> str:
        return (
            "Eres un asistente de proyectos de cocina. Sigue estas reglas estrictas: "
            "1) No inventes precios, condiciones legales ni datos del cliente. "
            "2) No solicites ni almacenes PII innecesaria; si el usuario comparte PII, redáctalo de forma segura. "
            "3) Respeta GDPR: no conserves información sensible fuera de los flujos definidos. "
            "4) Si el usuario pide algo fuera del contexto de cocinas o contra políticas, rechaza de forma educada. "
            "5) Prioriza respuestas breves, claras y seguras."
        )

    def _build_messages(self, prompt: str, user_message: Optional[str] = None) -> list[dict]:
        messages = [{"role": "system", "content": self._guardrail_prompt()}]
        if user_message:
            messages.append({"role": "user", "content": user_message})
        messages.append({"role": "system", "content": prompt})
        return messages

    def _audit_interaction(
        self,
        *,
        tenant_id: Optional[str],
        flow: str,
        user_input: Optional[str],
        ai_output: Optional[str],
        moderation_blocked: bool = False,
        moderation_adjusted: bool = False,
        circuit_breaker: bool = False,
        latency_ms: float | None = None,
    ):
        self.audit.record(
            tenant_id=tenant_id,
            flow=flow,
            user_input=user_input,
            ai_output=ai_output,
            moderation_blocked=moderation_blocked,
            moderation_adjusted=moderation_adjusted,
            circuit_breaker=circuit_breaker,
            latency_ms=latency_ms,
        )

    def _circuit_blocked(self, tenant_key: str) -> bool:
        state = self.circuit_breaker.is_open(tenant_key)
        return state.open

    def _safe_retry(self, model: str, prompt: str, original_output: str) -> Optional[str]:
        if not self.client:
            return None
        safe_prompt = (
            f"{prompt}\n\nSi existe contenido sensible o riesgoso, "
            "reescribe la respuesta de forma neutra y segura sin incluir datos personales."
        )
        completion = self.client.chat.completions.create(
            model=model,
            temperature=0,
            messages=self._build_messages(safe_prompt),
        )
        return completion.choices[0].message.content or original_output

    # ---------- API pública (extract / summary / reply) ----------

    async def extract_fields(
        self,
        text: str,
        purpose: str = "extraction",
        tenant: Any = None,
        tenant_id: Optional[str] = None,
        language: Optional[str] = None,
        db: Session | None = None,
        session_id: str | None = None,
    ) -> Dict[str, Any]:
        """
        Extrae campos estructurados según el propósito.
        purpose:
        - project_type
        - style
        - dimensions
        - budget
        - urgency
        - extraction (multi-campo genérico)
        """
        self._reset_fallback()
        plan = self._tenant_plan(tenant)
        model = self._select_model(plan)
        self.model = model
        tenant_identifier = tenant_id or getattr(tenant, "id", None)
        tenant_key = str(tenant_identifier or "unknown")

        if not self._is_enabled_for(tenant, tenant_identifier):
            fallback_reason = self.last_fallback_reason or "disabled"
            self._log_event(
                tenant_id=tenant_identifier,
                model=model,
                tokens_in=0,
                tokens_out=0,
                cost=0.0,
                fallback=fallback_reason,
                latency_ms=0.0,
            )
            self._flag_fallback(fallback_reason)
            return {}

        if not self.client:
            self._flag_fallback(self.last_fallback_reason or "missing_api_key")
            self._log_event(
                tenant_id=tenant_identifier,
                model=model,
                tokens_in=0,
                tokens_out=0,
                cost=0.0,
                fallback=self.last_fallback_reason,
                latency_ms=0.0,
            )
            return {}

        # Moderación previa
        moderation_input = self.moderation.check_input(text)
        if not moderation_input.allowed:
            self._flag_fallback("moderation_blocked")
            self._log_event(
                tenant_id=tenant_identifier,
                model=model,
                tokens_in=0,
                tokens_out=0,
                cost=0.0,
                fallback=moderation_input.reason or "moderation_blocked",
                latency_ms=0.0,
            )
            self._audit_interaction(
                tenant_id=tenant_identifier,
                flow="extract",
                user_input=moderation_input.masked_text,
                ai_output=None,
                moderation_blocked=True,
                circuit_breaker=False,
                latency_ms=0.0,
            )
            return {}

        if self._circuit_blocked(tenant_key):
            self._flag_fallback("circuit_open")
            self._log_event(
                tenant_id=tenant_identifier,
                model=model,
                tokens_in=0,
                tokens_out=0,
                cost=0.0,
                fallback="circuit_open",
                latency_ms=0.0,
            )
            self._audit_interaction(
                tenant_id=tenant_identifier,
                flow="extract",
                user_input=moderation_input.masked_text,
                ai_output=None,
                moderation_blocked=False,
                circuit_breaker=True,
                latency_ms=0.0,
            )
            return {}

        tenant_config = get_tenant_prompt_config(tenant_identifier) or {}
        if self._use_extended_prompts(plan):
            tenant_config = {**tenant_config, "prompt_level": "extended"}

        prompt = PromptRouter.get_extraction_prompt(
            purpose=purpose,
            user_text=text,
            language=language,
            tenant_config=tenant_config,
        )
        estimated_tokens_in, estimated_tokens_out, estimated_cost = self._estimate_cost(
            model, prompt, text or "", expected_output_tokens=160
        )
        if os.getenv("DISABLE_DB") == "1":
            budget_state = {"allowed": True}
        else:
            budget_state = self.budget.is_allowed(
                tenant_key, plan, projected_cost=estimated_cost
            )
        if not budget_state["allowed"]:
            self._flag_fallback("budget_exceeded")
            self._log_event(
                tenant_id=tenant_identifier,
                model=model,
                tokens_in=0,
                tokens_out=0,
                cost=0.0,
                fallback="budget_exceeded",
                latency_ms=0.0,
            )
            return {}

        if os.getenv("DISABLE_DB") != "1":
            try:
                self._enforce_quota(db, tenant, model, estimated_cost)
            except Exception as exc:
                fallback_reason = str(exc) or "quota_blocked"
                self._flag_fallback(fallback_reason)
                self._log_event(
                    tenant_id=tenant_identifier,
                    model=model,
                    tokens_in=0,
                    tokens_out=0,
                    cost=0.0,
                    fallback=fallback_reason,
                    latency_ms=0.0,
                    outcome="quota_blocked",
                )
                return {}

        content = ""
        start = time.perf_counter()
        try:
            completion = self.client.chat.completions.create(
                model=model,
                temperature=0,
                messages=self._build_messages(prompt),
            )
            content = completion.choices[0].message.content
            tokens_in, tokens_out = self._parse_tokens(completion)
            cost_data = self.budget.register(tenant_key, plan, tokens_in, tokens_out)
            latency_ms = (time.perf_counter() - start) * 1000
            self._log_event(
                tenant_id=tenant_identifier,
                model=model,
                tokens_in=tokens_in,
                tokens_out=tokens_out,
                cost=cost_data["cost"],
                fallback=None,
                latency_ms=latency_ms,
            )
            self._record_usage(
                db,
                tenant_identifier,
                model,
                tokens_in,
                tokens_out,
                cost_data["cost"],
                session_id=session_id,
                call_type="extraction",
            )
            output_moderation = self.moderation.check_output(content)
            moderated_output = False
            if not output_moderation.allowed:
                moderated_output = True
                safe_content = self._safe_retry(model, prompt, content) or ""
                if not safe_content:
                    safe_content = "{}"
                content = safe_content
            self._audit_interaction(
                tenant_id=tenant_identifier,
                flow="extract",
                user_input=moderation_input.masked_text,
                ai_output=mask_payload(content),
                moderation_blocked=False,
                moderation_adjusted=moderated_output,
                circuit_breaker=False,
                latency_ms=latency_ms,
            )
            self.circuit_breaker.record_success(tenant_key)
            data = json.loads(content)
            if not isinstance(data, dict):
                raise ValueError("JSON no es dict")
            return data
        except Exception as exc:
            latency_ms = (
                (time.perf_counter() - start) * 1000 if "start" in locals() else 0.0
            )
            self._log_event(
                tenant_id=tenant_identifier,
                model=model,
                tokens_in=0,
                tokens_out=0,
                cost=0.0,
                fallback=str(exc) or "fallback",
                latency_ms=latency_ms,
                outcome="error",
            )
            self.circuit_breaker.record_failure(tenant_key)
            if not self.last_fallback_reason:
                self._flag_fallback(str(exc) or "fallback")
            try:
                parsed = json.loads(content) if content else {}
                return parsed if isinstance(parsed, dict) else {}
            except Exception:
                return {}

    async def generate_summary(
        self,
        lead_data: Dict[str, Any],
        tenant: Any = None,
        tenant_id: Optional[str] = None,
        language: Optional[str] = None,
        db: Session | None = None,
        session_id: str | None = None,
    ) -> str:
        """
        Genera un resumen comercial corto para un lead.
        Usa prompt de tipo 'summary' vía PromptRouter.
        """
        self._reset_fallback()
        plan = self._tenant_plan(tenant)
        model = self._select_model(plan)
        self.model = model
        tenant_identifier = tenant_id or getattr(tenant, "id", None)
        tenant_key = str(tenant_identifier or "unknown")

        if not self._is_enabled_for(tenant, tenant_identifier):
            self._log_event(
                tenant_id=tenant_identifier,
                model=model,
                tokens_in=0,
                tokens_out=0,
                cost=0.0,
                fallback=self.last_fallback_reason or "disabled",
                latency_ms=0.0,
            )
            self._flag_fallback(self.last_fallback_reason or "disabled")
            return self._deterministic_text("summary")

        if not self.client:
            self._flag_fallback(self.last_fallback_reason or "missing_api_key")
            self._log_event(
                tenant_id=tenant_identifier,
                model=model,
                tokens_in=0,
                tokens_out=0,
                cost=0.0,
                fallback=self.last_fallback_reason,
                latency_ms=0.0,
            )
            return self._deterministic_text("summary")

        tenant_config = get_tenant_prompt_config(tenant_identifier) or {}
        if self._use_extended_prompts(plan):
            tenant_config = {**tenant_config, "prompt_level": "extended"}

        prompt = PromptRouter.get_generation_prompt(
            purpose="summary",
            payload=lead_data,
            language=language,
            tenant_config=tenant_config,
        )
        estimated_tokens_in, estimated_tokens_out, estimated_cost = self._estimate_cost(
            model, prompt, json.dumps(lead_data, ensure_ascii=False), expected_output_tokens=220
        )
        budget_state = self.budget.is_allowed(
            tenant_key, plan, projected_cost=estimated_cost
        )
        if not budget_state["allowed"]:
            self._flag_fallback("budget_exceeded")
            self._log_event(
                tenant_id=tenant_identifier,
                model=model,
                tokens_in=0,
                tokens_out=0,
                cost=0.0,
                fallback="budget_exceeded",
                latency_ms=0.0,
            )
            return self._deterministic_text("summary")

        try:
            self._enforce_quota(db, tenant, model, estimated_cost)
        except Exception as exc:
            fallback_reason = str(exc) or "quota_blocked"
            self._flag_fallback(fallback_reason)
            self._log_event(
                tenant_id=tenant_identifier,
                model=model,
                tokens_in=0,
                tokens_out=0,
                cost=0.0,
                fallback=fallback_reason,
                latency_ms=0.0,
                outcome="quota_blocked",
            )
            return self._deterministic_text("summary")

        tenant_safe_text = json.dumps(lead_data, ensure_ascii=False)
        moderation_input = self.moderation.check_input(tenant_safe_text)
        if not moderation_input.allowed:
            self._log_event(
                tenant_id=tenant_identifier,
                model=model,
                tokens_in=0,
                tokens_out=0,
                cost=0.0,
                fallback="moderation_blocked",
                latency_ms=0.0,
            )
            self._flag_fallback("moderation_blocked")
            self._audit_interaction(
                tenant_id=tenant_identifier,
                flow="summary",
                user_input=moderation_input.masked_text,
                ai_output=None,
                moderation_blocked=True,
                circuit_breaker=False,
                latency_ms=0.0,
            )
            return self._deterministic_text("summary")

        if self._circuit_blocked(tenant_key):
            self._flag_fallback("circuit_open")
            self._log_event(
                tenant_id=tenant_identifier,
                model=model,
                tokens_in=0,
                tokens_out=0,
                cost=0.0,
                fallback="circuit_open",
                latency_ms=0.0,
            )
            self._audit_interaction(
                tenant_id=tenant_identifier,
                flow="summary",
                user_input=moderation_input.masked_text,
                ai_output=None,
                moderation_blocked=False,
                circuit_breaker=True,
                latency_ms=0.0,
            )
            return self._deterministic_text("summary")

        start = time.perf_counter()
        try:
            completion = self.client.chat.completions.create(
                model=model,
                temperature=0.3,
                messages=self._build_messages(prompt),
            )
            tokens_in, tokens_out = self._parse_tokens(completion)
            cost_data = self.budget.register(tenant_key, plan, tokens_in, tokens_out)
            latency_ms = (time.perf_counter() - start) * 1000
            self._log_event(
                tenant_id=tenant_identifier,
                model=model,
                tokens_in=tokens_in,
                tokens_out=tokens_out,
                cost=cost_data["cost"],
                fallback=None,
                latency_ms=latency_ms,
            )
            self._record_usage(
                db,
                tenant_identifier,
                model,
                tokens_in,
                tokens_out,
                cost_data["cost"],
                session_id=session_id,
                call_type="summary",
            )
            output = completion.choices[0].message.content
            output_moderation = self.moderation.check_output(output)
            moderated_output = False
            if not output_moderation.allowed:
                moderated_output = True
                safe = self._safe_retry(model, prompt, output) or ""
                if safe:
                    output = safe
                else:
                    output = self._deterministic_text("summary")
            self._audit_interaction(
                tenant_id=tenant_identifier,
                flow="summary",
                user_input=moderation_input.masked_text,
                ai_output=mask_payload(output),
                moderation_blocked=False,
                moderation_adjusted=moderated_output,
                circuit_breaker=False,
                latency_ms=latency_ms,
            )
            self.circuit_breaker.record_success(tenant_key)
            return output
        except Exception as exc:
            latency_ms = (
                (time.perf_counter() - start) * 1000 if "start" in locals() else 0.0
            )
            self._log_event(
                tenant_id=tenant_identifier,
                model=model,
                tokens_in=0,
                tokens_out=0,
                cost=0.0,
                fallback=str(exc) or "fallback",
                latency_ms=latency_ms,
                outcome="error",
            )
            self.circuit_breaker.record_failure(tenant_key)
            if not self.last_fallback_reason:
                self._flag_fallback(str(exc) or "fallback")
            return self._deterministic_text("summary")

    async def generate_reply(
        self,
        message: str,
        context: Dict[str, Any],
        purpose: str = "reply_contextual",
        tenant: Any = None,
        tenant_id: Optional[str] = None,
        language: Optional[str] = None,
        db: Session | None = None,
        session_id: str | None = None,
    ) -> str:
        """
        Genera una respuesta conversacional:
        - reply_contextual (por defecto)
        - welcome
        - closing
        - microproposal
        """
        self._reset_fallback()
        plan = self._tenant_plan(tenant)
        model = self._select_model(plan)
        self.model = model
        tenant_identifier = tenant_id or getattr(tenant, "id", None)
        tenant_key = str(tenant_identifier or "unknown")

        if not self._is_enabled_for(tenant, tenant_identifier):
            self._log_event(
                tenant_id=tenant_identifier,
                model=model,
                tokens_in=0,
                tokens_out=0,
                cost=0.0,
                fallback=self.last_fallback_reason or "disabled",
                latency_ms=0.0,
            )
            self._flag_fallback(self.last_fallback_reason or "disabled")
            return self._deterministic_text(purpose)

        if not self.client:
            self._flag_fallback(self.last_fallback_reason or "missing_api_key")
            self._log_event(
                tenant_id=tenant_identifier,
                model=model,
                tokens_in=0,
                tokens_out=0,
                cost=0.0,
                fallback=self.last_fallback_reason,
                latency_ms=0.0,
            )
            return self._deterministic_text(purpose)

        payload = {
            "message": message,
            "context": context,
        }

        tenant_config = get_tenant_prompt_config(tenant_identifier) or {}
        if self._use_extended_prompts(plan):
            tenant_config = {**tenant_config, "prompt_level": "extended"}

        prompt = PromptRouter.get_generation_prompt(
            purpose=purpose,
            payload=payload,
            language=language,
            tenant_config=tenant_config,
        )
        estimated_tokens_in, estimated_tokens_out, estimated_cost = self._estimate_cost(
            model, prompt, message or "", expected_output_tokens=240
        )
        budget_state = self.budget.is_allowed(
            tenant_key, plan, projected_cost=estimated_cost
        )
        if not budget_state["allowed"]:
            self._flag_fallback("budget_exceeded")
            self._log_event(
                tenant_id=tenant_identifier,
                model=model,
                tokens_in=0,
                tokens_out=0,
                cost=0.0,
                fallback="budget_exceeded",
                latency_ms=0.0,
            )
            return self._deterministic_text(purpose)

        try:
            self._enforce_quota(db, tenant, model, estimated_cost)
        except Exception as exc:
            fallback_reason = str(exc) or "quota_blocked"
            self._flag_fallback(fallback_reason)
            self._log_event(
                tenant_id=tenant_identifier,
                model=model,
                tokens_in=0,
                tokens_out=0,
                cost=0.0,
                fallback=fallback_reason,
                latency_ms=0.0,
                outcome="quota_blocked",
            )
            return self._deterministic_text(purpose)

        moderation_input = self.moderation.check_input(message)
        if not moderation_input.allowed:
            self._log_event(
                tenant_id=tenant_identifier,
                model=model,
                tokens_in=0,
                tokens_out=0,
                cost=0.0,
                fallback="moderation_blocked",
                latency_ms=0.0,
            )
            self._flag_fallback("moderation_blocked")
            self._audit_interaction(
                tenant_id=tenant_identifier,
                flow="reply",
                user_input=moderation_input.masked_text,
                ai_output=None,
                moderation_blocked=True,
                circuit_breaker=False,
                latency_ms=0.0,
            )
            return self._deterministic_text(purpose)

        if self._circuit_blocked(tenant_key):
            self._flag_fallback("circuit_open")
            self._log_event(
                tenant_id=tenant_identifier,
                model=model,
                tokens_in=0,
                tokens_out=0,
                cost=0.0,
                fallback="circuit_open",
                latency_ms=0.0,
            )
            self._audit_interaction(
                tenant_id=tenant_identifier,
                flow="reply",
                user_input=moderation_input.masked_text,
                ai_output=None,
                moderation_blocked=False,
                circuit_breaker=True,
                latency_ms=0.0,
            )
            return self._deterministic_text(purpose)

        start = time.perf_counter()
        try:
            completion = self.client.chat.completions.create(
                model=model,
                temperature=0.4,
                messages=self._build_messages(prompt, message),
            )
            tokens_in, tokens_out = self._parse_tokens(completion)
            cost_data = self.budget.register(tenant_key, plan, tokens_in, tokens_out)
            latency_ms = (time.perf_counter() - start) * 1000
            self._log_event(
                tenant_id=tenant_identifier,
                model=model,
                tokens_in=tokens_in,
                tokens_out=tokens_out,
                cost=cost_data["cost"],
                fallback=None,
                latency_ms=latency_ms,
            )
            self._record_usage(
                db,
                tenant_identifier,
                model,
                tokens_in,
                tokens_out,
                cost_data["cost"],
                session_id=session_id,
                call_type="generation",
            )
            output = completion.choices[0].message.content
            output_moderation = self.moderation.check_output(output)
            moderated_output = False
            if not output_moderation.allowed:
                moderated_output = True
                safe = self._safe_retry(model, prompt, output)
                if safe:
                    output = safe
                else:
                    output = self._deterministic_text(purpose)
            self._audit_interaction(
                tenant_id=tenant_identifier,
                flow="reply",
                user_input=moderation_input.masked_text,
                ai_output=mask_payload(output),
                moderation_blocked=False,
                moderation_adjusted=moderated_output,
                circuit_breaker=False,
                latency_ms=latency_ms,
            )
            self.circuit_breaker.record_success(tenant_key)
            return output
        except Exception as exc:
            latency_ms = (
                (time.perf_counter() - start) * 1000 if "start" in locals() else 0.0
            )
            self._log_event(
                tenant_id=tenant_identifier,
                model=model,
                tokens_in=0,
                tokens_out=0,
                cost=0.0,
                fallback=str(exc) or "fallback",
                latency_ms=latency_ms,
                outcome="error",
            )
            self.circuit_breaker.record_failure(tenant_key)
            if not self.last_fallback_reason:
                self._flag_fallback(str(exc) or "fallback")
            return self._deterministic_text(purpose)

    def rewrite_for_pdf(
        self,
        text: str,
        tone: str,
        *,
        tenant: Any = None,
        tenant_id: Optional[str] = None,
    ) -> str:
        plan = self._tenant_plan(tenant)
        if plan not in {"pro", "elite"} or not self._is_enabled_for(tenant, tenant_id):
            return text
        model = self._select_model(plan)
        try:
            prompt = (
                f"Reescribe este texto en tono {tone} y conciso para un PDF: {text}"
            )
            completion = self.client.chat.completions.create(
                model=model,
                temperature=0.3,
                messages=[{"role": "user", "content": prompt}],
            )
            return completion.choices[0].message.content or text
        except Exception:
            return text
