from __future__ import annotations

import json
import os
from datetime import date, datetime, timezone
from typing import Any

from loguru import logger
from openai import APIConnectionError, APIStatusError, AuthenticationError, OpenAI, RateLimitError
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.flow_generations import FlowGeneration
from app.models.flows import Flow as FlowVersioned
from app.models.tenants import Tenant, PlanEnum
from app.services.ia_usage_service import IAQuotaExceeded, IAUsageService
from app.services.knowledge_base import build_knowledge_prompt, build_semantic_knowledge_prompt, tenant_knowledge_file_ids
from app.services.verticals import tenant_vertical_scopes, vertical_flow_base, vertical_prompt, vertical_prompt_extension, vertical_scope_prompts


FLOW_GEN_LIMITS = {
    "base": 1,
    "pro": 3,
    "elite": 5,
}

DEFAULT_MODEL = os.getenv("FLOW_GENERATION_MODEL") or os.getenv("AI_MODEL") or "gpt-4.1-mini"

ALLOWED_BLOCK_TYPES_V1 = {
    "message",
    "input",
    "buttons",
    "options",
    "calendar",
    "appointment",
    "attachment",
    "end",
}


def _month_start(today: date | None = None) -> date:
    today = today or date.today()
    return date(today.year, today.month, 1)


def generation_limit_for_plan(plan: Any) -> int:
    if isinstance(plan, PlanEnum):
        p = plan.value.lower()
    else:
        p = str(getattr(plan, "value", plan) or "base").lower()
    return int(FLOW_GEN_LIMITS.get(p, FLOW_GEN_LIMITS["base"]))


def monthly_generation_count(db: Session, tenant_id: str) -> int:
    ms = _month_start()
    return int(
        (db.query(func.count(FlowGeneration.id)).filter(FlowGeneration.tenant_id == tenant_id, FlowGeneration.created_at >= ms).scalar() or 0)
    )


def enforce_generation_quota(db: Session, tenant: Tenant, *, allow_overage: bool) -> dict[str, Any]:
    limit = generation_limit_for_plan(getattr(tenant, "plan", None))
    used = monthly_generation_count(db, str(tenant.id))
    remaining = max(limit - used, 0)
    if remaining <= 0 and not allow_overage:
        raise ValueError("flow_generation_quota_exceeded")
    return {"limit": limit, "used": used, "remaining": remaining, "overage": bool(remaining <= 0 and allow_overage)}


def _next_flow_version(db: Session, tenant_id: str) -> int:
    latest = (
        db.query(FlowVersioned)
        .filter(FlowVersioned.tenant_id == tenant_id)
        .order_by(FlowVersioned.version.desc())
        .first()
    )
    return (latest.version + 1) if latest else 1


