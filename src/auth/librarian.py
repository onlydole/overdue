"""Librarian registration and login."""

from fastapi import APIRouter, Depends, HTTPException
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.library_card import create_library_card
from src.config.settings import settings
from src.db.engine import get_session
from src.db.tables import LibrarianRow
from src.models.librarian import LibrarianCreate, LibrarianLogin, LibrarianResponse, LibraryCard

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@router.post("/register", response_model=LibrarianResponse, status_code=201)
async def register(
    body: LibrarianCreate,
    session: AsyncSession = Depends(get_session),
) -> LibrarianResponse:
    """Register a new librarian."""
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
