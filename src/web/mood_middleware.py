"""Middleware to compute library mood and inject into request state."""

from fastapi import Request
from sqlalchemy import select
from starlette.middleware.base import BaseHTTPMiddleware

from src.api.volumes import calculate_dewey_score
from src.db.engine import async_session
from src.db.tables import VolumeRow
from src.game.mood import calculate_mood


class MoodMiddleware(BaseHTTPMiddleware):
    """Compute the library mood on each request and store it in request.state."""

    async def dispatch(self, request: Request, call_next):
        # Skip for static files and API routes
        if request.url.path.startswith(("/static", "/api", "/favicon")):
            return await call_next(request)

        try:
            async with async_session() as session:
                result = await session.execute(
                    select(VolumeRow.last_reviewed_at).where(
                        VolumeRow.archived == False  # noqa: E712
                    )
                )
                reviewed_ats = result.scalars().all()

            if reviewed_ats:
                scores = [calculate_dewey_score(ts) for ts in reviewed_ats]
                avg = sum(scores) / len(scores)
            else:
                avg = 100.0

            mood = calculate_mood(avg)
            request.state.mood_ambiance = mood["ambiance"]
        except Exception:
            request.state.mood_ambiance = "soft_pages"

        return await call_next(request)
