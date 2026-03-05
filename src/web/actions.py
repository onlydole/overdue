"""Web POST routes for game actions (session-auth protected)."""

import json
import random
from datetime import datetime

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.volumes import calculate_dewey_score
from src.auth.web_session import get_current_librarian_optional, get_current_librarian_required
from src.config.settings import settings
from src.db.engine import get_session
from src.web.volumes import REVIEWS_PER_PAGE
from src.db.tables import ReviewRow, ShelfRow, VolumeRow, volume_bookmarks
from src.errors.incidents import VolumeTooLarge
from src.game.engine import on_volume_reviewed, on_volume_shelved
from src.models.game import GameResult
from src.web.templates import templates

router = APIRouter()


def _game_trigger_header(game_result) -> dict[str, str]:
    """Build HX-Trigger header for game feedback toast."""
    event_data = {
        "xp_awarded": game_result.xp_awarded,
        "xp_breakdown": game_result.xp_breakdown,
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
    elif len(title) > 60:
        errors.append("Title must be 60 characters or fewer.")
    if not content:
        errors.append("Content is required.")
    if not shelf_id:
        errors.append("Please select a shelf.")

    if errors:
        try:
            selected_shelf = int(shelf_id) if shelf_id else None
        except (ValueError, TypeError):
            selected_shelf = None
        return templates.TemplateResponse("volume_create.html", {
            "request": request,
            "current_user": user,
            "shelves": shelves,
            "errors": errors,
            "title": title,
            "content": content,
            "selected_shelf_id": selected_shelf,
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
        spine_seed=random.randint(0, 9999),
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

    if dewey_score_before >= 99.9:
        # Volume is already pristine; no action taken
        from src.game.xp import get_rank
        current_rank = get_rank(user["total_xp"])
        game_result = GameResult(
            xp_awarded=0,
            xp_breakdown=[],
            total_xp=user["total_xp"],
            rank=current_rank,
            rank_changed=False,
            new_rank=None,
            badges_earned=[],
            streak=0,
            streak_bonus_awarded=False
        )
    else:
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
            .limit(REVIEWS_PER_PAGE + 1)
        )
        reviews = list(reviews_result.scalars().all())
        has_more_reviews = len(reviews) > REVIEWS_PER_PAGE
        reviews = reviews[:REVIEWS_PER_PAGE]
        count_result = await session.execute(
            select(func.count()).select_from(ReviewRow)
            .where(ReviewRow.volume_id == volume.id)
        )
        total_reviews = count_result.scalar() or 0

        # Find next overdue volume to suggest
        next_volume = None

        # First: check siblings on the same shelf
        siblings_result = await session.execute(
            select(VolumeRow).where(
                VolumeRow.shelf_id == volume.shelf_id,
                VolumeRow.id != volume.id,
                VolumeRow.archived == False,  # noqa: E712
            )
        )
        siblings = siblings_result.scalars().all()
        candidates = []
        for v in siblings:
            score = calculate_dewey_score(v.last_reviewed_at)
            if score < 75:
                candidates.append({"id": v.id, "title": v.title, "dewey_score": round(score, 1)})
        candidates.sort(key=lambda c: c["dewey_score"])

        if candidates:
            next_volume = candidates[0]
        else:
            # Fallback: check all volumes authored by this user
            all_result = await session.execute(
                select(VolumeRow).where(
                    VolumeRow.author_id == user["id"],
                    VolumeRow.id != volume.id,
                    VolumeRow.archived == False,  # noqa: E712
                )
            )
            all_volumes = all_result.scalars().all()
            candidates = []
            for v in all_volumes:
                score = calculate_dewey_score(v.last_reviewed_at)
                if score < 75:
                    candidates.append({"id": v.id, "title": v.title, "dewey_score": round(score, 1)})
            candidates.sort(key=lambda c: c["dewey_score"])
            if candidates:
                next_volume = candidates[0]

        response = templates.TemplateResponse("partials/review_result.html", {
            "request": request,
            "current_user": user,
            "volume": volume,
            "dewey_score": round(new_score, 1),
            "reviews": reviews,
            "review_page": 1,
            "has_more_reviews": has_more_reviews,
            "total_reviews": total_reviews,
            "game_result": game_result,
            "next_volume": next_volume,
        })
        response.headers.update(_game_trigger_header(game_result))
        return response

    return RedirectResponse(url=f"/volumes/{volume_id}", status_code=302)
