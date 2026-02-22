"""Card catalog -- search endpoints (v2 with fuzzy matching)."""

from difflib import SequenceMatcher

from fastapi import APIRouter, Depends, Query
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.volumes import calculate_dewey_score, volume_to_response
from src.config.settings import settings
from src.db.engine import get_session
from src.db.tables import VolumeRow, volume_bookmarks
from src.models.catalog import CatalogQuery, CatalogResponse, CatalogResult, SuggestResponse

router = APIRouter()

# Minimum relevance score for fuzzy results (configurable)
MIN_SCORE = getattr(settings, "search_min_score", 0.3)


def fuzzy_score(query: str, text: str) -> float:
    """Calculate fuzzy match score between query and text."""
    query_lower = query.lower()
    text_lower = text.lower()

    # Exact substring match
    if query_lower in text_lower:
        return 1.0

    # Fuzzy matching using SequenceMatcher
    return SequenceMatcher(None, query_lower, text_lower).ratio()


@router.get("/autocomplete", response_model=SuggestResponse)
async def autocomplete(
    q: str,
    limit: int = 5,
    session: AsyncSession = Depends(get_session),
) -> SuggestResponse:
    """Get autocomplete suggestions from volume titles (renamed from suggest)."""
    query = (
        select(VolumeRow.title)
        .where(
            VolumeRow.archived == False,  # noqa: E712
            VolumeRow.title.ilike(f"%{q}%"),
        )
        .limit(limit)
    )
    result = await session.execute(query)
    titles = [row[0] for row in result]
    return SuggestResponse(suggestions=titles, query=q)
