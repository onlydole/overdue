"""Settings page routes."""

from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.library_card import create_library_card
from src.auth.web_session import get_current_librarian_required
from src.db.engine import get_session
from src.db.tables import LibrarianRow
from src.game.avatars import AVATAR_CATALOG, get_avatar_choices
from src.web.templates import templates

router = APIRouter()


@router.get("/settings")
async def settings_page(
    request: Request,
    session: AsyncSession = Depends(get_session),
):
    """Render the settings page."""
    user = await get_current_librarian_required(request, session)
    if isinstance(user, RedirectResponse):
        return user

    librarian = await session.get(LibrarianRow, user["id"])
    if librarian is None:
        return RedirectResponse(url="/login", status_code=302)

    avatar_id = librarian.avatar_id if librarian.avatar_id in AVATAR_CATALOG else "avatar_01"
    renewed_on = request.session.get("card_renewed_on") or librarian.created_at.strftime("%Y-%m-%d")
    card_form = {
        "username": librarian.username,
        "email": librarian.email,
        "role": librarian.role,
        "avatar_id": avatar_id,
    }
    card_meta = {
        "card_number": f"CARD-{librarian.id:05d}",
        "member_since": librarian.created_at.strftime("%Y-%m-%d"),
        "expires_on": (librarian.created_at + timedelta(days=365 * 3)).strftime("%Y-%m-%d"),
        "renewed_on": renewed_on,
    }
    return templates.TemplateResponse("settings.html", {
        "request": request,
        "current_user": user,
        "avatar_choices": get_avatar_choices(),
        "card_form": card_form,
        "card_meta": card_meta,
        "form_errors": [],
        "saved": request.query_params.get("saved") == "1",
    })


@router.post("/settings/card")
@router.post("/settings/avatar")
async def update_avatar(
    request: Request,
    session: AsyncSession = Depends(get_session),
):
    """Update editable library card fields for the current librarian."""
    user = await get_current_librarian_required(request, session)
    if isinstance(user, RedirectResponse):
        return user

    librarian = await session.get(LibrarianRow, user["id"])
    if librarian is None:
        return RedirectResponse(url="/login", status_code=302)

    form = await request.form()
    username = str(form.get("username", "")).strip()
    email = str(form.get("email", "")).strip().lower()
    avatar_id = str(form.get("avatar_id", "avatar_01"))

    errors: list[str] = []
    if len(username) < 3:
        errors.append("Username must be at least 3 characters.")
    if len(username) > 100:
        errors.append("Username must be 100 characters or fewer.")
    if not email or "@" not in email:
        errors.append("A valid email is required.")

    if avatar_id not in AVATAR_CATALOG:
        avatar_id = "avatar_01"

    if username != librarian.username:
        existing_username = await session.execute(
            select(LibrarianRow.id).where(
                LibrarianRow.username == username,
                LibrarianRow.id != librarian.id,
            ),
        )
        if existing_username.scalar_one_or_none():
            errors.append("That username is already taken.")

    if email != librarian.email:
        existing_email = await session.execute(
            select(LibrarianRow.id).where(
                LibrarianRow.email == email,
                LibrarianRow.id != librarian.id,
            ),
        )
        if existing_email.scalar_one_or_none():
            errors.append("That email is already registered.")

    if errors:
        renewed_on = request.session.get("card_renewed_on") or librarian.created_at.strftime("%Y-%m-%d")
        card_form = {
            "username": username or librarian.username,
            "email": email or librarian.email,
            "role": librarian.role,
            "avatar_id": avatar_id,
        }
        card_meta = {
            "card_number": f"CARD-{librarian.id:05d}",
            "member_since": librarian.created_at.strftime("%Y-%m-%d"),
            "expires_on": (librarian.created_at + timedelta(days=365 * 3)).strftime("%Y-%m-%d"),
            "renewed_on": renewed_on,
        }
        return templates.TemplateResponse("settings.html", {
            "request": request,
            "current_user": user,
            "avatar_choices": get_avatar_choices(),
            "card_form": card_form,
            "card_meta": card_meta,
            "form_errors": errors,
            "saved": False,
        }, status_code=400)

    librarian.username = username
    librarian.email = email
    librarian.avatar_id = avatar_id
    await session.commit()

    request.session["token"] = create_library_card(
        librarian_id=librarian.id,
        username=librarian.username,
        role=librarian.role,
    )
    request.session["card_renewed_on"] = datetime.utcnow().strftime("%Y-%m-%d")

    return RedirectResponse(url="/settings?saved=1", status_code=302)
