"""My Library route -- personal dashboard for authenticated users."""

from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.volumes import calculate_dewey_score
from src.auth.web_session import get_current_librarian_required
from src.config.defaults import DEWEY_OVERDUE
from src.db.engine import get_session
from src.db.tables import ShelfRow, VolumeRow
from src.game.badges import get_earned_badges
from src.game.streaks import get_streak
from src.game.xp import get_next_rank, get_rank, get_recent_awards

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/my-library")
async def my_library(
    request: Request,
    session: AsyncSession = Depends(get_session),
):
    """Render the personal library dashboard."""
    user = await get_current_librarian_required(request, session)
    if isinstance(user, RedirectResponse):
        return user

    librarian_id = user["id"]

    # Get user's shelves
    shelves_result = await session.execute(
        select(ShelfRow).where(ShelfRow.created_by == librarian_id)
    )
    my_shelves = shelves_result.scalars().all()

    shelf_data = []
    for shelf in my_shelves:
        vol_result = await session.execute(
            select(VolumeRow).where(
                VolumeRow.shelf_id == shelf.id,
                VolumeRow.archived == False,  # noqa: E712
            )
        )
        volumes = vol_result.scalars().all()
        avg_dewey = 100.0
        if volumes:
            scores = [calculate_dewey_score(v.last_reviewed_at) for v in volumes]
            avg_dewey = sum(scores) / len(scores)
        shelf_data.append({
            "id": shelf.id,
            "name": shelf.name,
            "volume_count": len(volumes),
            "average_dewey": round(avg_dewey, 1),
        })

    # Get user's overdue volumes
    volumes_result = await session.execute(
        select(VolumeRow).where(
            VolumeRow.author_id == librarian_id,
            VolumeRow.archived == False,  # noqa: E712
        )
    )
    all_volumes = volumes_result.scalars().all()
    overdue_volumes = []
    for v in all_volumes:
        score = calculate_dewey_score(v.last_reviewed_at)
        if score <= DEWEY_OVERDUE:
            overdue_volumes.append({
                "id": v.id,
                "title": v.title,
                "dewey_score": round(score, 1),
                "last_reviewed_at": v.last_reviewed_at,
            })
    overdue_volumes.sort(key=lambda x: x["dewey_score"])

    # XP and rank
    rank = get_rank(user["total_xp"])
    next_rank, xp_to_next = get_next_rank(user["total_xp"])
    badges = await get_earned_badges(session, librarian_id)
    streak = await get_streak(session, librarian_id)
    recent_awards = await get_recent_awards(session, librarian_id, limit=5)

    # Progress percentage
    progress = 0
    if next_rank and xp_to_next:
        from src.config.defaults import RANKS
        current_threshold = 0
        next_threshold = 0
        for rank_name, threshold in RANKS:
            if rank_name == rank:
                current_threshold = threshold
            if rank_name == next_rank:
                next_threshold = threshold
        total_needed = next_threshold - current_threshold
        earned = user["total_xp"] - current_threshold
        progress = int((earned / total_needed) * 100) if total_needed > 0 else 100

    return templates.TemplateResponse("my_library.html", {
        "request": request,
        "current_user": user,
        "my_shelves": shelf_data,
        "overdue_volumes": overdue_volumes,
        "total_volumes": len(all_volumes),
        "rank": rank,
        "next_rank": next_rank,
        "xp_to_next": xp_to_next,
        "progress": progress,
        "badges": badges,
        "streak": streak,
        "recent_awards": recent_awards,
    })
