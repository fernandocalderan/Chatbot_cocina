from app.services.ai.openai_service import OpenAIService

def get_ai_provider(provider: str = "openai"):
    if provider == "openai":
        return OpenAIService()
    else:
        raise Exception(f"AI provider '{provider}' not supported")
