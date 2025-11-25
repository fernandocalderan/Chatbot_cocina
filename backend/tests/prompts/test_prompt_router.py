import pytest
from app.services.prompts.router.prompt_router import PromptRouter


def test_router_extraction_project_type():
    prompt = PromptRouter.get_extraction_prompt(
        purpose="project_type",
        user_text="Quiero una cocina nueva para mi piso",
    )
    assert "Texto del usuario" in prompt
    assert "tipo de proyecto" in prompt.lower()


def test_router_generation_welcome():
    prompt = PromptRouter.get_generation_prompt(
        purpose="welcome",
        payload={},
    )
    assert "asistente de un estudio de cocinas" in prompt
