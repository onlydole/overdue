"""Daily review streak tracking."""

from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.tables import StreakRow


async def update_streak(session: AsyncSession, librarian_id: int) -> dict:
    """Update the review streak for a librarian after a review."""
    result = await session.execute(
        select(StreakRow).where(StreakRow.librarian_id == librarian_id)
    )
    streak = result.scalar_one_or_none()

    now = datetime.utcnow()
    today = now.date()

    if not streak:
        streak = StreakRow(
            librarian_id=librarian_id,
            current_streak=1,
            longest_streak=1,
            last_review_date=now,
        )
        session.add(streak)
        await session.flush()
        return {
            "current_streak": 1,
            "longest_streak": 1,
            "is_new_day": True,
        }

    last_date = streak.last_review_date.date() if streak.last_review_date else None

    if last_date == today:
        # Already reviewed today
        return {
            "current_streak": streak.current_streak,
            "longest_streak": streak.longest_streak,
            "is_new_day": False,
        }

    if last_date == today - timedelta(days=1):
        # Consecutive day -- extend streak
        streak.current_streak += 1
    else:
        # Streak broken -- reset
        streak.current_streak = 1

    streak.last_review_date = now
    if streak.current_streak > streak.longest_streak:
        streak.longest_streak = streak.current_streak

    await session.flush()
    return {
        "current_streak": streak.current_streak,
        "longest_streak": streak.longest_streak,
        "is_new_day": True,
    }


async def get_streak(session: AsyncSession, librarian_id: int) -> dict:
    """Get the current streak info for a librarian."""
    result = await session.execute(
        select(StreakRow).where(StreakRow.librarian_id == librarian_id)
    )
    streak = result.scalar_one_or_none()

    if not streak:
        return {
            "current_streak": 0,
            "longest_streak": 0,
            "last_review_date": None,
        }

    return {
        "current_streak": streak.current_streak,
        "longest_streak": streak.longest_streak,
        "last_review_date": streak.last_review_date,
    }
