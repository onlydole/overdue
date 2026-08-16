"""Overdue -- FastAPI application entry point."""

import asyncio
import logging
import os
import time
from collections import defaultdict
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text
from sqlalchemy.exc import DatabaseError
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.sessions import SessionMiddleware

from src.config.defaults import QUIET_HOURS_REQUESTS_PER_MINUTE
from src.config.settings import settings
from src.db.engine import async_session, engine
from src.db.tables import Base
from src.errors.handlers import register_handlers
from src.utils import utcnow
from src.web.mood_middleware import MoodMiddleware
from src.web.templates import templates as _templates

logger = logging.getLogger("overdue")

# Track last Dewey recalculation time
_last_dewey_recalc: datetime | None = None


def _warn_on_insecure_secret() -> None:
    """Loudly flag a public/default signing secret at startup."""
    if settings.is_using_insecure_secret():
        logger.warning(
            "INSECURE SECRET KEY: OVERDUE_SECRET_KEY is set to a public default. "
            "Anyone can forge library cards and impersonate any librarian. "
            "Set OVERDUE_SECRET_KEY to a strong random value (>=32 bytes) before "
            "exposing this server."
        )


async def dewey_recalc_task() -> None:
    """Background task that recalculates Dewey Scores periodically."""
    global _last_dewey_recalc
    interval = settings.dewey_recalc_interval_minutes * 60
    while True:
        await asyncio.sleep(interval)
        _last_dewey_recalc = utcnow()
        # Scores are computed on-read, so this is a no-op marker
        # In a real system, this would pre-compute and cache scores


@asynccontextmanager
async def lifespan(app: FastAPI):  # type: ignore[no-untyped-def]
    """Create database tables on startup and start background tasks."""
    global _last_dewey_recalc
    _warn_on_insecure_secret()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Migrate existing DBs: add new columns if missing (idempotent)
    async with engine.begin() as conn:
        for col_name, col_def in [
            ("is_bot", "BOOLEAN NOT NULL DEFAULT 0"),
            ("bot_difficulty", "VARCHAR(50)"),
            ("avatar_id", "VARCHAR(20) NOT NULL DEFAULT 'avatar_01'"),
        ]:
            try:
                await conn.execute(text(f"ALTER TABLE librarians ADD COLUMN {col_name} {col_def}"))
            except Exception:
                pass  # Column already exists

    # Migrate volumes table: add new columns if missing
    async with engine.begin() as conn:
        for col_name, col_def in [
            ("spine_seed", "INTEGER NOT NULL DEFAULT 0"),
        ]:
            try:
                await conn.execute(text(f"ALTER TABLE volumes ADD COLUMN {col_name} {col_def}"))
            except Exception:
                pass  # Column already exists

    # Migrate badges table: enforce one badge per librarian. Skipped when the
    # table DDL already carries the unique constraint (fresh databases) so we
    # don't stack a second, redundant index on top of it; legacy tables get a
    # dedupe pass first so the index creation succeeds. SQLite-only: other
    # backends get the constraint from create_all and have no legacy history.
    if engine.url.get_backend_name() == "sqlite":
        try:
            async with engine.begin() as conn:
                ddl_result = await conn.execute(
                    text("SELECT sql FROM sqlite_master WHERE type='table' AND name='badges'")
                )
                badges_ddl = ddl_result.scalar() or ""
                if "uq_badges_librarian_badge" not in badges_ddl:
                    await conn.execute(
                        text(
                            "DELETE FROM badges WHERE id NOT IN "
                            "(SELECT MIN(id) FROM badges GROUP BY librarian_id, badge_name)"
                        )
                    )
                    await conn.execute(
                        text(
                            "CREATE UNIQUE INDEX IF NOT EXISTS uq_badges_librarian_badge "
                            "ON badges (librarian_id, badge_name)"
                        )
                    )
        except DatabaseError as exc:
            # A swallowed failure here would leave duplicate badges possible
            # with no operator signal, so say what happened.
            logger.warning("Badge uniqueness migration skipped: %s", exc)

    # Auto-seed if database is empty (for docker compose demo experience)
    from src.db.seed import is_db_empty, seed_demo_data

    async with async_session() as session:
        if await is_db_empty(session):
            demo_password = await seed_demo_data(session)
            if "OVERDUE_DEMO_PASSWORD" not in os.environ:
                # Without this, the generated password exists nowhere outside
                # the hash and the demo accounts are unusable.
                logger.warning(
                    "Seeded demo accounts (archie, paige, dewey) with generated "
                    "password: %s -- set OVERDUE_DEMO_PASSWORD to control it.",
                    demo_password,
                )

    # Auto-simulate bot activity on startup so leaderboard shifts
    from src.game.bots import simulate_bot_activity

    async with async_session() as session:
        try:
            await simulate_bot_activity(session)
            await session.commit()
        except Exception:
            pass  # No bots yet or other issue

    _last_dewey_recalc = utcnow()
    task = asyncio.create_task(dewey_recalc_task())
    yield
    task.cancel()