def _sanitize_flow_schema(flow: Any, *, languages: list[str]) -> dict[str, Any]:
    if not isinstance(flow, dict):
        raise ValueError("flow_not_a_dict")
    blocks = flow.get("blocks")
    if not isinstance(blocks, dict) or not blocks:
        raise ValueError("missing_blocks")

    sanitized_blocks: dict[str, dict[str, Any]] = {}
    for bid, raw in blocks.items():
        if not bid or not isinstance(raw, dict):
            continue
        btype = str(raw.get("type") or "").strip().lower()
        if btype not in ALLOWED_BLOCK_TYPES_V1:
            continue
        if btype in {"condition", "internal", "ai_generate", "ai_extract"}:
            continue

        block: dict[str, Any] = {"id": str(raw.get("id") or bid), "type": btype}
        # allow only known keys
        for k in ("next", "next_map", "branches", "validation", "save_as", "save_to", "options", "text"):
            if k in raw:
                block[k] = raw.get(k)

        if btype == "input":
            save_key = block.get("save_as") or block.get("save_to")
            if not save_key:
                raise ValueError(f"input_missing_save_key:{bid}")
        if btype in {"buttons", "options"}:
            opts = block.get("options")
            if not isinstance(opts, list) or not opts:
                raise ValueError(f"options_missing:{bid}")
            norm_opts: list[dict[str, Any]] = []
            for o in opts:
                if isinstance(o, dict):
                    oid = o.get("id") or o.get("value")
                    if oid is None:
                        continue
                    label = o.get("label") or o.get("text") or oid
                    if isinstance(label, dict):
                        label = {k: v for k, v in label.items() if k in languages and isinstance(v, str)}
                    elif isinstance(label, str):
                        label = {languages[0]: label}
                    norm_opts.append({"id": str(oid), "label": label})
                elif o is not None:
                    # string option → normalize
                    norm_opts.append({"id": str(o), "label": {languages[0]: str(o)}})
            if not norm_opts:
                raise ValueError(f"options_invalid:{bid}")
            block["options"] = norm_opts
        if btype in {"calendar", "appointment", "attachment"}:
            save_key = block.get("save_as") or block.get("save_to")
            if not save_key:
                raise ValueError(f"{btype}_missing_save_key:{bid}")

        # text normalization
        txt = block.get("text")
        if isinstance(txt, str):
            block["text"] = {languages[0]: txt}
        elif isinstance(txt, dict):
            norm = {}
            for lang in languages:
                if isinstance(txt.get(lang), str):
                    norm[lang] = txt.get(lang)
            # allow fallback if only one language provided by IA
            if not norm and txt:
                any_val = next(iter(txt.values()), "")
                if isinstance(any_val, str) and any_val:
                    norm[languages[0]] = any_val
            block["text"] = norm

        sanitized_blocks[str(bid)] = block

    if not sanitized_blocks:
        raise ValueError("no_allowed_blocks")

    start_block = flow.get("start_block")
    if not isinstance(start_block, str) or start_block not in sanitized_blocks:
        start_block = next(iter(sanitized_blocks.keys()))

    out: dict[str, Any] = {
        "version": str(flow.get("version") or "custom_v2"),
        "plan": str(flow.get("plan") or "custom").lower(),
        "languages": languages,
        "start_block": str(start_block),
        "config": flow.get("config") if isinstance(flow.get("config"), dict) else {},
        "blocks": sanitized_blocks,
    }
    return out


def _build_flow_generation_system_prompt(*, languages: list[str]) -> str:
    langs = ", ".join(languages)
    return (
        "Devuelve SOLO un objeto JSON válido (sin markdown, sin explicaciones).\n"
        "Objetivo: generar un flow JSON para un asistente multi-tenant.\n\n"
        "REGLAS DE SEGURIDAD (v1):\n"
        "- Tipos permitidos: message, input, buttons, options, calendar, appointment, attachment, end.\n"
        "- PROHIBIDO: condition, internal, ai_generate, ai_extract.\n"
        "- No uses eval, no incluyas código, no incluyas acciones.\n"
        "- `input` debe incluir `save_to` o `save_as`.\n"
        "- `buttons/options` debe incluir `options` con `id` estable y `label` multi-idioma.\n"
        "- `calendar/appointment/attachment` debe incluir `save_to` o `save_as`.\n"
        f"- Idiomas obligatorios en `text` y labels: {langs}.\n\n"
        "ESQUEMA MÍNIMO:\n"
        "{\n"
        '  "version": "string",\n'
        '  "plan": "custom",\n'
        '  "languages": ["es","pt","en","ca"],\n'
        '  "start_block": "welcome",\n'
        '  "config": {},\n'
        '  "blocks": {\n'
        '     "welcome": {"id":"welcome","type":"message","text":{"es":"...","pt":"...","en":"...","ca":"..."},"next":"..."},\n'
        '     "...": {}\n'
        "  }\n"
        "}\n"
    )


def _build_text_patch_system_prompt(*, languages: list[str]) -> str:
    langs = ", ".join(languages)
    return (
        "Devuelve SOLO un objeto JSON válido (sin markdown, sin explicaciones).\n"
        "Objetivo: generar un PATCH de textos/labels multi-idioma para un flow existente.\n\n"
        "REGLAS DE SEGURIDAD:\n"
        "- NO modifiques estructura (no cambies type/next/next_map/branches/config/start_block).\n"
        "- SOLO puedes proponer textos para blocks y labels para opciones YA existentes.\n"
        f"- Idiomas obligatorios: {langs}.\n\n"
        "FORMATO DE SALIDA:\n"
        "{\n"
        '  "blocks": {\n'
        '    "block_id": {\n'
        '      "text": {"es":"...","pt":"...","en":"...","ca":"..."},\n'
        '      "options": {\n'
        '        "option_id": {"es":"...","pt":"...","en":"...","ca":"..."}\n'
        "      }\n"
        "    }\n"
        "  }\n"
        "}\n"
    )


