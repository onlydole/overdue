"""Reading Room dashboard route."""

from fastapi import APIRouter, Depends, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.api.volumes import calculate_dewey_score
from src.auth.web_session import get_current_librarian_optional
from src.config.defaults import DEWEY_GOOD_SHAPE, DEWEY_NEEDS_ATTENTION, DEWEY_OVERDUE
from src.db.engine import get_session
from src.db.tables import LibrarianRow, ReviewRow, StreakRow, VolumeRow
from src.game.mood import calculate_mood
from src.web.templates import templates

router = APIRouter()


async def _build_reading_room_context(session: AsyncSession) -> dict:
    """Build template context for the Reading Room dashboard.

    Shared by both the full-page route and the HTMX partial endpoint.
    """
    volumes_result = await session.execute(
        select(VolumeRow).where(VolumeRow.archived == False)  # noqa: E712
    )
    volumes = volumes_result.scalars().all()
    total_volumes = len(volumes)

    distribution = {"pristine": 0, "good": 0, "attention": 0, "overdue": 0, "lost": 0}
    scores = []

    for v in volumes:
        score = calculate_dewey_score(v.last_reviewed_at)
        scores.append(score)
        if score >= DEWEY_GOOD_SHAPE:
            distribution["pristine"] += 1
        elif score >= DEWEY_NEEDS_ATTENTION:
            distribution["good"] += 1
        elif score >= DEWEY_OVERDUE:
            distribution["attention"] += 1
        else:
            distribution["overdue"] += 1

    avg_score = sum(scores) / len(scores) if scores else 100.0
    mood = calculate_mood(avg_score)

    recent_result = await session.execute(
        select(ReviewRow)
        .options(selectinload(ReviewRow.volume), selectinload(ReviewRow.librarian))
        .order_by(ReviewRow.reviewed_at.desc())
        .limit(10)
    )
    recent_reviews = recent_result.scalars().all()

    streak_result = await session.execute(
        select(LibrarianRow.username, StreakRow.current_streak)
        .join(StreakRow, StreakRow.librarian_id == LibrarianRow.id)
        .where(StreakRow.current_streak > 0)
        .order_by(StreakRow.current_streak.desc())
        .limit(5)
    )
    streak_leaders = [
        {"username": row[0], "current_streak": row[1]}
        for row in streak_result
    ]

    return {
        "mood": mood,
        "total_volumes": total_volumes,
        "distribution": distribution,
        "overdue_count": distribution["overdue"],
        "recent_reviews": recent_reviews,
        "streak_leaders": streak_leaders,
    }


@router.get("/")
async def reading_room(
    request: Request,
    session: AsyncSession = Depends(get_session),
):
    """Render the Reading Room dashboard."""
    current_user = await get_current_librarian_optional(request, session)
    ctx = await _build_reading_room_context(session)
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "current_user": current_user,
        **ctx,
    })


@router.get("/reading-room/live")
async def reading_room_live(
    request: Request,
    session: AsyncSession = Depends(get_session),
):
    """Return the live-updating partial for the Reading Room."""
    ctx = await _build_reading_room_context(session)
    return templates.TemplateResponse("partials/reading_room_live.html", {
        "request": request,
        **ctx,
    })
