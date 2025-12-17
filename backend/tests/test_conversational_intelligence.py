from app.services.conversational_intelligence import (
    is_doubt_text,
    is_question_text,
    resolve_block_text,
)


def test_is_doubt_text():
    assert is_doubt_text("No sé")
    assert is_doubt_text("depende")
    assert is_doubt_text("más o menos")
    assert not is_doubt_text("sí")


def test_is_question_text():
    assert is_question_text("¿Cómo funciona?")
    assert is_question_text("como funciona")
    assert is_question_text("Cuánto cuesta")
    assert not is_question_text("vale")


def test_resolve_block_text_uses_base_when_ai_off():
    block = {"text": {"es": "Base", "en": "BaseEN"}, "text_enriched": {"es": "Enriched"}}
    out = resolve_block_text(
        block,
        lang="es",
        default_lang="es",
        enabled=True,
        use_ai=False,
        ci_state={"free_text_seen": True},
        raw_user_text="no sé",
        response_delay_s=99,
        prelim_score=99,
    )
    assert out == "Base"


def test_resolve_block_text_uses_base_when_disabled():
    block = {"text": {"es": "Base"}, "text_enriched": {"es": "Enriched"}}
    out = resolve_block_text(
        block,
        lang="es",
        default_lang="es",
        enabled=False,
        use_ai=True,
        ci_state={"free_text_seen": True},
        raw_user_text="no sé",
        response_delay_s=99,
        prelim_score=99,
    )
    assert out == "Base"


def test_resolve_block_text_uses_enriched_when_triggered():
    block = {"text": {"es": "Base"}, "text_enriched": {"es": "Enriched"}}
    out = resolve_block_text(
        block,
        lang="es",
        default_lang="es",
        enabled=True,
        use_ai=True,
        ci_state={"free_text_seen": True},
        raw_user_text="ok",
        response_delay_s=1,
        prelim_score=0,
    )
    assert out == "Enriched"


def test_resolve_block_text_uses_variants_by_score():
    block = {
        "text": {"es": "Base"},
        "text_variants": ["Directa", "Suave"],
    }
    out_strong = resolve_block_text(
        block,
        lang="es",
        default_lang="es",
        enabled=True,
        use_ai=True,
        ci_state={},
        raw_user_text="ok",
        response_delay_s=0,
        prelim_score=90,
        score_threshold=70,
    )
    out_mid = resolve_block_text(
        block,
        lang="es",
        default_lang="es",
        enabled=True,
        use_ai=True,
        ci_state={},
        raw_user_text="ok",
        response_delay_s=0,
        prelim_score=40,
        score_threshold=70,
    )
    assert out_strong == "Directa"
    assert out_mid == "Suave"