def _flow_block_summaries(flow: dict[str, Any]) -> list[dict[str, Any]]:
    blocks = flow.get("blocks") if isinstance(flow.get("blocks"), dict) else {}
    out: list[dict[str, Any]] = []
    for bid, b in blocks.items():
        if not isinstance(b, dict):
            continue
        item: dict[str, Any] = {"id": str(bid), "type": b.get("type")}
        if "text" in b:
            item["text"] = b.get("text")
        if isinstance(b.get("options"), list):
            item["options"] = [
                {"id": (o.get("id") or o.get("value")), "label": o.get("label")}
                for o in b.get("options")
                if isinstance(o, dict)
            ]
        out.append(item)
    return out


def _apply_text_patch_to_flow(flow: dict[str, Any], patch: dict[str, Any], *, languages: list[str]) -> dict[str, Any]:
    blocks = flow.get("blocks")
    if not isinstance(blocks, dict) or not blocks:
        raise ValueError("missing_blocks")
    pblocks = patch.get("blocks") if isinstance(patch.get("blocks"), dict) else None
    if not isinstance(pblocks, dict) or not pblocks:
        raise ValueError("patch_missing_blocks")

    for bid, pdata in pblocks.items():
        if not bid or not isinstance(pdata, dict):
            continue
        target = blocks.get(bid)
        if not isinstance(target, dict):
            continue

        txt = pdata.get("text")
        if isinstance(txt, dict):
            norm_txt: dict[str, str] = {}
            for lang in languages:
                v = txt.get(lang)
                if isinstance(v, str):
                    norm_txt[lang] = v
            if norm_txt:
                target["text"] = norm_txt

        popts = pdata.get("options")
        if isinstance(popts, dict):
            existing_opts = target.get("options") if isinstance(target.get("options"), list) else []
            if not existing_opts:
                continue
            by_id: dict[str, dict[str, Any]] = {}
            for o in existing_opts:
                if not isinstance(o, dict):
                    continue
                oid = o.get("id") or o.get("value")
                if oid is None:
                    continue
                by_id[str(oid)] = o
            for oid, lbl in popts.items():
                if oid not in by_id or not isinstance(lbl, dict):
                    continue
                norm_lbl: dict[str, str] = {}
                for lang in languages:
                    v = lbl.get(lang)
                    if isinstance(v, str):
                        norm_lbl[lang] = v
                if norm_lbl:
                    by_id[oid]["label"] = norm_lbl

    return flow


def compose_flow_generation_system_message(
    *,
    vertical_key: str | None,
    scopes: object,
    languages: list[str],
) -> str:
    v_prompt = vertical_prompt(vertical_key) or ""
    v_ext = vertical_prompt_extension(vertical_key) or ""
    scope_prompts = vertical_scope_prompts(vertical_key, scopes)
    system_msg = _build_flow_generation_system_prompt(languages=languages)
    prompt_parts = [p for p in [v_prompt, *scope_prompts, v_ext, system_msg] if isinstance(p, str) and p.strip()]
    return "\n\n".join([p.strip() for p in prompt_parts]).strip()


def compose_flow_text_patch_system_message(
    *,
    vertical_key: str | None,
    scopes: object,
    languages: list[str],
) -> str:
    v_prompt = vertical_prompt(vertical_key) or ""
    v_ext = vertical_prompt_extension(vertical_key) or ""
    scope_prompts = vertical_scope_prompts(vertical_key, scopes)
    system_msg = _build_text_patch_system_prompt(languages=languages)
    prompt_parts = [p for p in [v_prompt, *scope_prompts, v_ext, system_msg] if isinstance(p, str) and p.strip()]
    return "\n\n".join([p.strip() for p in prompt_parts]).strip()


