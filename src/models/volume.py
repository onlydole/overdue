"""Pydantic models for volumes."""

from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class VolumeCreate(BaseModel):
    """Request body for creating a new volume."""

    title: str = Field(..., min_length=1, max_length=60)
    content: str = Field(..., min_length=1)
    shelf_id: int
    bookmarks: list[str] = Field(default_factory=list)

    @field_validator("bookmarks")
    @classmethod
    def unique_bookmarks(cls, value: list[str]) -> list[str]:
        return list(dict.fromkeys(value))


class VolumeUpdate(BaseModel):
    """Request body for updating a volume."""

    title: str | None = Field(None, min_length=1, max_length=60)
    content: str | None = Field(None, min_length=1)
    shelf_id: int | None = None
    bookmarks: list[str] | None = None

    @field_validator("title", "content", "shelf_id")
    @classmethod
    def reject_null(cls, value: str | int | None) -> str | int:
        if value is None:
            raise ValueError("This field cannot be null.")
        return value

    @field_validator("bookmarks")
    @classmethod
    def unique_bookmarks(cls, value: list[str] | None) -> list[str] | None:
        return list(dict.fromkeys(value)) if value is not None else None


class VolumeResponse(BaseModel):
    """Response body for a volume."""

    id: int
    title: str
    content: str
    shelf_id: int
    author_id: int
    bookmarks: list[str]
    dewey_score: float
    created_at: datetime
    updated_at: datetime
    last_reviewed_at: datetime
    archived: bool

    model_config = {"from_attributes": True}


class VolumeListResponse(BaseModel):
    """Paginated list of volumes."""

    items: list[VolumeResponse]
    total: int
    page: int
    per_page: int
