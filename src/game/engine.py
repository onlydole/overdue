"""Game action orchestrator -- wires XP, badges, and streaks together."""

from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from src.api.volumes import calculate_dewey_score
from src.config.defaults import DEWEY_OVERDUE
from src.db.tables import ReviewRow, VolumeRow
from src.game.badges import check_badges_after_review, check_badges_after_shelve
from src.game.streaks import update_streak
from src.game.xp import award_review_xp, award_shelve_xp, award_streak_bonus, get_rank
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
        xp_awarded=10,
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
    xp_awarded = 10 if was_overdue else 5
    total_xp = await award_review_xp(session, librarian_id, was_overdue)

    # Update streak
    streak_info = await update_streak(session, librarian_id)
    streak_bonus = False
    if streak_info["is_new_day"]:
        await award_streak_bonus(session, librarian_id)
        xp_awarded += 15
        total_xp += 15
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
        total_xp=total_xp,
        rank=new_rank,
        rank_changed=rank_changed,
        new_rank=new_rank if rank_changed else None,
        badges_earned=badges,
        streak=streak_info["current_streak"],
        streak_bonus_awarded=streak_bonus,
    )
