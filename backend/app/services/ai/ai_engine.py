from app.services.ai.provider_factory import get_ai_provider

ai = get_ai_provider()


async def ai_extract(user_message: str, *, purpose: str = "extraction", tenant_id=None, language=None):
    return await ai.extract_fields(user_message, purpose=purpose, tenant_id=tenant_id, language=language)


async def ai_summary(lead_data: dict, *, tenant_id=None, language=None):
    return await ai.generate_summary(lead_data, tenant_id=tenant_id, language=language)


async def ai_reply(message: str, context: dict, *, purpose: str = "reply_contextual", tenant_id=None, language=None):
    return await ai.generate_reply(message, context, purpose=purpose, tenant_id=tenant_id, language=language)
