"""Settings page routes."""

from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

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
    return templates.TemplateResponse("settings.html", {
        "request": request,
        "current_user": user,
        "avatar_choices": get_avatar_choices(),
    })


@router.post("/settings/avatar")
async def update_avatar(
    request: Request,
    session: AsyncSession = Depends(get_session),
):
    """Update the current user's avatar."""
    user = await get_current_librarian_required(request, session)
    if isinstance(user, RedirectResponse):
        return user

    form = await request.form()
    avatar_id = form.get("avatar_id", "avatar_01")
    if avatar_id not in AVATAR_CATALOG:
        avatar_id = "avatar_01"

    librarian = await session.get(LibrarianRow, user["id"])
    if librarian:
        librarian.avatar_id = avatar_id
        await session.commit()

    return RedirectResponse(url="/settings", status_code=302)
