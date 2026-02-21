"""Pydantic models for webhook bulletins."""

from datetime import datetime

from pydantic import BaseModel, Field, HttpUrl


class BulletinCreate(BaseModel):
    """Request body for creating a webhook subscription."""

    url: HttpUrl
    events: list[str] = Field(..., min_length=1)
    secret: str | None = None


class BulletinResponse(BaseModel):
    """Response body for a webhook subscription."""

    id: int
    url: str
    events: list[str]
    created_at: datetime
    active: bool

    model_config = {"from_attributes": True}


class BulletinListResponse(BaseModel):
    """List of webhook subscriptions."""

    items: list[BulletinResponse]
    total: int
