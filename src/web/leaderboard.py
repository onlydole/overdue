"""Leaderboard route."""

from fastapi import APIRouter, Depends, Request
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.web_session import get_current_librarian_optional
from src.db.engine import get_session
from src.db.tables import BadgeRow, LibrarianRow, StreakRow
from src.game.avatars import render_avatar_svg
from src.game.xp import get_rank
from src.web.templates import templates

router = APIRouter()


@router.get("/leaderboard")
async def leaderboard(
    request: Request,
    session: AsyncSession = Depends(get_session),
):
    current_user = await get_current_librarian_optional(request, session)
    """Render the leaderboard page."""
    result = await session.execute(
        select(LibrarianRow).order_by(LibrarianRow.total_xp.desc()).limit(25)
    )
    librarians = result.scalars().all()

    entries = []
    for i, lib in enumerate(librarians, 1):
        badge_count_result = await session.execute(
            select(func.count()).select_from(BadgeRow).where(BadgeRow.librarian_id == lib.id)
        )
        badge_count = badge_count_result.scalar() or 0

        streak_result = await session.execute(
            select(StreakRow).where(StreakRow.librarian_id == lib.id)
        )
        streak = streak_result.scalar_one_or_none()

        entries.append({
            "position": i,
            "username": lib.username,
            "total_xp": lib.total_xp,
            "rank": get_rank(lib.total_xp),
            "badge_count": badge_count,
            "current_streak": streak.current_streak if streak else 0,
            "is_bot": lib.is_bot,
            "avatar_svg": render_avatar_svg(lib.avatar_id or "avatar_01", size=28),
            "librarian_id": lib.id,
        })

    return templates.TemplateResponse("leaderboard.html", {
        "request": request,
        "current_user": current_user,
        "entries": entries,
    })
