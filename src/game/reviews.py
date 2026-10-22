"""Coordinate reviews submitted at the same time."""

from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.attributes import set_committed_value

from src.db.tables import VolumeRow
from src.utils import utcnow


async def claim_review(session: AsyncSession, volume: VolumeRow) -> bool:
    """Reset the timestamp only if nobody has reviewed this version yet."""
    reviewed_at = utcnow()
    result = await session.execute(
        update(VolumeRow)
        .where(
            VolumeRow.id == volume.id,
            VolumeRow.last_reviewed_at == volume.last_reviewed_at,
            VolumeRow.archived.is_(False),
        )
        .values(last_reviewed_at=reviewed_at)
        .returning(VolumeRow.id)
        .execution_options(synchronize_session=False)
    )
    if result.scalar_one_or_none() is None:
        await session.refresh(volume)
        return False
    set_committed_value(volume, "last_reviewed_at", reviewed_at)
    return True
