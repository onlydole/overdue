"""Volume detail routes."""

from fastapi import APIRouter, Depends, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.volumes import calculate_dewey_score
from src.auth.web_session import get_current_librarian_optional
from src.db.engine import get_session
from src.db.tables import ReviewRow, VolumeRow, volume_bookmarks
from src.web.templates import templates

router = APIRouter()


@router.get("/volumes/{volume_id}")
async def volume_detail(
    volume_id: int,
    request: Request,
    session: AsyncSession = Depends(get_session),
):
    """Render a volume detail page."""
    current_user = await get_current_librarian_optional(request, session)
    volume = await session.get(VolumeRow, volume_id)
    if not volume:
        return templates.TemplateResponse("dashboard.html", {
            "request": request,
            "current_user": current_user,
            "error": "Volume not found",
        })

    score = calculate_dewey_score(volume.last_reviewed_at)

    # Get bookmarks
    bm_result = await session.execute(
        select(volume_bookmarks.c.bookmark).where(volume_bookmarks.c.volume_id == volume.id)
    )
    bookmarks = [b for (b,) in bm_result]

    # Get review history
    reviews_result = await session.execute(
        select(ReviewRow)
        .where(ReviewRow.volume_id == volume.id)
        .order_by(ReviewRow.reviewed_at.desc())
        .limit(20)
    )
    reviews = reviews_result.scalars().all()

    return templates.TemplateResponse("volume_detail.html", {
        "request": request,
        "current_user": current_user,
        "volume": volume,
        "dewey_score": round(score, 1),
        "bookmarks": bookmarks,
        "reviews": reviews,
    })
