"""Reading Room dashboard route."""

from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.volumes import calculate_dewey_score
from src.config.defaults import DEWEY_GOOD_SHAPE, DEWEY_NEEDS_ATTENTION, DEWEY_OVERDUE
from src.db.engine import get_session
from src.db.tables import ReviewRow, VolumeRow
from src.game.mood import calculate_mood

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/")
async def reading_room(
    request: Request,
    session: AsyncSession = Depends(get_session),
):
    """Render the Reading Room dashboard."""
    # Get all active volumes
    volumes_result = await session.execute(
        select(VolumeRow).where(VolumeRow.archived == False)  # noqa: E712
    )
    volumes = volumes_result.scalars().all()
    total_volumes = len(volumes)

    # Calculate score distribution
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

    # Recent reviews
    recent_result = await session.execute(
        select(ReviewRow).order_by(ReviewRow.reviewed_at.desc()).limit(10)
    )
    recent_reviews = recent_result.scalars().all()

    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "mood": mood,
        "total_volumes": total_volumes,
        "distribution": distribution,
        "overdue_count": distribution["overdue"],
        "recent_reviews": recent_reviews,
    })
