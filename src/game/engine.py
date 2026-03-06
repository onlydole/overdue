"""Game action orchestrator -- wires XP, badges, and streaks together."""

from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from src.config.defaults import (
    DEWEY_OVERDUE,
    XP_DAILY_STREAK_BONUS,
    XP_RESCUE_BONUS,
    XP_REVIEW_CURRENT,
    XP_REVIEW_OVERDUE_MULTIPLIER,
    XP_SHELVE_VOLUME,
)
from src.db.tables import ReviewRow
from src.game.badges import check_badges_after_review, check_badges_after_shelve
from src.game.streaks import update_streak
from src.game.xp import (
    award_rescue_bonus,
    award_review_xp,
    award_shelve_xp,
    award_streak_bonus,
    get_rank,
)
from src.models.game import GameResult


async def on_volume_shelved(
    session: AsyncSession,
    librarian_id: int,
    volume_id: int,
) -> GameResult:
    """Process game mechanics after a volume is shelved."""
    from src.db.tables import LibrarianRow

    librarian = await session.get(LibrarianRow, librarian_id)
    old_rank = get_rank(librarian.total_xp) if librarian else "Page"

    total_xp = await award_shelve_xp(session, librarian_id)
    badges = await check_badges_after_shelve(session, librarian_id)

    new_rank = get_rank(total_xp)
    rank_changed = new_rank != old_rank

    return GameResult(
        xp_awarded=XP_SHELVE_VOLUME,
        xp_breakdown=[
            {"amount": XP_SHELVE_VOLUME, "reason": "Shelved a new volume"},
        ],
        total_xp=total_xp,
        rank=new_rank,
        rank_changed=rank_changed,
        new_rank=new_rank if rank_changed else None,
        badges_earned=badges,
    )


async def on_volume_reviewed(
    session: AsyncSession,
    librarian_id: int,
    volume_id: int,
    dewey_score_before: float,
) -> GameResult:
    """Process game mechanics after a volume is reviewed."""
    from src.db.tables import LibrarianRow

    # Create review record
    review = ReviewRow(
        volume_id=volume_id,
        librarian_id=librarian_id,
        reviewed_at=datetime.utcnow(),
        dewey_score_before=dewey_score_before,
    )
    session.add(review)

    librarian = await session.get(LibrarianRow, librarian_id)
    old_rank = get_rank(librarian.total_xp) if librarian else "Page"

    # Award XP (2x for overdue volumes)
    was_overdue = dewey_score_before <= DEWEY_OVERDUE
    review_amount = (
        XP_REVIEW_CURRENT * XP_REVIEW_OVERDUE_MULTIPLIER if was_overdue else XP_REVIEW_CURRENT
    )
    review_reason = (
        f"Reviewed an overdue volume ({XP_REVIEW_OVERDUE_MULTIPLIER}x bonus)"
        if was_overdue
        else "Reviewed a current volume"
    )
    xp_awarded = review_amount
    xp_breakdown = [{"amount": review_amount, "reason": review_reason}]
    total_xp = await award_review_xp(session, librarian_id, was_overdue)

    # Award rescue bonus for saving a volume from Overdue territory
    if was_overdue:
        await award_rescue_bonus(session, librarian_id)
        xp_awarded += XP_RESCUE_BONUS
        xp_breakdown.append({
            "amount": XP_RESCUE_BONUS,
            "reason": "Rescue bonus (saved from Overdue)",
        })

    # Update streak
    streak_info = await update_streak(session, librarian_id)
    streak_bonus = False
    if streak_info["is_new_day"]:
        await award_streak_bonus(session, librarian_id)
        xp_awarded += XP_DAILY_STREAK_BONUS
        total_xp += XP_DAILY_STREAK_BONUS
        xp_breakdown.append({"amount": XP_DAILY_STREAK_BONUS, "reason": "Daily streak bonus"})
        streak_bonus = True

    # Refresh total_xp from DB after all awards
    await session.flush()
    if librarian:
        await session.refresh(librarian)
        total_xp = librarian.total_xp

    # Check badges
    badges = await check_badges_after_review(session, librarian_id)

    new_rank = get_rank(total_xp)
    rank_changed = new_rank != old_rank

    return GameResult(
        xp_awarded=xp_awarded,
        xp_breakdown=xp_breakdown,
        total_xp=total_xp,
        rank=new_rank,
        rank_changed=rank_changed,
        new_rank=new_rank if rank_changed else None,
        badges_earned=badges,
        streak=streak_info["current_streak"],
        streak_bonus_awarded=streak_bonus,
    )
