"""How to Play route."""

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.web_session import get_current_librarian_optional
from src.db.engine import get_session
from src.web.templates import templates

router = APIRouter()


@router.get("/how-to-play")
async def how_to_play(
    request: Request,
    session: AsyncSession = Depends(get_session),
):
    """Render the How to Play page."""
    current_user = await get_current_librarian_optional(request, session)
    return templates.TemplateResponse(request, "how_to_play.html", {
        "request": request,
        "current_user": current_user,
    })
