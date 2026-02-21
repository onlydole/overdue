"""XP calculation, rank thresholds, and leveling."""

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.config.defaults import RANKS, XP_DAILY_STREAK_BONUS, XP_REVIEW_CURRENT, XP_REVIEW_OVERDUE, XP_SHELVE_VOLUME
from src.db.tables import LibrarianRow, XPLedgerRow


def get_rank(total_xp: int) -> str:
    """Determine the librarian rank based on total XP."""
    current_rank = RANKS[0][0]
    for rank_name, threshold in RANKS:
        if total_xp >= threshold:
            current_rank = rank_name
    return current_rank


def get_next_rank(total_xp: int) -> tuple[str | None, int | None]:
    """Get the next rank and XP needed to reach it."""
    for i, (rank_name, threshold) in enumerate(RANKS):
        if total_xp < threshold:
            return rank_name, threshold - total_xp
    return None, None


async def award_xp(
    session: AsyncSession,
    librarian_id: int,
    amount: int,
    reason: str,
) -> int:
    """Award XP to a librarian and update their rank."""
    librarian = await session.get(LibrarianRow, librarian_id)
    if not librarian:
        return 0

    # Record in ledger
    entry = XPLedgerRow(
        librarian_id=librarian_id,
        amount=amount,
        reason=reason,
    )
    session.add(entry)

    # Update total
    librarian.total_xp += amount

    # Check for rank up
    new_rank = get_rank(librarian.total_xp)
    if new_rank != librarian.role:
        librarian.role = new_rank

    await session.flush()
    return librarian.total_xp


async def award_shelve_xp(session: AsyncSession, librarian_id: int) -> int:
    """Award XP for shelving a new volume."""
    return await award_xp(session, librarian_id, XP_SHELVE_VOLUME, "Shelved a new volume")


async def award_review_xp(
    session: AsyncSession,
    librarian_id: int,
    was_overdue: bool,
) -> int:
    """Award XP for reviewing a volume."""
    amount = XP_REVIEW_OVERDUE if was_overdue else XP_REVIEW_CURRENT
    reason = "Reviewed an overdue volume" if was_overdue else "Reviewed a current volume"
    return await award_xp(session, librarian_id, amount, reason)


async def award_streak_bonus(session: AsyncSession, librarian_id: int) -> int:
    """Award daily streak bonus XP."""
    return await award_xp(session, librarian_id, XP_DAILY_STREAK_BONUS, "Daily streak bonus")


async def get_recent_awards(
    session: AsyncSession,
    librarian_id: int,
    limit: int = 10,
) -> list[dict]:
    """Get recent XP awards for a librarian."""
    result = await session.execute(
        select(XPLedgerRow)
        .where(XPLedgerRow.librarian_id == librarian_id)
        .order_by(XPLedgerRow.created_at.desc())
        .limit(limit)
    )
    rows = result.scalars().all()
    return [
        {
            "amount": row.amount,
            "reason": row.reason,
            "created_at": row.created_at,
        }
        for row in rows
    ]
