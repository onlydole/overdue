"""Achievement badge definitions and tracking."""

from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.tables import BadgeRow, LibrarianRow, ReviewRow, StreakRow, VolumeRow

BADGE_TIERS = ("Common", "Rare")

BADGE_DEFINITIONS = {
    "First Shelve": {
        "description": "Created your first volume",
        "icon": "book-open",
        "tier": "Common",
        "check": "volume_count >= 1",
    },
    "Dust Buster": {
        "description": "Reviewed 10 overdue volumes",
        "icon": "sparkles",
        "tier": "Common",
        "check": "overdue_reviews >= 10",
    },
    "Streak Master": {
        "description": "7-day review streak",
        "icon": "fire",
        "tier": "Common",
        "check": "current_streak >= 7",
    },
    "Pristine Stacks": {
        "description": "All volumes above Dewey 75 at once",
        "icon": "star",
        "tier": "Common",
        "check": "all_above_75",
    },
    "Encyclopedist": {
        "description": "50 volumes authored",
        "icon": "library",
        "tier": "Common",
        "check": "volume_count >= 50",
    },
    "Night Owl": {
        "description": "Reviewed a volume after midnight",
        "icon": "moon",
        "tier": "Common",
        "check": "night_review",
    },
    "Speed Reader": {
        "description": "Reviewed 5 volumes in under a minute",
        "icon": "zap",
        "tier": "Common",
        "check": "speed_reviews >= 5",
    },
    "Completionist": {
        "description": "Earned all other badges",
        "icon": "trophy",
        "tier": "Common",
        "check": "all_badges",
    },
    # --- Rare tier badges ---
    "Marathon Reader": {
        "description": "30-day review streak",
        "icon": "fire",
        "tier": "Rare",
        "check": "current_streak >= 30",
    },
    "Dewey Devotee": {
        "description": "Maintained average Dewey Score above 90 for 7 days",
        "icon": "award",
        "tier": "Rare",
        "check": "avg_dewey_7d >= 90",
    },
    "Centurion": {
        "description": "Reviewed 100 volumes total",
        "icon": "trophy",
        "tier": "Rare",
        "check": "total_reviews >= 100",
    },
}


async def get_earned_badges(session: AsyncSession, librarian_id: int) -> list[dict]:
    """Get all badges earned by a librarian."""
    result = await session.execute(
        select(BadgeRow)
        .where(BadgeRow.librarian_id == librarian_id)
        .order_by(BadgeRow.earned_at.desc())
    )
    rows = result.scalars().all()
    return [
        {
            "name": row.badge_name,
            "description": BADGE_DEFINITIONS.get(row.badge_name, {}).get("description", ""),
            "icon": BADGE_DEFINITIONS.get(row.badge_name, {}).get("icon", "award"),
            "tier": BADGE_DEFINITIONS.get(row.badge_name, {}).get("tier", "Common"),
            "earned_at": row.earned_at,
        }
        for row in rows
    ]


async def has_badge(session: AsyncSession, librarian_id: int, badge_name: str) -> bool:
    """Check if a librarian has already earned a specific badge."""
    result = await session.execute(
        select(BadgeRow).where(
            BadgeRow.librarian_id == librarian_id,
            BadgeRow.badge_name == badge_name,
        )
    )
    return result.scalar_one_or_none() is not None


async def grant_badge(session: AsyncSession, librarian_id: int, badge_name: str) -> bool:
    """Grant a badge to a librarian if they don't already have it."""
    if await has_badge(session, librarian_id, badge_name):
        return False

    badge = BadgeRow(
        librarian_id=librarian_id,
        badge_name=badge_name,
    )
    session.add(badge)
    await session.flush()
    return True


async def check_badges_after_shelve(session: AsyncSession, librarian_id: int) -> list[str]:
    """Check and award badges after shelving a volume."""
    awarded = []

    # First Shelve
    count_result = await session.execute(
        select(func.count()).select_from(VolumeRow).where(VolumeRow.author_id == librarian_id)
    )
    volume_count = count_result.scalar() or 0

    if volume_count >= 1 and not await has_badge(session, librarian_id, "First Shelve"):
        await grant_badge(session, librarian_id, "First Shelve")
        awarded.append("First Shelve")

    if volume_count >= 50 and not await has_badge(session, librarian_id, "Encyclopedist"):
        await grant_badge(session, librarian_id, "Encyclopedist")
        awarded.append("Encyclopedist")

    return awarded


async def check_badges_after_review(session: AsyncSession, librarian_id: int) -> list[str]:
    """Check and award badges after reviewing a volume."""
    awarded = []

    # Night Owl -- reviewed after midnight
    now = datetime.utcnow()
    if now.hour < 5 and not await has_badge(session, librarian_id, "Night Owl"):
        await grant_badge(session, librarian_id, "Night Owl")
        awarded.append("Night Owl")

    # Streak Master
    streak_result = await session.execute(
        select(StreakRow).where(StreakRow.librarian_id == librarian_id)
    )
    streak = streak_result.scalar_one_or_none()
    if streak and streak.current_streak >= 7 and not await has_badge(session, librarian_id, "Streak Master"):
        await grant_badge(session, librarian_id, "Streak Master")
        awarded.append("Streak Master")

    # Check completionist
    all_other = [b for b in BADGE_DEFINITIONS if b != "Completionist"]
    earned_result = await session.execute(
        select(func.count()).select_from(BadgeRow).where(
            BadgeRow.librarian_id == librarian_id,
            BadgeRow.badge_name.in_(all_other),
        )
    )
    earned_count = earned_result.scalar() or 0
    if earned_count == len(all_other) and not await has_badge(session, librarian_id, "Completionist"):
        await grant_badge(session, librarian_id, "Completionist")
        awarded.append("Completionist")

    return awarded
