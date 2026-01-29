from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from app.api.deps import get_db
from app.middleware.authz import require_role
from app.models.users import UserRole
from app.schemas.catalog import CatalogResponse
from app.services.catalog_service import list_catalog

router = APIRouter(prefix="/catalog", tags=["catalog"])


@router.get("", response_model=CatalogResponse, dependencies=[Depends(require_role(UserRole.SUPER_ADMIN.value))])
def get_catalog(
    vertical_key: str | None = Query(None),
    tenant_id: str | None = Query(None),
    include_empty_scopes: bool = Query(True),
    include_drafts: bool = Query(True),
    include_templates: bool = Query(True),
    only_published: bool = Query(False),
    db=Depends(get_db),
):
    return list_catalog(
        db,
        vertical_key=vertical_key,
        tenant_id=tenant_id,
        include_empty_scopes=include_empty_scopes,
        include_drafts=include_drafts,
        include_templates=include_templates,
        only_published=only_published,
    )
