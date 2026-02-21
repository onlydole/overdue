"""Reading Room health check and dashboard data."""

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.volumes import calculate_dewey_score
from src.config.defaults import DEWEY_OVERDUE, MOODS, DEWEY_NEEDS_ATTENTION
from src.db.engine import get_session
from src.db.tables import VolumeRow

router = APIRouter()


def get_mood(average_score: float) -> tuple[str, str]:
    """Determine the reading room mood based on average Dewey Score."""
    for mood_name, threshold in MOODS:
        if average_score >= threshold:
            descriptions = {
                "Quiet study": "Warm golden light fills the reading room. Knowledge is well-tended.",
                "Gentle hum": "A pleasant bustle of activity. Most volumes are in good shape.",
                "Getting noisy": "The stacks are getting restless. Several volumes need attention.",
                "Call for order": "Warning! Many volumes are gathering dust. Review needed urgently.",
                "Closed for renovation": "The library needs serious attention. Knowledge is at risk.",
            }
            return mood_name, descriptions.get(mood_name, "")
    return "Closed for renovation", "The library needs serious attention."


@router.get("/health")
async def health_check(
    session: AsyncSession = Depends(get_session),
) -> dict:
    """Get the overall health of the library."""
    count_result = await session.execute(
        select(func.count())
        .select_from(VolumeRow)
        .where(VolumeRow.archived == False)  # noqa: E712
    )
    total_volumes = count_result.scalar() or 0

    if total_volumes == 0:
        return {
            "status": "healthy",
            "mood": "Quiet study",
            "description": "The library is empty but pristine. Time to shelve some knowledge!",
            "total_volumes": 0,
            "overdue_volumes": 0,
            "average_dewey_score": 100.0,
        }

    # Calculate scores
    volumes_result = await session.execute(
        select(VolumeRow).where(VolumeRow.archived == False)  # noqa: E712
    )
    volumes = volumes_result.scalars().all()
    scores = [calculate_dewey_score(v.last_reviewed_at) for v in volumes]

    avg_score = sum(scores) / len(scores)
    overdue_count = sum(1 for s in scores if s <= DEWEY_OVERDUE)
    mood_name, description = get_mood(avg_score)

    return {
        "status": "healthy",
        "mood": mood_name,
        "description": description,
        "total_volumes": total_volumes,
        "overdue_volumes": overdue_count,
        "average_dewey_score": round(avg_score, 1),
    }


@router.get("/overdue")
async def overdue_report(
    session: AsyncSession = Depends(get_session),
) -> dict:
    """Get a report of all overdue volumes needing review."""
    volumes_result = await session.execute(
        select(VolumeRow).where(VolumeRow.archived == False)  # noqa: E712
    )
    volumes = volumes_result.scalars().all()

    overdue_items = []
    needs_attention = []

    for v in volumes:
        score = calculate_dewey_score(v.last_reviewed_at)
        entry = {
            "id": v.id,
            "title": v.title,
            "shelf_id": v.shelf_id,
            "dewey_score": round(score, 1),
            "last_reviewed_at": v.last_reviewed_at.isoformat(),
        }
        if score <= DEWEY_OVERDUE:
            overdue_items.append(entry)
        elif score <= DEWEY_NEEDS_ATTENTION:
            needs_attention.append(entry)

    return {
        "overdue": overdue_items,
        "needs_attention": needs_attention,
        "total_overdue": len(overdue_items),
        "total_needs_attention": len(needs_attention),
    }
