"""Overdue -- FastAPI application entry point."""

import time
from collections import defaultdict
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from src.config.defaults import QUIET_HOURS_REQUESTS_PER_MINUTE
from src.config.settings import settings
from src.db.engine import engine
from src.db.tables import Base
from src.errors.handlers import register_handlers
from src.errors.incidents import QuietHoursExceeded


@asynccontextmanager
async def lifespan(app: FastAPI):  # type: ignore[no-untyped-def]
    """Create database tables on startup."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(
    title=settings.app_name,
    description="Don't let your knowledge expire.",
    version="0.3.0",
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


# Import and include routers after app creation to avoid circular imports
from src.api.router import api_router  # noqa: E402

app.include_router(api_router, prefix="/api")
