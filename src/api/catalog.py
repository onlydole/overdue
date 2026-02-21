"""Card catalog -- search endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.volumes import calculate_dewey_score, volume_to_response
from src.db.engine import get_session
from src.db.tables import VolumeRow, volume_bookmarks
from src.models.catalog import CatalogQuery, CatalogResponse, CatalogResult, SuggestResponse

router = APIRouter()


@router.post("/search", response_model=CatalogResponse)
async def search_catalog(
    body: CatalogQuery,
    session: AsyncSession = Depends(get_session),
) -> CatalogResponse:
    """Search the card catalog for volumes."""
    query = select(VolumeRow)

    if not body.include_archived:
        query = query.where(VolumeRow.archived == False)  # noqa: E712

    if body.shelf_id:
        query = query.where(VolumeRow.shelf_id == body.shelf_id)

    # Text search across title and content
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

    result = await session.execute(query)
    rows = result.scalars().all()

    results = []
    for row in rows:
        bm_result = await session.execute(
            select(volume_bookmarks.c.bookmark).where(volume_bookmarks.c.volume_id == row.id)
        )
        bookmarks = [b for (b,) in bm_result]
        vol_response = volume_to_response(row, bookmarks)

        # Simple relevance: title match scores higher than content match
        relevance = 1.0 if body.query.lower() in row.title.lower() else 0.5
        results.append(CatalogResult(volume=vol_response, relevance=relevance))

    # Sort by relevance
    results.sort(key=lambda r: r.relevance, reverse=True)

    return CatalogResponse(results=results, total=len(results), query=body.query)


@router.get("/suggest", response_model=SuggestResponse)
async def suggest(
    q: str,
    limit: int = 5,
    session: AsyncSession = Depends(get_session),
) -> SuggestResponse:
    """Get autocomplete suggestions from volume titles."""
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