app = FastAPI(
    title=settings.app_name,
    description="Don't let your knowledge expire.",
    version="0.6.0",
    lifespan=lifespan,
)

# A wildcard origin combined with credentials is both forbidden by the CORS
# spec and dangerous: Starlette reflects the caller's Origin, letting any site
# make credentialed cross-origin requests. settings.cors_allow_credentials()
# only enables credentials for an explicit allowlist. (Same-origin requests
# from the web UI and bearer tokens on the API don't rely on CORS credentials.)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_origins(),
    allow_credentials=settings.cors_allow_credentials(),
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.signing_secret_key,
    same_site="lax",
    https_only=settings.session_https_only,
)

app.add_middleware(MoodMiddleware)

# Register library incident handlers
register_handlers(app)


# Custom error pages for web routes
@app.exception_handler(404)
async def not_found_handler(request: Request, exc: StarletteHTTPException) -> Response:
    if request.url.path.startswith("/api"):
        return JSONResponse(status_code=404, content={"detail": str(exc.detail)})
    return _templates.TemplateResponse(
        request,
        "404.html",
        {"request": request, "current_user": None},
        status_code=404,
    )


@app.exception_handler(500)
async def server_error_handler(request: Request, exc: Exception) -> Response:
    if request.url.path.startswith("/api"):
        return JSONResponse(status_code=500, content={"detail": "Internal server error"})
    return _templates.TemplateResponse(
        request,
        "500.html",
        {"request": request, "current_user": None},
        status_code=500,
    )


# Simple in-memory rate limiting (quiet hours)
_request_counts: dict[str, list[float]] = defaultdict(list)


@app.middleware("http")
async def quiet_hours_middleware(request: Request, call_next):  # type: ignore[no-untyped-def]
    """Enforce quiet hours (rate limiting)."""
    # Exclude static files from rate limiting to prevent asset loading from blocking the app
    if request.url.path.startswith("/static") or request.url.path.startswith("/favicon.ico"):
        return await call_next(request)

    client_ip = request.client.host if request.client else "unknown"
    now = time.time()
    window = 60.0  # 1 minute window

    # Clean old entries; drop drained IPs entirely so the map doesn't grow
    # without bound as one-off clients (scanners, crawlers) come and go
    recent = [t for t in _request_counts[client_ip] if now - t < window]
    if recent:
        _request_counts[client_ip] = recent
    else:
        _request_counts.pop(client_ip, None)

    if len(recent) >= QUIET_HOURS_REQUESTS_PER_MINUTE:
        oldest = recent[0]
        retry_after = int(window - (now - oldest)) + 1

        if request.url.path.startswith("/api"):
            return JSONResponse(
                status_code=429,
                content={"detail": f"Quiet hours, please. Try again in {retry_after}s."},
                headers={"Retry-After": str(retry_after)},
            )

        return HTMLResponse(
            status_code=429,
            content=f"""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta http-equiv="refresh" content="{retry_after}">
                <title>Quiet Hours</title>
                <style>
                    body {{
                        background-color: #0f0e17; color: #f0e6d3;
                        font-family: monospace; display: flex;
                        align-items: center; justify-content: center;
                        height: 100vh; margin: 0;
                    }}
                    .card {{
                        border: 4px solid #3d3d6b; background: #232342;
                        padding: 2rem; text-align: center;
                        box-shadow: 4px 4px 0 #0f0e17; max-width: 420px;
                    }}
                    h1 {{
                        color: #f0c543; text-transform: uppercase;
                        margin-bottom: 1rem; font-size: 1.5rem;
                    }}
                    .countdown {{ color: #f0c543; font-size: 2rem; margin: 1rem 0; }}
                </style>
            </head>
            <body>
                <div class="card">
                    <h1>Quiet Hours</h1>
                    <p>The librarian says you're being too loud!</p>
                    <p class="countdown" id="countdown">{retry_after}</p>
                    <p>seconds until you can return</p>
                </div>
                <script>
                    (function() {{
                        var remaining = {retry_after};
                        var el = document.getElementById('countdown');
                        var timer = setInterval(function() {{
                            remaining--;
                            if (remaining <= 0) {{
                                clearInterval(timer);
                                window.location.replace(document.referrer || '/');
                                return;
                            }}
                            el.textContent = remaining;
                        }}, 1000);
                    }})();
                </script>
            </body>
            </html>
            """,
            headers={"Retry-After": str(retry_after)},
        )

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
