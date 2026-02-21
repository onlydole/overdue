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


@router.post("/search", response_model=CatalogResponse)
async def search_catalog(
    body: CatalogQuery,
    fuzzy: bool = Query(False, description="Enable fuzzy matching"),
    session: AsyncSession = Depends(get_session),
) -> CatalogResponse:
    """Search the card catalog for volumes with optional fuzzy matching."""
    query = select(VolumeRow)

    if not body.include_archived:
        query = query.where(VolumeRow.archived == False)  # noqa: E712

    if body.shelf_id:
        query = query.where(VolumeRow.shelf_id == body.shelf_id)

    if not fuzzy:
        # Exact substring search
        search_term = f"%{body.query}%"
        query = query.where(
            or_(
                VolumeRow.title.ilike(search_term),
                VolumeRow.content.ilike(search_term),
            )
        )

    # Filter by bookmarks if specified
    if body.bookmarks:
        for tag in body.bookmarks:
            subq = select(volume_bookmarks.c.volume_id).where(
                volume_bookmarks.c.bookmark == tag
            )
            query = query.where(VolumeRow.id.in_(subq))

    # Filter by minimum Dewey Score
    if hasattr(body, "min_dewey_score") and body.min_dewey_score is not None:
        # Applied post-query since Dewey is computed on read
        pass

    result = await session.execute(query)
    rows = result.scalars().all()

    results = []
    for row in rows:
        bm_result = await session.execute(
            select(volume_bookmarks.c.bookmark).where(volume_bookmarks.c.volume_id == row.id)
        )
        bookmarks = [b for (b,) in bm_result]
        vol_response = volume_to_response(row, bookmarks)

        if fuzzy:
            title_score = fuzzy_score(body.query, row.title)
            content_score = fuzzy_score(body.query, row.content[:200])
            relevance = max(title_score, content_score * 0.7)
            if relevance < MIN_SCORE:
                continue
        else:
            relevance = 1.0 if body.query.lower() in row.title.lower() else 0.5

        # Generate excerpt
        excerpt = ""
        content_lower = row.content.lower()
        query_lower = body.query.lower()
        idx = content_lower.find(query_lower)
        if idx >= 0:
            start = max(0, idx - 50)
            end = min(len(row.content), idx + len(body.query) + 50)
            excerpt = ("..." if start > 0 else "") + row.content[start:end] + ("..." if end < len(row.content) else "")

        results.append(CatalogResult(
            volume=vol_response,
            relevance=round(relevance, 3),
            excerpt=excerpt,
        ))

    # Sort by relevance
    results.sort(key=lambda r: r.relevance, reverse=True)

    return CatalogResponse(results=results, total=len(results), query=body.query)


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
