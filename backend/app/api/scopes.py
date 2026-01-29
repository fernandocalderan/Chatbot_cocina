from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.middleware.authz import require_role
from app.models.scopes import Scope
from app.models.users import UserRole

router = APIRouter(prefix="/scopes", tags=["scopes"])


class ScopeCreate(BaseModel):
    vertical_key: str = Field(..., min_length=1)
    scope_key: str = Field(..., min_length=1)
    display_name: str = Field(..., min_length=1)
    description: str | None = None


@router.post("", status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_role(UserRole.SUPER_ADMIN.value))])
def create_scope(payload: ScopeCreate, db: Session = Depends(get_db)):
    existing = (
        db.query(Scope)
        .filter(Scope.vertical_key == payload.vertical_key, Scope.scope_key == payload.scope_key)
        .first()
    )
    if existing:
        raise HTTPException(status_code=409, detail="scope_already_exists")

    scope = Scope(
        vertical_key=payload.vertical_key,
        scope_key=payload.scope_key,
        display_name=payload.display_name,
        description=payload.description,
    )
    db.add(scope)
    db.commit()
    db.refresh(scope)
    return {
        "id": str(scope.id),
        "vertical_key": scope.vertical_key,
        "scope_key": scope.scope_key,
        "display_name": scope.display_name,
        "description": scope.description,
        "created_at": scope.created_at.isoformat() if scope.created_at else None,
    }