def generate_flow_patch_sample_for_vertical(
    *,
    vertical_key: str | None,
    scopes: object,
    languages: list[str],
    business_knowledge: str | None = None,
    tenant_name: str | None = None,
    model: str | None = None,
    temperature: float = 0.3,
) -> dict[str, Any]:
    """
    Admin-only: genera un PATCH de textos/labels y lo aplica a un flow base (no persiste en DB).
    """
    settings = get_settings()
    if not settings.openai_api_key:
        raise ValueError("missing_openai_api_key")

    langs = [str(x).lower().strip() for x in (languages or ["es", "pt", "en", "ca"]) if x]
    langs = [x for x in langs if x in {"es", "pt", "en", "ca"}] or ["es"]

    base_flow = vertical_flow_base(vertical_key, scopes)
    if not isinstance(base_flow, dict) or not isinstance(base_flow.get("blocks"), dict) or not base_flow.get("blocks"):
        raise ValueError("missing_flow_base_for_scope")

    system_msg = compose_flow_text_patch_system_message(vertical_key=vertical_key, scopes=scopes, languages=langs)
    user_prompt = {
        "vertical_key": vertical_key,
        "scopes": scopes if isinstance(scopes, list) else [],
        "tenant_name": tenant_name,
        "languages": langs,
        "business_knowledge": (business_knowledge or "").strip(),
        "flow_structure": {
            "start_block": base_flow.get("start_block"),
            "blocks": _flow_block_summaries(base_flow),
        },
    }

    client = OpenAI(api_key=settings.openai_api_key)
    resp = client.chat.completions.create(
        model=(model or DEFAULT_MODEL),
        temperature=float(temperature),
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": json.dumps(user_prompt, ensure_ascii=False)},
        ],
    )
    content = (resp.choices[0].message.content or "").strip()
    try:
        raw = json.loads(content) if content else {}
    except Exception:
        raw = {}
    if not isinstance(raw, dict):
        raw = {}
    patched = json.loads(json.dumps(base_flow))
    patched = _apply_text_patch_to_flow(patched, raw, languages=langs)
    patched["languages"] = langs
    return {"system_message": system_msg, "user_prompt": user_prompt, "patch": raw, "flow": patched}

def generate_flow_sample_for_vertical(
    *,
    vertical_key: str | None,
    scopes: object,
    languages: list[str],
    business_knowledge: str | None = None,
    tenant_name: str | None = None,
    model: str | None = None,
    temperature: float = 0.3,
) -> dict[str, Any]:
    """
    Genera un flow de ejemplo (NO persiste en DB, NO consume cuota de tenant).
    Uso: testing/preview en panel ADMIN.
    """
    settings = get_settings()
    if not settings.openai_api_key:
        raise ValueError("missing_openai_api_key")

    langs = [str(x).lower().strip() for x in (languages or ["es", "pt", "en", "ca"]) if x]
    langs = [x for x in langs if x in {"es", "pt", "en", "ca"}] or ["es"]

    def _normalize_scopes(raw: object) -> list[str]:
        if not raw:
            return []
        if isinstance(raw, str):
            items = [raw]
        elif isinstance(raw, list):
            items = [str(s) for s in raw if s]
        elif isinstance(raw, tuple):
            items = [str(s) for s in raw if s]
        else:
            return []
        out: list[str] = []
        seen: set[str] = set()
        for s in items:
            key = str(s).strip()
            if not key or key in seen:
                continue
            seen.add(key)
            out.append(key)
        return out

    system_msg = compose_flow_generation_system_message(vertical_key=vertical_key, scopes=scopes, languages=langs)
    user_prompt = {
        "vertical_key": vertical_key,
        "scopes": _normalize_scopes(scopes),
        "tenant_name": tenant_name,
        "languages": langs,
        "business_knowledge": (business_knowledge or "").strip(),
        "notes": (
            "Genera un flujo de ejemplo para validar prompts. "
            "No inventes datos; si falta información, haz preguntas genéricas."
        ),
    }

    client = OpenAI(api_key=settings.openai_api_key)
    resp = client.chat.completions.create(
        model=(model or DEFAULT_MODEL),
        temperature=float(temperature),
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": json.dumps(user_prompt, ensure_ascii=False)},
        ],
    )
    content = (resp.choices[0].message.content or "").strip()
    try:
        raw = json.loads(content) if content else {}
    except Exception:
        raw = {}
    sanitized = _sanitize_flow_schema(raw, languages=langs)
    return {"system_message": system_msg, "user_prompt": user_prompt, "flow": sanitized, "raw": raw}


