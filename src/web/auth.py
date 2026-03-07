"""Web authentication routes (login, register, logout)."""

import re

import bcrypt
from fastapi import APIRouter, Depends, Request
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.web_session import get_current_librarian_optional, login_librarian, logout_librarian
from src.db.engine import get_session
from src.db.tables import LibrarianRow
from src.game.avatars import get_avatar_choices, AVATAR_CATALOG
from src.web.templates import templates

router = APIRouter()

PASSWORD_PATTERN = re.compile(
    r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,72}$"
)


@router.get("/login")
async def login_page(
    request: Request,
    session: AsyncSession = Depends(get_session),
):
    """Render the login page."""
    user = await get_current_librarian_optional(request, session)
    if user:
        return RedirectResponse(url="/", status_code=302)
    return templates.TemplateResponse("login.html", {
        "request": request,
        "current_user": None,
    })


@router.post("/login")
async def login_submit(
    request: Request,
    session: AsyncSession = Depends(get_session),
):
    """Process login form submission."""
    form = await request.form()
    username = form.get("username", "").strip()
    password = form.get("password", "")

    if not username or not password:
        return templates.TemplateResponse("login.html", {
            "request": request,
            "current_user": None,
            "error": "Username and password are required.",
        })

    result = await login_librarian(request, session, username, password)
    if not result:
        return templates.TemplateResponse("login.html", {
            "request": request,
            "current_user": None,
            "error": "Invalid username or password.",
        })

    return RedirectResponse(url="/", status_code=302)


@router.get("/register")
async def register_page(
    request: Request,
    session: AsyncSession = Depends(get_session),
):
    """Render the registration page."""
    user = await get_current_librarian_optional(request, session)
    if user:
        return RedirectResponse(url="/", status_code=302)
    return templates.TemplateResponse("register.html", {
        "request": request,
        "current_user": None,
        "avatar_choices": get_avatar_choices(),
    })


@router.post("/register")
async def register_submit(
    request: Request,
    session: AsyncSession = Depends(get_session),
):
    """Process registration form submission."""
    form = await request.form()
    username = form.get("username", "").strip()
    email = form.get("email", "").strip()
    password = form.get("password", "")
    confirm = form.get("confirm_password", "")
    avatar_id = form.get("avatar_id", "avatar_01").strip()

    # Validate avatar selection
    if avatar_id not in AVATAR_CATALOG:
        avatar_id = "avatar_01"

    errors = []
    if not username or len(username) < 3:
        errors.append("Username must be at least 3 characters.")
    if not email or "@" not in email:
        errors.append("A valid email is required.")
    if not PASSWORD_PATTERN.match(password):
        errors.append("Password must be 8–72 chars with uppercase, lowercase, digit, and special character (@$!%*?&).")
    if password != confirm:
        errors.append("Passwords do not match.")

    if errors:
        return templates.TemplateResponse("register.html", {
            "request": request,
            "current_user": None,
            "errors": errors,
            "username": username,
            "email": email,
            "avatar_choices": get_avatar_choices(),
            "selected_avatar": avatar_id,
        })

    # Check existing username/email
    existing = await session.execute(
        select(LibrarianRow).where(LibrarianRow.username == username)
    )
    if existing.scalar_one_or_none():
        return templates.TemplateResponse("register.html", {
            "request": request,
            "current_user": None,
            "errors": ["That username is already taken."],
            "username": username,
            "email": email,
            "avatar_choices": get_avatar_choices(),
            "selected_avatar": avatar_id,
        })

    existing_email = await session.execute(
        select(LibrarianRow).where(LibrarianRow.email == email)
    )
    if existing_email.scalar_one_or_none():
        return templates.TemplateResponse("register.html", {
            "request": request,
            "current_user": None,
            "errors": ["That email is already registered."],
            "username": username,
            "email": email,
            "avatar_choices": get_avatar_choices(),
            "selected_avatar": avatar_id,
        })

    hashed_password = await run_in_threadpool(
        lambda: bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    )
    librarian = LibrarianRow(
        username=username,
        email=email,
        hashed_password=hashed_password,
        avatar_id=avatar_id,
    )
    session.add(librarian)
    await session.commit()
    await session.refresh(librarian)

    # Auto-login after registration
    await login_librarian(request, session, username, password)
    return RedirectResponse(url="/", status_code=302)


@router.post("/logout")
async def logout(request: Request):
    """Log out and redirect to home."""
    logout_librarian(request)
    return RedirectResponse(url="/", status_code=302)
