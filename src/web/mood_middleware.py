"""Middleware to compute library mood and inject into request state."""

import time

from fastapi import Request
from sqlalchemy import select
from starlette.middleware.base import BaseHTTPMiddleware

from src.api.volumes import calculate_dewey_score
from src.db.engine import async_session
from src.db.tables import VolumeRow
from src.game.mood import calculate_mood

_MOOD_CACHE_TTL = 30  # seconds
_mood_cache: dict[str, object] = {"ambiance": "", "expires_at": 0.0}


class MoodMiddleware(BaseHTTPMiddleware):
    """Compute the library mood on each request and store it in request.state."""

    async def dispatch(self, request: Request, call_next):
        # Skip for static files and API routes
        if request.url.path.startswith(("/static", "/api", "/favicon")):
            return await call_next(request)

        try:
            now = time.time()
            if now < _mood_cache["expires_at"]:
                request.state.mood_ambiance = _mood_cache["ambiance"]
            else:
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
                ambiance = mood["ambiance"]
                _mood_cache["ambiance"] = ambiance
                _mood_cache["expires_at"] = now + _MOOD_CACHE_TTL
                request.state.mood_ambiance = ambiance
        except Exception:
            request.state.mood_ambiance = "soft_pages"

        return await call_next(request)
