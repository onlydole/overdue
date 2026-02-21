"""Shelf browsing routes."""

from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.volumes import calculate_dewey_score
from src.auth.web_session import get_current_librarian_optional
from src.db.engine import get_session
from src.db.tables import ShelfRow, VolumeRow

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/shelves")
async def browse_shelves(
    request: Request,
    session: AsyncSession = Depends(get_session),
):
    current_user = await get_current_librarian_optional(request, session)
    """Render the shelf browsing page."""
    result = await session.execute(select(ShelfRow))
    shelves = result.scalars().all()

    shelf_data = []
    for shelf in shelves:
        vol_result = await session.execute(
            select(VolumeRow).where(
                VolumeRow.shelf_id == shelf.id,
                VolumeRow.archived == False,  # noqa: E712
            )
        )
        volumes = vol_result.scalars().all()
        volume_count = len(volumes)
        avg_dewey = 100.0
        if volumes:
            scores = [calculate_dewey_score(v.last_reviewed_at) for v in volumes]
            avg_dewey = sum(scores) / len(scores)

        shelf_data.append({
            "id": shelf.id,
            "name": shelf.name,
            "description": shelf.description,
            "volume_count": volume_count,
            "average_dewey": round(avg_dewey, 1),
        })

    return templates.TemplateResponse("shelves.html", {
        "request": request,
        "current_user": current_user,
        "shelves": shelf_data,
    })


@router.get("/shelves/{shelf_id}")
async def shelf_detail(
    shelf_id: int,
    request: Request,
    session: AsyncSession = Depends(get_session),
):
    """Render a shelf detail page with its volumes."""
    current_user = await get_current_librarian_optional(request, session)
    shelf = await session.get(ShelfRow, shelf_id)
    if not shelf:
        return templates.TemplateResponse("shelves.html", {
            "request": request,
            "current_user": current_user,
            "shelves": [],
            "error": "Shelf not found",
        })

    vol_result = await session.execute(
        select(VolumeRow).where(
            VolumeRow.shelf_id == shelf_id,
            VolumeRow.archived == False,  # noqa: E712
        )
    )
    volumes = vol_result.scalars().all()

    volume_data = []
    for v in volumes:
        score = calculate_dewey_score(v.last_reviewed_at)
        volume_data.append({
            "id": v.id,
            "title": v.title,
            "dewey_score": round(score, 1),
            "last_reviewed_at": v.last_reviewed_at,
        })

    return templates.TemplateResponse("shelf_detail.html", {
        "request": request,
        "current_user": current_user,
        "shelf": shelf,
        "volumes": volume_data,
    })
