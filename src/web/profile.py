"""Librarian profile route."""

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.web_session import get_current_librarian_optional
from src.db.engine import get_session
from src.db.tables import LibrarianRow
from src.game.badges import get_earned_badges
from src.game.streaks import get_streak
from src.game.xp import get_next_rank, get_rank, get_recent_awards
from src.web.templates import templates

router = APIRouter()


@router.get("/profile/{librarian_id}")
async def librarian_profile(
    librarian_id: int,
    request: Request,
    session: AsyncSession = Depends(get_session),
):
    """Render a librarian's profile page."""
    current_user = await get_current_librarian_optional(request, session)
    librarian = await session.get(LibrarianRow, librarian_id)
    if not librarian:
        return templates.TemplateResponse(request, "dashboard.html", {
            "request": request,
            "current_user": current_user,
            "error": "Librarian not found",
        })

    rank = get_rank(librarian.total_xp)
    next_rank, xp_to_next = get_next_rank(librarian.total_xp)
    badges = await get_earned_badges(session, librarian_id)
    streak = await get_streak(session, librarian_id)
    recent_awards = await get_recent_awards(session, librarian_id)

    # Calculate progress percentage to next rank
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
        earned = librarian.total_xp - current_threshold
        progress = int((earned / total_needed) * 100) if total_needed > 0 else 100

    avatar_id = librarian.avatar_id or "avatar_01"

    return templates.TemplateResponse(request, "profile.html", {
        "request": request,
        "current_user": current_user,
        "librarian": librarian,
        "avatar_id": avatar_id,
        "rank": rank,
        "next_rank": next_rank,
        "xp_to_next": xp_to_next,
        "progress": progress,
        "badges": badges,
        "streak": streak,
        "recent_awards": recent_awards,
    })
