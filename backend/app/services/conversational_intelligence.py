from __future__ import annotations

import os
import re
from typing import Any


def _env_int(*keys: str, default: int) -> int:
    for k in keys:
        v = os.getenv(k)
        if v is None or str(v).strip() == "":
            continue
        try:
            return int(float(str(v).strip()))
        except Exception:
            continue
    return int(default)


DEFAULT_ENRICHED_SCORE_THRESHOLD = _env_int(
    "CI_ENRICHED_SCORE_THRESHOLD",
    "KITCHENS_ENRICHED_SCORE_THRESHOLD",
    default=70,
)
DEFAULT_FRICTION_SECONDS = _env_int(
    "CI_ENRICHED_FRICTION_SECONDS",
    "KITCHENS_ENRICHED_FRICTION_SECONDS",
    default=12,
)


_RE_MULTISPACE = re.compile(r"\s+")


def _norm(text: str | None) -> str:
    if not text:
        return ""
    return _RE_MULTISPACE.sub(" ", str(text)).strip().lower()


def is_doubt_text(text: str | None) -> bool:
    t = _norm(text)
    if not t:
        return False
    needles = [
        "no se",
        "no sé",
        "depende",
        "más o menos",
        "mas o menos",
        "no estoy seguro",
        "no estoy segura",
        "no lo tengo claro",
        "no lo sé",
        "quizas",
        "quizá",
        "tal vez",
        "aun no",
        "aún no",
    ]
    return any(n in t for n in needles)


def is_question_text(text: str | None) -> bool:
    t = _norm(text)
    if not t:
        return False
    if "?" in t or t.startswith("¿"):
        return True
    prefixes = (
        "como ",
        "cómo ",
        "que ",
        "qué ",
        "cuanto ",
        "cuánto ",
        "cuando ",
        "cuándo ",
        "donde ",
        "dónde ",
        "podrias ",
        "podrías ",
        "me puedes ",
        "se puede ",
        "es posible ",
    )
    return t.startswith(prefixes)


def pick_text_field(block: dict[str, Any], field: str, lang: str, default_lang: str) -> str | None:
    if not isinstance(block, dict):
        return None
    val = block.get(field)
    if isinstance(val, dict):
        if val.get(lang):
            return str(val.get(lang))
        if val.get(default_lang):
            return str(val.get(default_lang))
        for k in ("es", "en", "pt", "ca"):
            if val.get(k):
                return str(val.get(k))
        try:
            return str(next(iter(val.values())))
        except Exception:
            return None
    if isinstance(val, str):
        return val
    return None


def _pick_text_variant(
    block: dict[str, Any],
    *,
    lang: str,
    default_lang: str,
    prelim_score: int,
    strong_threshold: int,
) -> str | None:
    variants = block.get("text_variants")
    if not isinstance(variants, list) or not variants:
        return None
    idx = 0 if int(prelim_score or 0) >= int(strong_threshold) else 1
    if idx >= len(variants):
        idx = 0
    cand = variants[idx]
    if isinstance(cand, dict):
        return pick_text_field({"v": cand}, "v", lang, default_lang)
    if isinstance(cand, str):
        # Variantes normalmente redactadas en ES; si no es ES, mejor no forzar.
        if lang != "es" and default_lang != "es":
            return None
        return cand
    return None


def should_use_enriched_copy(
    *,
    enabled: bool,
    use_ai: bool,
    ci_state: dict[str, Any] | None,
    raw_user_text: str | None,
    response_delay_s: float | None,
    prelim_score: int | None,
    score_threshold: int = DEFAULT_ENRICHED_SCORE_THRESHOLD,
    friction_seconds: int = DEFAULT_FRICTION_SECONDS,
) -> bool:
    if not enabled:
        return False
    if not use_ai:
        return False
    ci = ci_state or {}
    if bool(ci.get("free_text_seen")):
        return True
    if is_doubt_text(raw_user_text):
        return True
    if response_delay_s is not None and float(response_delay_s) >= float(friction_seconds):
        return True
    if prelim_score is not None and int(prelim_score) >= int(score_threshold):
        return True
    return False


def resolve_block_text(
    block: dict[str, Any],
    *,
    lang: str,
    default_lang: str,
    enabled: bool,
    use_ai: bool,
    ci_state: dict[str, Any] | None,
    raw_user_text: str | None,
    response_delay_s: float | None,
    prelim_score: int | None,
    score_threshold: int = DEFAULT_ENRICHED_SCORE_THRESHOLD,
    friction_seconds: int = DEFAULT_FRICTION_SECONDS,
) -> str:
    base = pick_text_field(block, "text", lang, default_lang) or ""
    if not enabled or not use_ai:
        return base

    variant = _pick_text_variant(
        block,
        lang=lang,
        default_lang=default_lang,
        prelim_score=int(prelim_score or 0),
        strong_threshold=int(score_threshold),
    )
    if variant:
        base = variant

    if should_use_enriched_copy(
        enabled=enabled,
        use_ai=use_ai,
        ci_state=ci_state,
        raw_user_text=raw_user_text,
        response_delay_s=response_delay_s,
        prelim_score=int(prelim_score or 0),
        score_threshold=score_threshold,
        friction_seconds=friction_seconds,
    ):
        enriched = pick_text_field(block, "text_enriched", lang, default_lang)
        if enriched:
            return enriched

    return base
