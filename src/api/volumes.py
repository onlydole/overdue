"""Volume CRUD endpoints."""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.library_card import verify_library_card
from src.config.defaults import DEWEY_DECAY_RATE, DEWEY_LOST, DEWEY_PRISTINE
from src.config.settings import settings
from src.db.engine import get_session
from src.errors.incidents import VolumeTooLarge
from src.db.tables import ShelfRow, VolumeRow, volume_bookmarks
from src.models.volume import VolumeCreate, VolumeListResponse, VolumeResponse, VolumeUpdate

router = APIRouter()


def calculate_dewey_score(last_reviewed_at: datetime) -> float:
    """Calculate the current Dewey Score based on time since last review."""
    days_elapsed = (datetime.utcnow() - last_reviewed_at).total_seconds() / 86400
    score = DEWEY_PRISTINE - (days_elapsed * DEWEY_DECAY_RATE)
    return max(score, DEWEY_LOST)


def volume_to_response(row: VolumeRow, bookmarks: list[str]) -> VolumeResponse:
    """Convert a VolumeRow to a VolumeResponse with calculated Dewey Score."""
    return VolumeResponse(
        id=row.id,
        title=row.title,
        content=row.content,
        shelf_id=row.shelf_id,
        author_id=row.author_id,
        bookmarks=bookmarks,
        dewey_score=round(calculate_dewey_score(row.last_reviewed_at), 1),
        created_at=row.created_at,
        updated_at=row.updated_at,
        last_reviewed_at=row.last_reviewed_at,
        archived=row.archived,
    )


@router.post("/", response_model=VolumeResponse, status_code=201)
async def create_volume(
    body: VolumeCreate,
    session: AsyncSession = Depends(get_session),
    payload: dict = Depends(verify_library_card),
) -> VolumeResponse:
    """Shelve a new volume in the library."""
    # Check volume size
    content_size_kb = len(body.content.encode("utf-8")) / 1024
    if content_size_kb > settings.max_volume_size_kb:
        raise VolumeTooLarge(max_size_kb=settings.max_volume_size_kb)

    # Verify shelf exists
    shelf = await session.get(ShelfRow, body.shelf_id)
    if not shelf:
        raise HTTPException(status_code=404, detail="That shelf isn't in our library. Check the catalog and try again.")

    volume = VolumeRow(
        title=body.title,
        content=body.content,
        shelf_id=body.shelf_id,
        author_id=int(payload["sub"]),
    )
    session.add(volume)
    await session.flush()

    # Add bookmarks
    for tag in body.bookmarks:
        await session.execute(volume_bookmarks.insert().values(volume_id=volume.id, bookmark=tag))

    await session.commit()
    await session.refresh(volume)
    return volume_to_response(volume, body.bookmarks)


@router.get("/", response_model=VolumeListResponse)
async def list_volumes(
    page: int = 1,
    per_page: int = 20,
    shelf_id: int | None = None,
    session: AsyncSession = Depends(get_session),
) -> VolumeListResponse:
    """Browse all volumes in the library."""
    query = select(VolumeRow).where(VolumeRow.archived == False)  # noqa: E712
    if shelf_id:
        query = query.where(VolumeRow.shelf_id == shelf_id)

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total = (await session.execute(count_query)).scalar() or 0

    # Paginate
    query = query.offset((page - 1) * per_page).limit(per_page)
    result = await session.execute(query)
    rows = result.scalars().all()

    items = []
    for row in rows:
        bm_result = await session.execute(
            select(volume_bookmarks.c.bookmark).where(volume_bookmarks.c.volume_id == row.id)
        )
        bookmarks = [b for (b,) in bm_result]
        items.append(volume_to_response(row, bookmarks))

    return VolumeListResponse(items=items, total=total, page=page, per_page=per_page)


@router.get("/{volume_id}", response_model=VolumeResponse)
async def get_volume(
    volume_id: int,
    session: AsyncSession = Depends(get_session),
) -> VolumeResponse:
    """Look up a specific volume."""
    volume = await session.get(VolumeRow, volume_id)
    if not volume:
        raise HTTPException(
            status_code=404,
            detail="That volume isn't on any of our shelves. Check the catalog and try again.",
        )

    bm_result = await session.execute(
        select(volume_bookmarks.c.bookmark).where(volume_bookmarks.c.volume_id == volume.id)
    )
    bookmarks = [b for (b,) in bm_result]
    return volume_to_response(volume, bookmarks)


@router.patch("/{volume_id}", response_model=VolumeResponse)
async def update_volume(
    volume_id: int,
    body: VolumeUpdate,
    session: AsyncSession = Depends(get_session),
    payload: dict = Depends(verify_library_card),
) -> VolumeResponse:
    """Update an existing volume."""
    volume = await session.get(VolumeRow, volume_id)
    if not volume:
        raise HTTPException(
            status_code=404,
            detail="That volume isn't on any of our shelves. Check the catalog and try again.",
        )

    update_data = body.model_dump(exclude_unset=True)
    bookmarks_update = update_data.pop("bookmarks", None)

    for key, value in update_data.items():
        setattr(volume, key, value)

    if bookmarks_update is not None:
        await session.execute(
            volume_bookmarks.delete().where(volume_bookmarks.c.volume_id == volume_id)
        )
        for tag in bookmarks_update:
            await session.execute(
                volume_bookmarks.insert().values(volume_id=volume_id, bookmark=tag)
            )

    await session.commit()
    await session.refresh(volume)

    bm_result = await session.execute(
        select(volume_bookmarks.c.bookmark).where(volume_bookmarks.c.volume_id == volume.id)
    )
    bookmarks = [b for (b,) in bm_result]
    return volume_to_response(volume, bookmarks)


@router.delete("/{volume_id}", status_code=204)
async def archive_volume(
    volume_id: int,
    session: AsyncSession = Depends(get_session),
    payload: dict = Depends(verify_library_card),
) -> None:
    """Archive a volume (soft delete)."""
    volume = await session.get(VolumeRow, volume_id)
    if not volume:
        raise HTTPException(
            status_code=404,
            detail="That volume isn't on any of our shelves. Check the catalog and try again.",
        )

    volume.archived = True
    await session.commit()


@router.post("/{volume_id}/review", response_model=VolumeResponse)
async def review_volume(
    volume_id: int,
    session: AsyncSession = Depends(get_session),
    payload: dict = Depends(verify_library_card),
) -> VolumeResponse:
    """Review a volume, resetting its Dewey Score to pristine."""
    volume = await session.get(VolumeRow, volume_id)
    if not volume:
        raise HTTPException(
            status_code=404,
            detail="That volume isn't on any of our shelves. Check the catalog and try again.",
        )

    volume.last_reviewed_at = datetime.utcnow()
    await session.commit()
    await session.refresh(volume)

    bm_result = await session.execute(
        select(volume_bookmarks.c.bookmark).where(volume_bookmarks.c.volume_id == volume.id)
    )
    bookmarks = [b for (b,) in bm_result]
    return volume_to_response(volume, bookmarks)
