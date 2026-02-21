"""Pydantic models for shelves."""

from datetime import datetime

from pydantic import BaseModel, Field


class ShelfCreate(BaseModel):
    """Request body for creating a new shelf."""

    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None


class ShelfUpdate(BaseModel):
    """Request body for updating a shelf."""

    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None


class ShelfResponse(BaseModel):
    """Response body for a shelf."""

    id: int
    name: str
    description: str | None
    created_at: datetime
    created_by: int
    volume_count: int = 0
    average_dewey_score: float = 100.0

    model_config = {"from_attributes": True}


class ShelfListResponse(BaseModel):
    """List of shelves."""

    items: list[ShelfResponse]
    total: int
