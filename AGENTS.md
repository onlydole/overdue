# AGENTS.md -- Overdue Project Guide

This file provides conventions, architecture context, and guidelines for AI agents (and human contributors) working on the Overdue codebase.

## Project Overview

Overdue is a retro pixel art-themed gamified knowledge library application. Users ("librarians") create and review knowledge entries ("volumes"), organized on "shelves," earning XP ("pages read"), ranks, badges, and streaks. The entire UI is rendered in a pixel art aesthetic with custom-built SVG icons and avatars -- no emoji anywhere.

### Architecture

- **Backend**: FastAPI (Python 3.12+), async throughout
- **Frontend**: Jinja2 templates + HTMX for interactivity, minimal vanilla JS (Alpine.js for small UI state)
- **Styling**: Tailwind CSS with a custom dark parchment palette
- **Database**: SQLAlchemy async with aiosqlite (SQLite by default)
- **Validation**: Pydantic v2 for request/response models
- **Game layer**: XP engine, badge system, streaks, mood/dust decay, AI bots, pixel art avatars and icons

## Key Conventions

### Library Metaphor Terminology

All user-facing text and code identifiers use library-themed names. Never use the generic term when the Overdue term exists:

| Generic Term | Overdue Term | Used In |
|---|---|---|
| Post / entry | **Volume** | Models, API, templates |
| Category / collection | **Shelf** | Models, API, templates |
| User | **Librarian** | Auth, models, templates |
| JWT token | **Library Card** | Auth system |
| Freshness score | **Dewey Score** | Game engine |
| XP / points | **Pages Read** | Game engine, templates |
| Search | **Catalog** | API, templates |
| Dashboard | **Reading Room** | Web routes, templates |
| Rate limit | **Quiet Hours** | Middleware |
| Webhook | **Bulletin** | API |
| Tags | **Bookmarks** | Models, templates |

### Pixel Art Design System

All decorative visuals are custom-built pixel art SVGs. This is a hard rule:

- **NO emoji** anywhere in templates, JS, or Python-rendered HTML. Every decorative element uses a pixel art icon or avatar.
- **Icons** (8x8 pixel grid): Defined in `src/game/icons.py`. Rendered via the `render_icon(name, size)` Jinja2 global, which returns a `Markup()` object containing an inline SVG. Use `{{ render_icon("star", 16) }}` in templates.
- **Avatars** (16x16 pixel grid): Defined in `src/game/avatars.py`. 12 diverse librarian portraits with unique hair styles, skin tones, outfits, and optional glasses. Rendered via the `render_avatar(avatar_id, size)` Jinja2 global. Use `{{ render_avatar("avatar_01", 32) }}` in templates.
- **Rendering pipeline**: Pixel coordinates -> list of `(x, y, color)` tuples -> SVG `<rect>` elements -> joined into `<svg>` string -> wrapped in `Markup()` -> registered as Jinja2 global -> called in templates.

### Typography

- **Headings**: "Press Start 2P" (Google Fonts) -- pixelated retro feel
- **Body text**: "VT323" (Google Fonts) -- monospace terminal style
- Both loaded via `<link>` in `templates/base.html`

### Color Palette

| Role | Hex | CSS Variable |
|---|---|---|
| Background | `#0f0e17` | `bg-[#0f0e17]` |
| Surface | `#1a1a2e` | `bg-[#1a1a2e]` |
| Card | `#232342` | `bg-[#232342]` |
| Border | `#3d3d6b` | `border-[#3d3d6b]` |
| Parchment (text) | `#f0e6d3` | `text-[#f0e6d3]` |
| Gold (accent) | `#f0c543` | `text-[#f0c543]` |

## File Organization

