"""How to Play route."""

from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/how-to-play")
async def how_to_play(request: Request):
    """Render the How to Play page."""
    return templates.TemplateResponse("how_to_play.html", {
        "request": request,
    })
