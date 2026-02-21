"""Web POST routes for game actions (session-auth protected)."""

import json
from datetime import datetime

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.volumes import calculate_dewey_score
from src.auth.web_session import get_current_librarian_optional, get_current_librarian_required
from src.config.settings import settings
from src.db.engine import get_session
from src.db.tables import ReviewRow, ShelfRow, VolumeRow, volume_bookmarks
from src.errors.incidents import VolumeTooLarge
from src.game.engine import on_volume_reviewed, on_volume_shelved

router = APIRouter()
templates = Jinja2Templates(directory="templates")


def _game_trigger_header(game_result) -> dict[str, str]:
    """Build HX-Trigger header for game feedback toast."""
    event_data = {
        "xp_awarded": game_result.xp_awarded,
        "total_xp": game_result.total_xp,
        "rank": game_result.rank,
        "rank_changed": game_result.rank_changed,
        "new_rank": game_result.new_rank,
        "badges_earned": game_result.badges_earned,
        "streak": game_result.streak,
        "streak_bonus_awarded": game_result.streak_bonus_awarded,
    }
    return {"HX-Trigger": json.dumps({"gameEvent": event_data})}


@router.get("/shelves/create")
async def shelf_create_page(
    request: Request,
    session: AsyncSession = Depends(get_session),
):
    """Render shelf creation form."""
    user = await get_current_librarian_required(request, session)
    if isinstance(user, RedirectResponse):
        return user
    return templates.TemplateResponse("shelf_create.html", {
        "request": request,
        "current_user": user,
    })


@router.post("/shelves/create")
async def shelf_create_submit(
    request: Request,
    session: AsyncSession = Depends(get_session),
):
    """Process shelf creation."""
    user = await get_current_librarian_required(request, session)
    if isinstance(user, RedirectResponse):
        return user

    form = await request.form()
    name = form.get("name", "").strip()
    description = form.get("description", "").strip()

    if not name:
        return templates.TemplateResponse("shelf_create.html", {
            "request": request,
            "current_user": user,
            "error": "Shelf name is required.",
        })

    # Check duplicate
    existing = await session.execute(select(ShelfRow).where(ShelfRow.name == name))
    if existing.scalar_one_or_none():
        return templates.TemplateResponse("shelf_create.html", {
            "request": request,
            "current_user": user,
            "error": "A shelf with that name already exists.",
            "name": name,
            "description": description,
        })

    shelf = ShelfRow(
        name=name,
        description=description or None,
        created_by=user["id"],
    )
    session.add(shelf)
    await session.commit()
    await session.refresh(shelf)
    return RedirectResponse(url=f"/shelves/{shelf.id}", status_code=302)


@router.get("/volumes/create")
async def volume_create_page(
    request: Request,
    shelf_id: int | None = None,
    session: AsyncSession = Depends(get_session),
):
    """Render volume creation form."""
    user = await get_current_librarian_required(request, session)
    if isinstance(user, RedirectResponse):
        return user

    shelves_result = await session.execute(select(ShelfRow))
    shelves = shelves_result.scalars().all()

    return templates.TemplateResponse("volume_create.html", {
        "request": request,
        "current_user": user,
        "shelves": shelves,
        "selected_shelf_id": shelf_id,
    })