```
overdue/
  src/
    main.py                 # FastAPI app, lifespan, middleware
    api/                    # REST API endpoints (volumes, librarians, shelves, catalog)
      router.py             # API router aggregation
      volumes.py            # Volume CRUD endpoints
      librarians.py         # Registration, login, leaderboard
    auth/                   # Authentication & authorization
      jwt.py                # Library card (JWT) creation/verification
      dependencies.py       # FastAPI dependency injection for auth
    config/                 # Settings and constants
      settings.py           # Pydantic Settings with OVERDUE_ prefix
      defaults.py           # Game balance constants (XP rates, decay, ranks)
    errors/                 # Exception handling
      incidents.py          # Custom exception classes (library-themed)
      handlers.py           # FastAPI exception handlers
    game/                   # Game mechanics layer
      xp.py                 # XP (pages read) calculations
      badges.py             # Badge unlock logic and definitions
      streaks.py            # Daily review streak tracking
      mood.py               # Volume mood / Dewey Score decay
      engine.py             # Game action processor (review -> XP + badges + streak)
      avatars.py            # 12 pixel art librarian avatars (16x16 SVG)
      icons.py              # Pixel art icon system (8x8 SVG)
      bots.py               # AI bot player engine (create, simulate, remove)
    models/                 # Pydantic & SQLAlchemy models
      volume.py             # Volume request/response schemas
      librarian.py          # Librarian schemas
    db/                     # Database layer
      engine.py             # Async engine and session factory
      tables.py             # SQLAlchemy ORM table definitions
      seed.py               # Demo data seeding (shelves, volumes, bots)
    web/                    # Web dashboard routes and template config
      router.py             # Web route aggregation
      templates.py          # Jinja2 Templates instance with globals (render_avatar, render_icon)
      actions.py            # Form action handlers
      shelves.py            # Shelf browsing routes
      settings.py           # User settings routes
  templates/                # Jinja2 HTML templates
    base.html               # Base layout (fonts, nav, footer)
    partials/               # Reusable template fragments (review_result, etc.)
    profile.html            # Librarian profile page
    shelves.html            # Shelf listing
    shelf_detail.html       # Single shelf with volumes
    volume_detail.html      # Volume view with review action
    volume_create.html      # New volume form
    settings.html           # User settings page
  static/
    css/styles.css          # Tailwind-generated CSS
    js/
      htmx.min.js           # HTMX library
      alpine.min.js         # Alpine.js for small UI state
      app.js                # Custom JS (minimal)
  tests/                    # Test suite (pytest)
  docs/                     # Guides and API reference
    api/                    # Endpoint docs, auth, errors, rate limiting
    guides/                 # Installation, quickstart, gameplay, bots, config
    architecture/           # Architecture overview
    changelog/              # CHANGELOG.md
```

## Common Patterns

### Jinja2 Partials

Reusable template fragments live in `templates/partials/`. Include them with:

```jinja
{% include "partials/review_result.html" %}
```

### HTMX Interactions

Interactive updates use HTMX attributes instead of custom JavaScript:

```html
<button hx-post="/volumes/{{ volume.id }}/review"
        hx-target="#review-result"
        hx-swap="innerHTML">
  Review
</button>
```

Server endpoints return HTML fragments for HTMX to swap in.

### Game Mechanic Layer

When a librarian performs an action (e.g., reviewing a volume), the flow is:

1. Web/API route receives the request
2. Route calls `src/game/engine.py` to process the action
3. Engine awards XP, checks badge unlocks, updates streak
4. Engine returns a result dict with XP gained, badges earned, etc.
5. Route renders the result (HTML partial for web, JSON for API)

### Adding a New Pixel Art Icon

1. Define the pixel map in `src/game/icons.py` as a list of `(x, y, color)` tuples on an 8x8 grid
2. Add it to the `ICON_CATALOG` dict with a descriptive name
3. Use it in templates: `{{ render_icon("your_icon_name", 16) }}`

### Adding a New Avatar

1. Add the avatar definition to `AVATAR_CATALOG` in `src/game/avatars.py`
2. Define skin tone, hair style, hair color, glasses, and outfit color
3. Pick or create a hair builder function from `_HAIR_BUILDERS`
4. Use in templates: `{{ render_avatar("avatar_XX", 32) }}`

## Testing

- **Test runner**: `pytest`
- **Linting**: `ruff check src/`
- **Formatting**: `ruff format src/`
- Run the full check: `pytest && ruff check src/`

## Commit Conventions

This project uses [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` -- New feature
- `fix:` -- Bug fix
- `docs:` -- Documentation only
- `style:` -- Formatting, no code change
- `refactor:` -- Code restructuring, no behavior change
- `test:` -- Adding or updating tests
- `chore:` -- Build, CI, dependency updates

Example: `feat: add pixel art icon system with 27 icons`

## AI Bot Players

Bots are managed via CLI commands and simulate library activity:

- **Three difficulty tiers**: casual, diligent, obsessive
- **Themed names**: Each tier has its own name pool (e.g., "bookworm42", "archivist_x77")
- **Full history**: Bots get XP ledger entries, volumes, reviews, streaks, and badges
- **Activity simulation**: `simulate_bot_activity()` runs on startup and can be triggered manually
- Bot code lives in `src/game/bots.py`
- See [docs/guides/bots.md](docs/guides/bots.md) for CLI usage
