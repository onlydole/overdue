"""Review streak tracking with configurable cooldown.

Default: 5-second cooldown between reviews for demo mode.
Set OVERDUE_STREAK_COOLDOWN_SECONDS=86400 for realistic daily streaks.
"""

from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.config.settings import settings
from src.db.tables import StreakRow


async def update_streak(session: AsyncSession, librarian_id: int) -> dict:
    """Update the review streak for a librarian after a review.

    Uses configurable cooldown: if last review was within cooldown window,
    streak extends. If too much time passed, streak resets.
    """
    result = await session.execute(
        select(StreakRow).where(StreakRow.librarian_id == librarian_id)
    )
    streak = result.scalar_one_or_none()

    now = datetime.utcnow()
    cooldown = settings.streak_cooldown_seconds

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

    if not streak.last_review_date:
        streak.current_streak = 1
        streak.last_review_date = now
        await session.flush()
        return {
            "current_streak": 1,
            "longest_streak": streak.longest_streak,
            "is_new_day": True,
        }

    seconds_since = (now - streak.last_review_date).total_seconds()

    if seconds_since < cooldown:
        # Too soon -- still within same window, no streak change
        return {
            "current_streak": streak.current_streak,
            "longest_streak": streak.longest_streak,
            "is_new_day": False,
        }

    if seconds_since <= cooldown * 3:
        # Within the valid window (1x-3x cooldown) -- extend streak
        streak.current_streak += 1
    else:
        # Too long -- streak broken, reset
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
