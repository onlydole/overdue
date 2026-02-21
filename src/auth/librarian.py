"""Librarian registration, login, and profile."""

import re
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query
from passlib.context import CryptContext
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.library_card import create_library_card, verify_library_card
from src.config.settings import settings
from src.db.engine import get_session
from src.db.tables import BadgeRow, LibrarianRow, StreakRow
from src.game.badges import get_earned_badges
from src.game.streaks import get_streak
from src.game.xp import get_next_rank, get_rank, get_recent_awards
from src.models.librarian import LibrarianCreate, LibrarianLogin, LibrarianResponse, LibraryCard

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

PASSWORD_PATTERN = re.compile(
    r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$"
)


@router.post("/register", response_model=LibrarianResponse, status_code=201)
async def register(
    body: LibrarianCreate,
    session: AsyncSession = Depends(get_session),
) -> LibrarianResponse:
    """Register a new librarian."""
    # Validate password complexity
    if not PASSWORD_PATTERN.match(body.password):
        raise HTTPException(
            status_code=422,
            detail="Password must be at least 8 characters with uppercase, lowercase, digit, and special character.",
        )

    # Check for existing username
    existing = await session.execute(
        select(LibrarianRow).where(LibrarianRow.username == body.username)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="That username is already taken.")

    # Check for existing email
    existing_email = await session.execute(
        select(LibrarianRow).where(LibrarianRow.email == body.email)
    )
    if existing_email.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="That email is already registered.")

    librarian = LibrarianRow(
        username=body.username,
        email=body.email,
        hashed_password=pwd_context.hash(body.password),
    )
    session.add(librarian)
    await session.commit()
    await session.refresh(librarian)
    return LibrarianResponse.model_validate(librarian)


@router.post("/login", response_model=LibraryCard)
async def login(
    body: LibrarianLogin,
    session: AsyncSession = Depends(get_session),
) -> LibraryCard:
    """Log in and receive a library card (JWT token)."""
    result = await session.execute(
        select(LibrarianRow).where(LibrarianRow.username == body.username)
    )
    librarian = result.scalar_one_or_none()

    if not librarian or not pwd_context.verify(body.password, librarian.hashed_password):
        raise HTTPException(
            status_code=401,
            detail="You'll need a library card to access the stacks.",
        )

    token = create_library_card(
        librarian_id=librarian.id,
        username=librarian.username,
        role=librarian.role,
    )
    return LibraryCard(
        access_token=token,
        expires_in=settings.token_expiry_minutes * 60,
    )


@router.post("/refresh", response_model=LibraryCard)
async def refresh_token(
    session: AsyncSession = Depends(get_session),
    payload: dict = Depends(verify_library_card),
) -> LibraryCard:
    """Refresh a library card before it expires."""
    librarian_id = int(payload["sub"])
    librarian = await session.get(LibrarianRow, librarian_id)
    if not librarian:
        raise HTTPException(status_code=404, detail="Librarian not found.")

    token = create_library_card(
        librarian_id=librarian.id,
        username=librarian.username,
        role=librarian.role,
    )
    return LibraryCard(
        access_token=token,
        expires_in=settings.token_expiry_minutes * 60,
    )


@router.get("/me/xp")
async def get_my_xp(
    session: AsyncSession = Depends(get_session),
    payload: dict = Depends(verify_library_card),
) -> dict:
    """Get the current librarian's XP summary."""
    librarian_id = int(payload["sub"])
    librarian = await session.get(LibrarianRow, librarian_id)
    if not librarian:
        raise HTTPException(status_code=404, detail="Librarian not found.")

    next_rank, xp_to_next = get_next_rank(librarian.total_xp)
    recent = await get_recent_awards(session, librarian_id)

    return {
        "total_xp": librarian.total_xp,
        "rank": get_rank(librarian.total_xp),
        "next_rank": next_rank,
        "xp_to_next_rank": xp_to_next,
        "recent_awards": recent,
    }


@router.get("/me/badges")
async def get_my_badges(
    session: AsyncSession = Depends(get_session),
    payload: dict = Depends(verify_library_card),
) -> dict:
    """Get the current librarian's earned badges."""
    librarian_id = int(payload["sub"])
    badges = await get_earned_badges(session, librarian_id)
    return {"badges": badges, "total": len(badges)}


@router.get("/me/streak")
async def get_my_streak(
    session: AsyncSession = Depends(get_session),
    payload: dict = Depends(verify_library_card),
) -> dict:
    """Get the current librarian's review streak."""
    librarian_id = int(payload["sub"])
    return await get_streak(session, librarian_id)


@router.get("/leaderboard")
async def get_leaderboard(
    session: AsyncSession = Depends(get_session),
    limit: int = 10,
    timeframe: str = Query("all-time", description="Filter: week, month, or all-time"),
    sort_by: str = Query("xp", description="Sort by: xp or streak"),
) -> dict:
    """Get the top librarians by pages read or streak length."""
    from src.db.tables import XPLedgerRow

    if timeframe == "week":
        cutoff = datetime.utcnow() - timedelta(weeks=1)
    elif timeframe == "month":
        cutoff = datetime.utcnow() - timedelta(days=30)
    else:
        cutoff = None

    if sort_by == "streak":
        # Sort by current streak
        result = await session.execute(
            select(LibrarianRow)
            .join(StreakRow, StreakRow.librarian_id == LibrarianRow.id, isouter=True)
            .order_by(func.coalesce(StreakRow.current_streak, 0).desc())
            .limit(limit)
        )
    elif cutoff:
        # Sort by XP earned in timeframe
        subq = (
            select(
                XPLedgerRow.librarian_id,
                func.sum(XPLedgerRow.amount).label("period_xp"),
            )
            .where(XPLedgerRow.created_at >= cutoff)
            .group_by(XPLedgerRow.librarian_id)
            .subquery()
        )
        result = await session.execute(
            select(LibrarianRow)
            .join(subq, subq.c.librarian_id == LibrarianRow.id)
            .order_by(subq.c.period_xp.desc())
            .limit(limit)
        )
    else:
        result = await session.execute(
            select(LibrarianRow)
            .order_by(LibrarianRow.total_xp.desc())
            .limit(limit)
        )

    librarians = result.scalars().all()

    entries = []
    for i, lib in enumerate(librarians, 1):
        badge_count_result = await session.execute(
            select(func.count()).select_from(BadgeRow).where(BadgeRow.librarian_id == lib.id)
        )
        badge_count = badge_count_result.scalar() or 0

        streak_result = await session.execute(
            select(StreakRow).where(StreakRow.librarian_id == lib.id)
        )
        streak = streak_result.scalar_one_or_none()

        entries.append({
            "rank_position": i,
            "username": lib.username,
            "total_xp": lib.total_xp,
            "librarian_rank": get_rank(lib.total_xp),
            "badge_count": badge_count,
            "current_streak": streak.current_streak if streak else 0,
        })

    return {
        "entries": entries,
        "total_librarians": len(entries),
        "timeframe": timeframe,
        "sort_by": sort_by,
    }
