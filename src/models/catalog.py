"""Pydantic models for catalog search."""

from pydantic import BaseModel, Field

from src.models.volume import VolumeResponse


class CatalogQuery(BaseModel):
    """Search query for the card catalog."""

    query: str = Field(..., min_length=1)
    shelf_id: int | None = None
    bookmarks: list[str] = Field(default_factory=list)
    include_archived: bool = False
    min_dewey_score: float | None = None


class CatalogResult(BaseModel):
    """A single search result with excerpt."""

    volume: VolumeResponse
    relevance: float = Field(..., ge=0.0, le=1.0)
    excerpt: str = ""


class CatalogResponse(BaseModel):
    """Search results from the catalog."""

    results: list[CatalogResult]
    total: int
    query: str


class SuggestResponse(BaseModel):
    """Auto-complete suggestions."""

    suggestions: list[str]
    query: str
