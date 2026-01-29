from __future__ import annotations

from pydantic import BaseModel, Field


class CatalogFlow(BaseModel):
    flow_id: str | None = None
    name: str | None = None
    version: int | None = None
    published: bool = False
    published_at: str | None = None
    owner_type: str = Field(default="TENANT")
    owner_id: str | None = None


class CatalogScope(BaseModel):
    scope_key: str
    source: str = Field(default="FILESYSTEM")
    has_filesystem_definition: bool = False
    flows: list[CatalogFlow] = Field(default_factory=list)
    status: str = Field(default="NO_FLOW_YET")


class CatalogVertical(BaseModel):
    vertical_key: str
    scopes: list[CatalogScope] = Field(default_factory=list)


class CatalogWarning(BaseModel):
    code: str
    detail: str


class CatalogResponse(BaseModel):
    verticals: list[CatalogVertical] = Field(default_factory=list)
    warnings: list[CatalogWarning] = Field(default_factory=list)
