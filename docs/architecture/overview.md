---
title: Architecture Overview
category: architecture
freshness:
  ttl_days: 365
  sources:
    - "src/main.py"
    - "src/db/*.py"
    - "src/game/*.py"
    - "src/web/*.py"
    - "src/api/*.py"
    - "src/auth/*.py"
    - "src/cli/*.py"
    - "src/cli/commands/*.py"
    - "src/config/*.py"
    - "src/errors/*.py"
    - "src/models/*.py"
---

# Architecture Overview

Overdue follows a layered architecture with clear separation of concerns. Every layer speaks the library metaphor -- from "library cards" (JWT) to "quiet hours" (rate limiting) to "bulletins" (webhooks).

## Layers

```
┌─────────────────────────────────┐
│         Web Dashboard           │  Jinja2 + HTMX templates
├─────────────────────────────────┤
│           API Layer             │  FastAPI routers
├─────────────────────────────────┤
│        Game Mechanics           │  XP, badges, streaks, mood
├─────────────────────────────────┤
│       Pixel Art System          │  26 icons, 8 avatars (SVG paths)
├─────────────────────────────────┤
│       Business Logic            │  Dewey Scores, catalog, mood
├─────────────────────────────────┤
│         Middleware              │  Rate limiting, mood backdrop
├─────────────────────────────────┤
│         Data Layer              │  SQLAlchemy async + Pydantic
├─────────────────────────────────┤
│          Database               │  SQLite (aiosqlite, configurable URL)
├─────────────────────────────────┤
│            CLI                  │  Typer (serve, seed, bots, stats, ...)
└─────────────────────────────────┘
```

## Module responsibilities

### `src/api/`
REST API endpoints organized by domain. Each router handles a specific resource type (volumes, shelves, catalog, reading room, bulletins), plus the librarians/auth router mounted at `/api/librarians` (registration, login, refresh, leaderboard).

### `src/auth/`
Authentication and authorization. Librarian registration and login, JWT "library card" generation via PyJWT (HS256), session cookies for web, and object-level authorization via the circulation desk (a resource's owner, or a Head Librarian, may manage it).

### `src/config/`
Application settings (via pydantic-settings with `OVERDUE_` prefix), game balance constants (Dewey thresholds, XP values, rank definitions, mood levels), and rate limiting configuration.

### `src/game/`
Game mechanic calculations. XP awarding, rank progression, badge tracking (11 badges across 2 tiers), streak management, reading room mood calculation, AI bot simulation, and the pixel art icon/avatar system. A shelf bonus (+50 XP) is awarded when a review brings the last struggling volume on a multi-volume shelf back into good shape.

### `src/game/icons/`
26 pixel art icons defined as SVG path strings on a 24x24 viewBox. Icons support CSS `currentColor` tinting for flexible theming. Pre-rendered to `static/icons/` as bare SVGs with optional tinted variants (green, gold, flame).

### `src/game/avatars.py`
8 heroic librarian silhouettes defined as hand-crafted SVG path strings on a 32x32 grid. Each avatar has a unique character design with primary, secondary, and accent colors.

### `src/models/`
Pydantic models for request/response validation and SQLAlchemy table definitions for persistence.

### `src/db/`
Database engine configuration and session management using SQLAlchemy's async engine. SQLite foreign key enforcement is switched on per connection via a PRAGMA in `src/db/engine.py`. Includes demo data seeding with shelves, volumes, and bot players.

### `src/web/`
Server-side rendered dashboard routes. Returns HTML responses using Jinja2 templates with HTMX for interactive updates. Includes mood middleware that computes the library's ambient atmosphere from aggregate Dewey Scores.

### `src/errors/`
Library-themed exception classes and FastAPI exception handlers. Each error type has a unique incident code (TS-001+) and a friendly message.

### `src/cli/`
Typer-based command-line interface. Commands: `serve`, `seed`, `bots`, `stats`, `shelves`, `volumes`, `auth`, and `version`.

## Middleware stack

Four middlewares wrap every request: CORS, session (cookie-backed, via Starlette), the mood middleware, and the quiet-hours rate limiter. There is **no** authentication middleware -- auth happens per route via FastAPI dependency injection: API routes verify the bearer library card (JWT) through an HTTPBearer dependency, and web routes resolve the current librarian from the session cookie with a helper.

## Data flow

1. Request arrives at API or web route
2. Route dependencies authenticate the caller (bearer library card for API, session cookie for web)
3. Mood middleware attaches the ambient atmosphere for web page requests (cached, see below)
4. Route handler processes the request
5. Game mechanics are triggered where appropriate (XP, badges, streaks)
6. Data is persisted via SQLAlchemy
7. Response is returned (JSON for API, HTML partial or full page for web)

## Database schema

| Table | Purpose |
|---|---|
| `librarians` | Authenticated users with username, email, role, XP totals, avatar, and bot flag |
| `volumes` | Knowledge entries with title, content, shelf assignment, and review timestamps |
| `shelves` | Categorized collections that group related volumes |
| `reviews` | History of volume reviews with before-review Dewey Scores |
| `xp_ledger` | Itemized XP awards with reasons (shelving, reviewing, streaks) |
| `badges` | Achievement badges earned by librarians -- one row per librarian/badge pair, enforced by a unique constraint (with a SQLite startup migration for legacy databases) |
| `streaks` | Daily review streak tracking per librarian |
| `bulletins` | Webhook subscriptions for library events |
| `volume_bookmarks` | Two-column tag table: a volume id paired with a bookmark string |

### Relationships

- A **shelf** contains many **volumes**
- A **librarian** authors many **volumes** and creates many **shelves**
- A **volume** has many **reviews**, each linked to a **librarian**
- A **librarian** has one **streak** record and many **badges** and **XP ledger** entries
- A **librarian** can have many **bulletin** (webhook) subscriptions

## Dewey Score calculation

Dewey Scores decay over time. Each volume starts at 100 (pristine) and loses points based on the configured decay rate (`OVERDUE_DEWEY_DECAY_RATE` points per `OVERDUE_DEWEY_DECAY_SECONDS`). Reviewing a volume resets its score to 100. The calculation is synchronous -- scores are computed on read based on the time elapsed since the last review. Reviewing a volume that is already pristine (score 99.9 or above) is a no-op that awards nothing, and archived volumes cannot be reviewed at all (the endpoint returns 404).

## Mood system

The Reading Room mood is computed by the mood middleware (`src/web/mood_middleware.py`) for web page requests -- it skips `/static`, `/api`, and favicon paths, and serves from a 30-second cache rather than querying on every request:

1. On a cache miss, query `last_reviewed_at` timestamps for non-archived volumes
2. Compute the average Dewey Score across those volumes
3. Map to a mood level: Quiet Study (80+), Gentle Hum (60-79), Getting Noisy (40-59), Call for Order (20-39), Closed for Renovation (0-19)
4. Store mood data in `request.state` for template access
5. `base.html` sets `data-mood` on `<body>` to activate CSS ambient effects (gradients, vignettes, particles)
