"""Bulletin (webhook) subscription endpoints."""

import hashlib
import hmac
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.library_card import verify_library_card
from src.config.settings import settings
from src.db.engine import get_session
from src.db.tables import BulletinRow
from src.models.bulletin import BulletinCreate, BulletinListResponse, BulletinResponse

router = APIRouter()

VALID_EVENTS = [
    "volume.created",
    "volume.reviewed",
    "volume.archived",
    "shelf.created",
    "librarian.ranked_up",
    "badge.earned",
]


@router.post("/", response_model=BulletinResponse, status_code=201)
async def create_bulletin(
    body: BulletinCreate,
    session: AsyncSession = Depends(get_session),
    payload: dict = Depends(verify_library_card),
) -> BulletinResponse:
    """Subscribe to webhook notifications."""
    # Validate events
    invalid = [e for e in body.events if e not in VALID_EVENTS]
    if invalid:
        raise HTTPException(
            status_code=422,
            detail=f"Invalid event types: {', '.join(invalid)}. Valid events: {', '.join(VALID_EVENTS)}",
        )

    bulletin = BulletinRow(
        url=str(body.url),
        events=",".join(body.events),
        secret=body.secret or "",
        librarian_id=int(payload["sub"]),
    )
    session.add(bulletin)
    await session.commit()
    await session.refresh(bulletin)

    return BulletinResponse(
        id=bulletin.id,
        url=bulletin.url,
        events=bulletin.events.split(","),
        created_at=bulletin.created_at,
        active=bulletin.active,
    )


@router.get("/", response_model=BulletinListResponse)
async def list_bulletins(
    session: AsyncSession = Depends(get_session),
    payload: dict = Depends(verify_library_card),
) -> BulletinListResponse:
    """List all webhook subscriptions for the current librarian."""
    librarian_id = int(payload["sub"])
    result = await session.execute(
        select(BulletinRow).where(BulletinRow.librarian_id == librarian_id)
    )
    rows = result.scalars().all()

    items = [
        BulletinResponse(
            id=row.id,
            url=row.url,
            events=row.events.split(","),
            created_at=row.created_at,
            active=row.active,
        )
        for row in rows
    ]
    return BulletinListResponse(items=items, total=len(items))


@router.delete("/{bulletin_id}", status_code=204)
async def delete_bulletin(
    bulletin_id: int,
    session: AsyncSession = Depends(get_session),
    payload: dict = Depends(verify_library_card),
) -> None:
    """Remove a webhook subscription."""
    librarian_id = int(payload["sub"])
    bulletin = await session.get(BulletinRow, bulletin_id)

    if not bulletin or bulletin.librarian_id != librarian_id:
        raise HTTPException(
            status_code=404,
            detail="That bulletin board posting wasn't found.",
        )

    await session.delete(bulletin)
    await session.commit()


def sign_payload(payload_bytes: bytes, secret: str) -> str:
    """Create HMAC-SHA256 signature for webhook delivery."""
    return hmac.new(
        secret.encode(),
        payload_bytes,
        hashlib.sha256,
    ).hexdigest()
