"""Shelf CRUD endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.volumes import calculate_dewey_score
from src.auth.library_card import verify_library_card
from src.db.engine import get_session
from src.db.tables import ShelfRow, VolumeRow
from src.models.shelf import ShelfCreate, ShelfListResponse, ShelfResponse, ShelfUpdate

router = APIRouter()


async def shelf_to_response(row: ShelfRow, session: AsyncSession) -> ShelfResponse:
    """Convert a ShelfRow to a ShelfResponse with volume stats."""
    count_result = await session.execute(
        select(func.count())
        .select_from(VolumeRow)
        .where(VolumeRow.shelf_id == row.id, VolumeRow.archived == False)  # noqa: E712
    )
    volume_count = count_result.scalar() or 0

    # Calculate average Dewey Score
    avg_dewey = 100.0
    if volume_count > 0:
        volumes_result = await session.execute(
            select(VolumeRow).where(
                VolumeRow.shelf_id == row.id, VolumeRow.archived == False  # noqa: E712
            )
        )
        volumes = volumes_result.scalars().all()
        scores = [calculate_dewey_score(v.last_reviewed_at) for v in volumes]
        avg_dewey = round(sum(scores) / len(scores), 1)

    return ShelfResponse(
        id=row.id,
        name=row.name,
        description=row.description,
        created_at=row.created_at,
        created_by=row.created_by,
        volume_count=volume_count,
        average_dewey_score=avg_dewey,
    )


@router.post("/", response_model=ShelfResponse, status_code=201)
async def create_shelf(
    body: ShelfCreate,
    session: AsyncSession = Depends(get_session),
    payload: dict = Depends(verify_library_card),
) -> ShelfResponse:
    """Create a new shelf in the library."""
    # Check for duplicate name
    existing = await session.execute(select(ShelfRow).where(ShelfRow.name == body.name))
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=409,
            detail="A volume with that title is already shelved in this section.",
        )

    shelf = ShelfRow(
        name=body.name,
        description=body.description,
        created_by=int(payload["sub"]),
    )
    session.add(shelf)
    await session.commit()
    await session.refresh(shelf)
    return await shelf_to_response(shelf, session)


@router.get("/", response_model=ShelfListResponse)
async def list_shelves(
    session: AsyncSession = Depends(get_session),
) -> ShelfListResponse:
    """Browse all shelves in the library."""
    result = await session.execute(select(ShelfRow))
    rows = result.scalars().all()

    items = [await shelf_to_response(row, session) for row in rows]
    return ShelfListResponse(items=items, total=len(items))


@router.get("/{shelf_id}", response_model=ShelfResponse)
async def get_shelf(
    shelf_id: int,
    session: AsyncSession = Depends(get_session),
) -> ShelfResponse:
    """Look up a specific shelf."""
    shelf = await session.get(ShelfRow, shelf_id)
    if not shelf:
        raise HTTPException(
            status_code=404,
            detail="That shelf isn't in our library. Check the catalog and try again.",
        )
    return await shelf_to_response(shelf, session)


@router.patch("/{shelf_id}", response_model=ShelfResponse)
async def update_shelf(
    shelf_id: int,
    body: ShelfUpdate,
    session: AsyncSession = Depends(get_session),
) -> ShelfResponse:
    """Update an existing shelf."""
    shelf = await session.get(ShelfRow, shelf_id)
    if not shelf:
        raise HTTPException(
            status_code=404,
            detail="That shelf isn't in our library. Check the catalog and try again.",
        )

    update_data = body.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(shelf, key, value)

    await session.commit()
    await session.refresh(shelf)
    return await shelf_to_response(shelf, session)


@router.delete("/{shelf_id}", status_code=204)
async def delete_shelf(
    shelf_id: int,
    session: AsyncSession = Depends(get_session),
    payload: dict = Depends(verify_library_card),
) -> None:
    """Remove a shelf and all its volumes."""
    shelf = await session.get(ShelfRow, shelf_id)
    if not shelf:
        raise HTTPException(
            status_code=404,
            detail="That shelf isn't in our library. Check the catalog and try again.",
        )

    await session.delete(shelf)
    await session.commit()
