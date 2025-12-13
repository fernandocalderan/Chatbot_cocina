from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.api.deps import get_db, get_tenant_id
from app.middleware.authz import require_any_role
from app.models.conversation_templates import ConversationTemplate
from app.services.template_service import TemplateService

router = APIRouter(prefix="/templates", tags=["templates"])


class TemplateCreate(BaseModel):
    name: str
    description: Optional[str] = None
    schema_json: dict
    is_default: bool = False


def _serialize(tpl: ConversationTemplate) -> dict:
    return {
        "id": str(tpl.id),
        "tenant_id": str(tpl.tenant_id) if tpl.tenant_id else None,
        "name": tpl.name,
        "description": tpl.description,
        "schema_json": tpl.schema_json,
        "is_default": bool(tpl.is_default),
        "created_at": tpl.created_at.isoformat() if tpl.created_at else None,
        "updated_at": tpl.updated_at.isoformat() if tpl.updated_at else None,
    }


@router.get(
    "",
    dependencies=[Depends(require_any_role("OWNER", "ADMIN"))],
)
def list_templates(
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    templates = TemplateService.list_templates(db, tenant_id)
    return [_serialize(t) for t in templates]


@router.post(
    "",
    dependencies=[Depends(require_any_role("OWNER", "ADMIN"))],
)
def create_template(
    payload: TemplateCreate,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    tpl = ConversationTemplate(
        tenant_id=tenant_id,
        name=payload.name,
        description=payload.description,
        schema_json=payload.schema_json,
        is_default=payload.is_default,
    )
    db.add(tpl)
    db.commit()
    db.refresh(tpl)
    return _serialize(tpl)


@router.post(
    "/{template_id}/clone",
    dependencies=[Depends(require_any_role("OWNER", "ADMIN"))],
)
def clone_template(
    template_id: str,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    tpl = TemplateService.get(db, template_id)
    if not tpl:
        raise HTTPException(status_code=404, detail="template_not_found")
    clone = TemplateService.clone_template_to_tenant(db, tpl, tenant_id)
    return _serialize(clone)


@router.post(
    "/onboarding/clone-default",
    dependencies=[Depends(require_any_role("OWNER", "ADMIN"))],
)
def clone_default_template(
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    clone = TemplateService.clone_default_template(db, tenant_id)
    if not clone:
        raise HTTPException(status_code=404, detail="no_default_template")
    return _serialize(clone)