@router.post("/volumes/create")
async def volume_create_submit(
    request: Request,
    session: AsyncSession = Depends(get_session),
):
    """Process volume creation."""
    user = await get_current_librarian_required(request, session)
    if isinstance(user, RedirectResponse):
        return user

    form = await request.form()
    title = form.get("title", "").strip()
    content = form.get("content", "").strip()
    shelf_id = form.get("shelf_id", "")
    bookmarks_str = form.get("bookmarks", "").strip()

    shelves_result = await session.execute(select(ShelfRow))
    shelves = shelves_result.scalars().all()

    errors = []
    if not title:
        errors.append("Title is required.")
    if not content:
        errors.append("Content is required.")
    if not shelf_id:
        errors.append("Please select a shelf.")

    if errors:
        return templates.TemplateResponse("volume_create.html", {
            "request": request,
            "current_user": user,
            "shelves": shelves,
            "errors": errors,
            "title": title,
            "content": content,
            "selected_shelf_id": int(shelf_id) if shelf_id else None,
            "bookmarks": bookmarks_str,
        })

    # Check content size
    content_size_kb = len(content.encode("utf-8")) / 1024
    if content_size_kb > settings.max_volume_size_kb:
        return templates.TemplateResponse("volume_create.html", {
            "request": request,
            "current_user": user,
            "shelves": shelves,
            "errors": [f"Content exceeds maximum size of {settings.max_volume_size_kb}KB."],
            "title": title,
            "content": content,
            "selected_shelf_id": int(shelf_id),
            "bookmarks": bookmarks_str,
        })

    volume = VolumeRow(
        title=title,
        content=content,
        shelf_id=int(shelf_id),
        author_id=user["id"],
    )
    session.add(volume)
    await session.flush()

    # Add bookmarks
    if bookmarks_str:
        for tag in [t.strip() for t in bookmarks_str.split(",") if t.strip()]:
            await session.execute(volume_bookmarks.insert().values(volume_id=volume.id, bookmark=tag))

    await session.commit()
    await session.refresh(volume)

    # Trigger game mechanics
    game_result = await on_volume_shelved(session, user["id"], volume.id)
    await session.commit()

    return RedirectResponse(url=f"/volumes/{volume.id}", status_code=302)


@router.post("/volumes/{volume_id}/review")
async def review_volume_web(
    volume_id: int,
    request: Request,
    session: AsyncSession = Depends(get_session),
):
    """Review a volume from the web UI."""
    user = await get_current_librarian_required(request, session)
    if isinstance(user, RedirectResponse):
        return user

    volume = await session.get(VolumeRow, volume_id)
    if not volume:
        return RedirectResponse(url="/", status_code=302)

    dewey_score_before = calculate_dewey_score(volume.last_reviewed_at)
    volume.last_reviewed_at = datetime.utcnow()

    game_result = await on_volume_reviewed(session, user["id"], volume_id, dewey_score_before)
    await session.commit()
    await session.refresh(volume)

    # Check if this is an HTMX request
    if request.headers.get("HX-Request"):
        new_score = calculate_dewey_score(volume.last_reviewed_at)
        reviews_result = await session.execute(
            select(ReviewRow)
            .where(ReviewRow.volume_id == volume.id)
            .order_by(ReviewRow.reviewed_at.desc())
            .limit(20)
        )
        reviews = reviews_result.scalars().all()

        response = templates.TemplateResponse("partials/review_result.html", {
            "request": request,
            "current_user": user,
            "volume": volume,
            "dewey_score": round(new_score, 1),
            "reviews": reviews,
            "game_result": game_result,
        })
        response.headers.update(_game_trigger_header(game_result))
        return response

    return RedirectResponse(url=f"/volumes/{volume_id}", status_code=302)


@router.get("/search")
async def search_page(
    request: Request,
    q: str = "",
    session: AsyncSession = Depends(get_session),
):
    """Render search page with results."""
    current_user = await get_current_librarian_optional(request, session)
    results = []

    if q:
        from difflib import SequenceMatcher
        query_result = await session.execute(
            select(VolumeRow).where(VolumeRow.archived == False)  # noqa: E712
        )
        volumes = query_result.scalars().all()
        for v in volumes:
            title_score = SequenceMatcher(None, q.lower(), v.title.lower()).ratio()
            content_score = SequenceMatcher(None, q.lower(), v.content[:200].lower()).ratio() * 0.5
            score = max(title_score, content_score)
            if score >= 0.3 or q.lower() in v.title.lower() or q.lower() in v.content.lower():
                dewey = calculate_dewey_score(v.last_reviewed_at)
                excerpt = v.content[:150] + "..." if len(v.content) > 150 else v.content
                results.append({
                    "id": v.id,
                    "title": v.title,
                    "excerpt": excerpt,
                    "dewey_score": round(dewey, 1),
                    "relevance": round(max(score, 1.0 if q.lower() in v.title.lower() else score), 2),
                })
        results.sort(key=lambda x: x["relevance"], reverse=True)

    # If HTMX request, return just the results partial
    if request.headers.get("HX-Request"):
        return templates.TemplateResponse("partials/search_results.html", {
            "request": request,
            "results": results,
            "query": q,
        })

    return templates.TemplateResponse("search.html", {
        "request": request,
        "current_user": current_user,
        "results": results,
        "query": q,
    })
