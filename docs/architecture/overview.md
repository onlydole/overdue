---
title: Architecture Overview
category: architecture
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
│          Database               │  SQLite (dev) / PostgreSQL
├─────────────────────────────────┤
│            CLI                  │  Typer (serve, seed, bots, stats)
└─────────────────────────────────┘
```

## Module responsibilities

### `src/api/`
REST API endpoints organized by domain. Each router handles a specific resource type (volumes, shelves, catalog, reading room, bulletins).

### `src/auth/`
Authentication and authorization. Librarian registration and login, JWT "library card" generation via PyJWT (HS256), session cookies for web, and role-based access control via the circulation desk.

### `src/config/`
Application settings (via pydantic-settings with `OVERDUE_` prefix), game balance constants (Dewey thresholds, XP values, rank definitions, mood levels), and rate limiting configuration.

### `src/game/`
Game mechanic calculations. XP awarding, rank progression, badge tracking (11 badges across 2 tiers), streak management, reading room mood calculation, AI bot simulation, and the pixel art icon/avatar system.

### `src/game/icons/`
26 pixel art icons defined as SVG path strings on a 24x24 viewBox. Icons support CSS `currentColor` tinting for flexible theming. Pre-rendered to `static/icons/` as bare SVGs with optional tinted variants (green, gold, flame).

### `src/game/avatars.py`
8 heroic librarian silhouettes defined as hand-crafted SVG path strings on a 32x32 grid. Each avatar has a unique character design with primary, secondary, and accent colors.

### `src/models/`
Pydantic models for request/response validation and SQLAlchemy table definitions for persistence.

### `src/db/`
Database engine configuration and session management using SQLAlchemy's async engine. Includes demo data seeding with shelves, volumes, and bot players.

### `src/web/`
Server-side rendered dashboard routes. Returns HTML responses using Jinja2 templates with HTMX for interactive updates. Includes mood middleware that computes the library's ambient atmosphere from aggregate Dewey Scores.

### `src/errors/`
Library-themed exception classes and FastAPI exception handlers. Each error type has a unique incident code (TS-001+) and a friendly message.

### `src/cli/`
Typer-based command-line interface for serving, seeding data, managing auth, viewing stats, and controlling bot players.

## Data flow

1. Request arrives at API or web route
2. Authentication middleware validates the library card (JWT) or session cookie
3. Mood middleware computes ambient atmosphere from aggregate Dewey Scores (web routes)
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
| `badges` | Achievement badges earned by librarians |
| `streaks` | Daily review streak tracking per librarian |
| `bulletins` | Webhook subscriptions for library events |
| `volume_bookmarks` | Many-to-many association for volume tags |

### Relationships

- A **shelf** contains many **volumes**
- A **librarian** authors many **volumes** and creates many **shelves**
- A **volume** has many **reviews**, each linked to a **librarian**
- A **librarian** has one **streak** record and many **badges** and **XP ledger** entries
- A **librarian** can have many **bulletin** (webhook) subscriptions

## Dewey Score calculation

Dewey Scores decay over time. Each volume starts at 100 (pristine) and loses points based on the configured decay rate (`OVERDUE_DEWEY_DECAY_RATE` points per `OVERDUE_DEWEY_DECAY_SECONDS`). Reviewing a volume resets its score to 100. The calculation is synchronous -- scores are computed on read based on the time elapsed since the last review.

## Mood system

The Reading Room mood is computed by the mood middleware (`src/web/mood_middleware.py`) on every web request:

1. Query all volume `last_reviewed_at` timestamps
2. Compute average Dewey Score across all volumes
3. Map to a mood level: Quiet Study (80+), Gentle Hum (60-79), Getting Noisy (40-59), Call for Order (20-39), Closed for Renovation (0-19)
4. Store mood data in `request.state` for template access
5. `base.html` sets `data-mood` on `<body>` to activate CSS ambient effects (gradients, vignettes, particles)
