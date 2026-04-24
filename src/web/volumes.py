"""Volume detail routes."""

from fastapi import APIRouter, Depends, Request
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.api.volumes import calculate_dewey_score
from src.auth.web_session import get_current_librarian_optional
from src.db.engine import get_session
from src.db.tables import ReviewRow, VolumeRow, volume_bookmarks
from src.web.templates import templates

router = APIRouter()

REVIEWS_PER_PAGE = 5


@router.get("/volumes/{volume_id}")
async def volume_detail(
    volume_id: int,
    request: Request,
    session: AsyncSession = Depends(get_session),
):
    """Render a volume detail page."""
    current_user = await get_current_librarian_optional(request, session)
    result = await session.execute(
        select(VolumeRow)
        .where(VolumeRow.id == volume_id)
        .options(selectinload(VolumeRow.author))
    )
    volume = result.scalar_one_or_none()
    if not volume:
        return templates.TemplateResponse(request, "404.html", {
            "request": request,
            "current_user": current_user,
        }, status_code=404)

    score = calculate_dewey_score(volume.last_reviewed_at)

    # Get bookmarks
    bm_result = await session.execute(
        select(volume_bookmarks.c.bookmark).where(volume_bookmarks.c.volume_id == volume.id)
    )
    bookmarks = [b for (b,) in bm_result]

    # Get first page of review history and total count for the heading
    reviews_result = await session.execute(
        select(ReviewRow)
        .where(ReviewRow.volume_id == volume.id)
        .order_by(ReviewRow.reviewed_at.desc())
        .limit(REVIEWS_PER_PAGE + 1)
    )
    reviews = list(reviews_result.scalars().all())
    has_more = len(reviews) > REVIEWS_PER_PAGE
    reviews = reviews[:REVIEWS_PER_PAGE]
    count_result = await session.execute(
        select(func.count()).select_from(ReviewRow).where(ReviewRow.volume_id == volume.id)
    )
    total_reviews = count_result.scalar() or 0

    return templates.TemplateResponse(request, "volume_detail.html", {
        "request": request,
        "current_user": current_user,
        "volume": volume,
        "dewey_score": round(score, 1),
        "bookmarks": bookmarks,
        "reviews": reviews,
        "review_page": 1,
        "has_more_reviews": has_more,
        "total_reviews": total_reviews,
    })


@router.get("/volumes/{volume_id}/reviews")
async def volume_reviews_page(
    volume_id: int,
    request: Request,
    page: int = 2,
    session: AsyncSession = Depends(get_session),
):
    """Return a page of review history as an HTML fragment for HTMX."""
    offset = (page - 1) * REVIEWS_PER_PAGE
    reviews_result = await session.execute(
        select(ReviewRow)
        .where(ReviewRow.volume_id == volume_id)
        .order_by(ReviewRow.reviewed_at.desc())
        .offset(offset)
        .limit(REVIEWS_PER_PAGE + 1)
    )
    reviews = list(reviews_result.scalars().all())
    has_more = len(reviews) > REVIEWS_PER_PAGE
    reviews = reviews[:REVIEWS_PER_PAGE]

    return templates.TemplateResponse(request, "partials/review_history_page.html", {
        "request": request,
        "reviews": reviews,
        "volume_id": volume_id,
        "review_page": page,
        "has_more_reviews": has_more,
    })
