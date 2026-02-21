"""Overdue -- FastAPI application entry point."""

import asyncio
import time
from collections import defaultdict
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from src.config.defaults import QUIET_HOURS_REQUESTS_PER_MINUTE
from src.config.settings import settings
from src.db.engine import async_session, engine
from src.db.tables import Base, VolumeRow

from src.errors.handlers import register_handlers
from src.errors.incidents import QuietHoursExceeded

# Track last Dewey recalculation time
_last_dewey_recalc: datetime | None = None


async def dewey_recalc_task() -> None:
    """Background task that recalculates Dewey Scores periodically."""
    global _last_dewey_recalc
    interval = settings.dewey_recalc_interval_minutes * 60
    while True:
        await asyncio.sleep(interval)
        _last_dewey_recalc = datetime.utcnow()
        # Scores are computed on-read, so this is a no-op marker
        # In a real system, this would pre-compute and cache scores


@asynccontextmanager
async def lifespan(app: FastAPI):  # type: ignore[no-untyped-def]
    """Create database tables on startup and start background tasks."""
    global _last_dewey_recalc
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    _last_dewey_recalc = datetime.utcnow()
    task = asyncio.create_task(dewey_recalc_task())
    yield
    task.cancel()


app = FastAPI(
    title=settings.app_name,
    description="Don't let your knowledge expire.",
    version="0.6.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register library incident handlers
register_handlers(app)

# Simple in-memory rate limiting (quiet hours)
_request_counts: dict[str, list[float]] = defaultdict(list)


@app.middleware("http")
async def quiet_hours_middleware(request: Request, call_next):  # type: ignore[no-untyped-def]
    """Enforce quiet hours (rate limiting)."""
    client_ip = request.client.host if request.client else "unknown"
    now = time.time()
    window = 60.0  # 1 minute window

    # Clean old entries
    _request_counts[client_ip] = [
        t for t in _request_counts[client_ip] if now - t < window
    ]

    if len(_request_counts[client_ip]) >= QUIET_HOURS_REQUESTS_PER_MINUTE:
        oldest = _request_counts[client_ip][0]
        retry_after = int(window - (now - oldest)) + 1
        raise QuietHoursExceeded(retry_after=retry_after)

    _request_counts[client_ip].append(now)
    response = await call_next(request)
    return response


# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Import and include routers after app creation to avoid circular imports
from src.api.router import api_router  # noqa: E402
from src.web.router import web_router  # noqa: E402

app.include_router(api_router, prefix="/api")
app.include_router(web_router)
