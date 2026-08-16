"""XP calculation, rank thresholds, and leveling."""

from typing import Any

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.config.defaults import (
    RANKS,
    XP_DAILY_STREAK_BONUS,
    XP_RESCUE_BONUS,
    XP_REVIEW_CURRENT,
    XP_REVIEW_OVERDUE_MULTIPLIER,
    XP_SHELVE_VOLUME,
)
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

    # Update total atomically in the database: a read-modify-write through the
    # ORM loses awards when two sessions review at the same time. RETURNING
    # gives back the fresh total without a per-award refresh SELECT.
    result = await session.execute(
        update(LibrarianRow)
        .where(LibrarianRow.id == librarian_id)
        .values(total_xp=LibrarianRow.total_xp + amount)
        .returning(LibrarianRow.total_xp)
    )
    new_total = result.scalar_one()

    # Check for rank up
    new_rank = get_rank(new_total)
    if new_rank != librarian.role:
        librarian.role = new_rank

    await session.flush()
    return new_total


async def award_shelve_xp(session: AsyncSession, librarian_id: int) -> int:
    """Award XP for shelving a new volume."""
    return await award_xp(session, librarian_id, XP_SHELVE_VOLUME, "Shelved a new volume")


async def award_review_xp(
    session: AsyncSession,
    librarian_id: int,
    was_overdue: bool,
) -> int:
    """Award XP for reviewing a volume.

    Overdue reviews earn base XP * multiplier (2x by default).
    """
    if was_overdue:
        amount = XP_REVIEW_CURRENT * XP_REVIEW_OVERDUE_MULTIPLIER
        reason = f"Reviewed an overdue volume ({XP_REVIEW_OVERDUE_MULTIPLIER}x bonus)"
    else:
        amount = XP_REVIEW_CURRENT
        reason = "Reviewed a current volume"
    return await award_xp(session, librarian_id, amount, reason)


async def award_rescue_bonus(session: AsyncSession, librarian_id: int) -> int:
    """Award rescue bonus XP for saving a volume from Overdue territory."""
    return await award_xp(
        session, librarian_id, XP_RESCUE_BONUS, "Rescue bonus (saved from Overdue)"
    )


async def award_streak_bonus(session: AsyncSession, librarian_id: int) -> int:
    """Award daily streak bonus XP."""
    return await award_xp(session, librarian_id, XP_DAILY_STREAK_BONUS, "Daily streak bonus")


async def get_recent_awards(
    session: AsyncSession,
    librarian_id: int,
    limit: int = 10,
) -> list[dict[str, Any]]:
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