def generate_flow_draft(
    *,
    db: Session,
    tenant: Tenant,
    allow_overage: bool = False,
    languages: list[str] | None = None,
    user_id: str | None = None,
) -> dict[str, Any]:
    settings = get_settings()
    if not settings.openai_api_key:
        raise ValueError("missing_openai_api_key")

    langs = [str(x).lower().strip() for x in (languages or ["es", "pt", "en", "ca"]) if x]
    langs = [x for x in langs if x in {"es", "pt", "en", "ca"}] or ["es"]

    quota_state = enforce_generation_quota(db, tenant, allow_overage=allow_overage)

    # record request (counts against quota once created)
    gen = FlowGeneration(
        tenant_id=tenant.id,
        status="running",
        source="tenant_panel",
        requested_by_user_id=user_id,
        scopes=tenant_vertical_scopes(tenant),
        languages=langs,
        selected_file_ids=tenant_knowledge_file_ids(db, str(tenant.id)),
        model=DEFAULT_MODEL,
        meta={"quota": quota_state},
    )
    db.add(gen)
    db.commit()
    db.refresh(gen)

    v_key = getattr(tenant, "vertical_key", None)
    scopes = tenant_vertical_scopes(tenant)

    # Base flow: estructura fija por scope principal.
    # Fallback compat (tenants antiguos): si no hay vertical/scope base, usar el último published/draft.
    base_flow = vertical_flow_base(v_key, scopes)
    if not isinstance(base_flow, dict) or not isinstance(base_flow.get("blocks"), dict) or not base_flow.get("blocks"):
        try:
            fallback_row = (
                db.query(FlowVersioned)
                .filter(FlowVersioned.tenant_id == tenant.id)
                .order_by(
                    (FlowVersioned.estado == "published").desc(),
                    FlowVersioned.published_at.desc().nullslast(),
                    FlowVersioned.version.desc(),
                )
                .first()
            )
            if fallback_row and isinstance(fallback_row.schema_json, dict) and isinstance(fallback_row.schema_json.get("blocks"), dict):
                base_flow = fallback_row.schema_json
        except Exception:
            base_flow = None
    if not isinstance(base_flow, dict) or not isinstance(base_flow.get("blocks"), dict) or not base_flow.get("blocks"):
        gen.status = "failed"
        gen.error = "missing_flow_base_for_scope"
        db.add(gen)
        db.commit()
        raise ValueError("missing_flow_base_for_scope")

    v_prompt = vertical_prompt(v_key) or ""
    v_ext = vertical_prompt_extension(v_key) or ""
    scope_prompts = vertical_scope_prompts(v_key, scopes)

    # KB context (semantic first, fallback to raw extracted prompt)
    kb = ""
    try:
        kb = build_semantic_knowledge_prompt(
            db,
            str(tenant.id),
            query="servicios, precios, horarios, materiales, políticas y condiciones del negocio",
        )
    except Exception:
        kb = ""
    if not kb:
        kb = build_knowledge_prompt(db, str(tenant.id))

    user_prompt = {
        "tenant_name": getattr(tenant, "name", None),
        "vertical_key": v_key,
        "scopes": scopes,
        "languages": langs,
        "business_knowledge": kb,
        "flow_structure": {
            "start_block": base_flow.get("start_block"),
            "blocks": _flow_block_summaries(base_flow),
        },
        "notes": (
            "Devuelve SOLO el patch de textos/labels. "
            "No inventes datos; usa solo lo que aparece en business_knowledge."
        ),
    }

    system_msg = _build_text_patch_system_prompt(languages=langs)
    prompt_parts = [p for p in [v_prompt, *scope_prompts, v_ext, system_msg] if isinstance(p, str) and p.strip()]
    system_msg = "\n\n".join([p.strip() for p in prompt_parts]).strip()

    client = OpenAI(api_key=settings.openai_api_key)
    # Enforce IA budget/quota antes de la llamada (estimación conservadora).
    try:
        approx_in = max(1, int((len(system_msg) + len(json.dumps(user_prompt, ensure_ascii=False))) / 4))
        approx_out = 1400
        approx_cost = IAUsageService.estimate_cost(DEFAULT_MODEL, approx_in, approx_out)
        IAUsageService.enforce_quota(db, tenant, estimated_cost_next_call=max(approx_cost, 0.0))
    except IAQuotaExceeded as exc:
        gen.status = "failed"
        gen.error = str(exc)
        db.add(gen)
        db.commit()
        raise

    try:
        resp = client.chat.completions.create(
            model=DEFAULT_MODEL,
            temperature=0.3,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": json.dumps(user_prompt, ensure_ascii=False)},
            ],
        )
        content = (resp.choices[0].message.content or "").strip()
        usage = getattr(resp, "usage", None)
        tokens_in = int(getattr(usage, "prompt_tokens", 0) or 0) if usage else 0
        tokens_out = int(getattr(usage, "completion_tokens", 0) or 0) if usage else 0
        cost = IAUsageService.estimate_cost(DEFAULT_MODEL, tokens_in, tokens_out)
        IAUsageService.record_usage(
            db,
            str(tenant.id),
            DEFAULT_MODEL,
            tokens_in,
            tokens_out,
            cost,
            session_id=None,
            call_type="flow_generation",
        )
    except AuthenticationError as exc:
        gen.status = "failed"
        gen.error = "invalid_openai_api_key"
        db.add(gen)
        db.commit()
        raise ValueError("invalid_openai_api_key") from exc
    except RateLimitError as exc:
        gen.status = "failed"
        gen.error = "ia_rate_limited"
        db.add(gen)
        db.commit()
        raise ValueError("ia_rate_limited") from exc
    except APIConnectionError as exc:
        gen.status = "failed"
        gen.error = "ia_provider_unavailable"
        db.add(gen)
        db.commit()
        raise ValueError("ia_provider_unavailable") from exc
    except APIStatusError as exc:
        # 5xx del provider → degradado temporal
        gen.status = "failed"
        gen.error = f"ia_provider_error:{getattr(exc, 'status_code', None) or 'unknown'}"
        db.add(gen)
        db.commit()
        raise ValueError("ia_provider_unavailable") from exc
    except IAQuotaExceeded as exc:
        gen.status = "failed"
        gen.error = str(exc)
        db.add(gen)
        db.commit()
        raise
    except Exception as exc:
        gen.status = "failed"
        gen.error = str(exc)
        db.add(gen)
        db.commit()
        raise

    try:
        raw = json.loads(content) if content else {}
    except Exception:
        raw = {}

    try:
        if not isinstance(raw, dict):
            raise ValueError("invalid_patch")
        # Aplicar patch sobre base (estructura intacta)
        patched = json.loads(json.dumps(base_flow))  # deep copy
        patched = _apply_text_patch_to_flow(patched, raw, languages=langs)
        patched["languages"] = langs
        sanitized = patched
    except Exception as exc:
        gen.status = "failed"
        gen.error = f"invalid_patch:{str(exc)}"
        db.add(gen)
        db.commit()
        raise

    # Create draft flow version
    new_flow = FlowVersioned(
        tenant_id=tenant.id,
        vertical_key=str(getattr(tenant, "vertical_key", "") or "") or None,
        scope_key=(scopes[0] if scopes else None),
        version=_next_flow_version(db, str(tenant.id)),
        schema_json=sanitized,
        estado="draft",
        published_at=None,
        owner_type="TENANT",
        owner_id=tenant.id,
        flow_kind="base",
    )
    db.add(new_flow)
    db.commit()
    db.refresh(new_flow)

    gen.status = "succeeded"
    gen.tokens_in = tokens_in
    gen.tokens_out = tokens_out
    gen.cost_eur = cost
    gen.result_flow_id = new_flow.id
    gen.meta = {**(gen.meta or {}), "scopes": scopes, "languages": langs}
    db.add(gen)

    # Ensure tenant is v2
    branding = getattr(tenant, "branding", {}) or {}
    branding["flow_system"] = "v2"
    tenant.branding = branding
    db.add(tenant)
    db.commit()

    logger.info({"event": "flow_generation_succeeded", "tenant_id": str(tenant.id), "flow_id": str(new_flow.id)})
    return {
        "tenant_id": str(tenant.id),
        "flow_id": str(new_flow.id),
        "version": new_flow.version,
        "estado": new_flow.estado,
        "generation_id": str(gen.id),
        "quota": quota_state,
    }
