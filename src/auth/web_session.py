"""Web session utilities for cookie-based browser auth."""

import bcrypt
import jwt
from fastapi import Request
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import RedirectResponse
from jwt.exceptions import PyJWTError as JWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.library_card import ALGORITHM, create_library_card
from src.config.settings import settings
from src.db.tables import LibrarianRow


async def get_current_librarian_optional(
    request: Request,
    session: AsyncSession,
) -> dict | None:
    """Return librarian info from session cookie, or None if not logged in."""
    token = request.session.get("token")
    if not token:
        return None
    try:
        payload = jwt.decode(token, settings.signing_secret_key, algorithms=[ALGORITHM])
        librarian_id = payload.get("sub")
        if not librarian_id:
            return None
        librarian = await session.get(LibrarianRow, int(librarian_id))
        if not librarian:
            return None
        return {
            "id": librarian.id,
            "username": librarian.username,
            "role": librarian.role,
            "total_xp": librarian.total_xp,
            "avatar_id": librarian.avatar_id,
        }
    except JWTError:
        request.session.clear()
        return None


async def get_current_librarian_required(
    request: Request,
    session: AsyncSession,
) -> dict | RedirectResponse:
    """Return librarian info or redirect to login."""
    user = await get_current_librarian_optional(request, session)
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    return user


async def login_librarian(
    request: Request,
    session: AsyncSession,
    username: str,
    password: str,
) -> dict | None:
    """Verify credentials and store JWT in session. Returns librarian dict or None."""
    result = await session.execute(
        select(LibrarianRow).where(LibrarianRow.username == username)
    )
    librarian = result.scalar_one_or_none()

    if not librarian:
        return None

    try:
        valid = await run_in_threadpool(
            bcrypt.checkpw, password.encode(), librarian.hashed_password.encode()
        )
    except ValueError:
        return None

    if not valid:
        return None

    token = create_library_card(
        librarian_id=librarian.id,
        username=librarian.username,
        role=librarian.role,
    )
    request.session["token"] = token
    return {
        "id": librarian.id,
        "username": librarian.username,
        "role": librarian.role,
    }


def logout_librarian(request: Request) -> None:
    """Clear the session."""
    request.session.clear()
