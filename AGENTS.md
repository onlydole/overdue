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
- **Auth**: PyJWT (HS256) with HMAC-safe signing key derivation
- **CLI**: Typer with subcommands for auth, shelves, volumes, bots, seed, stats
- **Game layer**: XP engine, badge system, streaks, mood/dust decay, AI bots, pixel art avatars and icons
- **Deployment**: Docker (Python 3.12-slim) with docker-compose, non-root user, healthcheck

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
- **Icons** (16x16 pixel grid, GBA-era fidelity): Defined in `src/game/icons/` (split by category: `_books.py`, `_nature.py`, `_achievements.py`, `_objects.py`, `_characters.py`). Shared palette and shading helpers in `_palette.py`. Rendered as static `<img>` tags pointing to pre-rendered SVGs in `static/icons/`. For uncommon tint colors, falls back to inline SVG. Use `{{ render_icon("star", 16) }}` in templates.
- **Avatars** (32x32 pixel grid, GBA-era fidelity): Defined in `src/game/avatars.py`. 12 monster librarian portraits with species-specific rigs, strand-level hair, skin shading, and outfit detail. Rendered as inline SVG via the `render_avatar(avatar_id, size)` Jinja2 global. Use `{{ render_avatar("avatar_01", 32) }}` in templates.
- **Shared palette**: The system uses a consistent set of colors (GOLD, FLAME, GREEN, BLUE, PURPLE, PARCHMENT, INK) defined directly in `src/game/avatars.py` and `src/game/icons/_catalog.py`.
- **Static asset build**: `scripts/build_icons.py` pre-renders all icons and avatars to `static/icons/` as bare SVGs. Generates base icons plus tinted variants (`--green`, `--gold`) and prunes stale tints. Run after any icon or avatar changes.
- **Rendering pipeline**: Pixel coordinates -> list of `(x, y, color)` tuples -> SVG `<rect>` elements -> joined into `<svg>` string -> wrapped in `Markup()` -> registered as Jinja2 global -> called in templates. Icons use static `<img>` tags by default; avatars always render inline.
- **Tinted icon variants**: Only specific icon/color combinations get static tinted SVGs:
  - Green (`#5cdb5c`): `checkmark`, `play`
  - Gold (`#f0c543`): `book-open`, `books`, `chart`, `crown`, `fire`, `gamepad`, `house`, `trophy`

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
    api/                    # REST API endpoints
      router.py             # API router aggregation
      volumes.py            # Volume CRUD endpoints
      shelves.py            # Shelf CRUD endpoints
      catalog.py            # Search and autocomplete
      reading_room.py       # Health snapshot, overdue report
      bulletins.py          # Webhook subscriptions
    auth/                   # Authentication & authorization
      library_card.py       # Library card (JWT) creation/verification via PyJWT
      web_session.py        # Session-based browser auth (cookie)
      librarian.py          # Registration, login, refresh, leaderboard routes
      dependencies.py       # FastAPI dependency injection for auth
      circulation.py        # Role-based access control (Page -> Head Librarian)
    cli/                    # Typer CLI
      main.py               # Entry point (overdue command)
      commands/
        auth.py             # User management (create/remove)
        shelves.py          # Shelf management (list/create)
        volumes.py          # Volume management (list/create)
        bots.py             # Bot management (create/simulate/remove)
        seed.py             # Demo data seeding
        stats.py            # Statistics display
    config/                 # Settings and constants
      settings.py           # Pydantic Settings with OVERDUE_ prefix, signing_secret_key
      defaults.py           # Game balance constants (XP rates, decay, ranks, moods)
      quiet_hours.py        # Rate limiting middleware
    errors/                 # Exception handling
      incidents.py          # Custom exception classes (library-themed)
      handlers.py           # FastAPI exception handlers
      codes.py              # Error codes
    game/                   # Game mechanics layer
      xp.py                 # XP (pages read) calculations
      badges.py             # Badge unlock logic and definitions
      streaks.py            # Daily review streak tracking
      mood.py               # Volume mood / Dewey Score decay
      engine.py             # Game action processor (review -> XP + badges + streak)
      avatars.py            # 12 monster librarian avatars (32x32 pixel art SVG)
      icons/                # Pixel art icon system (16x16 SVG, GBA-era)
        __init__.py          # Re-exports render_icon_svg, get_icon_names
        _palette.py          # Shared color ramps + blend/darken/lighten helpers
        _renderer.py         # render_icon_svg() with viewBox="0 0 16 16"
        _books.py            # books, book-open, book-closed, scroll, bookmark, clipboard
        _nature.py           # fire, moon, star, sparkles, zap
        _achievements.py     # trophy, crown, award, chart
        _objects.py          # clock, search, key, hourglass, gear, house, library, construction
        _characters.py       # person, robot, gamepad, play, checkmark
      bots.py               # AI bot player engine (create, simulate, remove)
    models/                 # Pydantic & SQLAlchemy models
      volume.py             # Volume request/response schemas
      librarian.py          # Librarian schemas
      shelf.py              # Shelf schemas
      bulletin.py           # Bulletin (webhook) schemas
      catalog.py            # Search schemas
      game.py               # Game-related schemas
    db/                     # Database layer
      engine.py             # Async engine and session factory
      tables.py             # SQLAlchemy ORM table definitions
      seed.py               # Demo data seeding (shelves, volumes, bots)
    web/                    # Web dashboard routes and template config
      router.py             # Web router aggregation
      templates.py          # Jinja2 Templates instance with globals (render_avatar, render_icon)
      auth.py               # Login/register/logout web routes
      actions.py            # Form action handlers
      dashboard.py          # Reading room dashboard
      shelves.py            # Shelf browsing routes
      volumes.py            # Volume browsing routes
      profile.py            # Librarian profile page
      settings.py           # Library card settings (edit username, email, role, avatar)
      leaderboard.py        # Leaderboard page
      how_to_play.py        # How to play guide
      my_library.py         # Personal library view
  scripts/
    build_icons.py          # Pre-render icons + avatars to static/icons/ as SVG files
  templates/                # Jinja2 HTML templates
    base.html               # Base layout (fonts, nav, footer)
    dashboard.html          # Reading room dashboard
    login.html              # Login page
    register.html           # Registration page
    shelves.html            # Shelf listing
    shelf_detail.html       # Single shelf with volumes
    shelf_create.html       # New shelf form
    volume_detail.html      # Volume view with review action
    volume_create.html      # New volume form
    profile.html            # Librarian profile page
    settings.html           # Library card editor (avatar carousel, editable fields)
    leaderboard.html        # Leaderboard page
    how_to_play.html        # How to play guide
    my_library.html         # Personal library view
    search.html             # Catalog search page
    404.html                # Not found error page
    500.html                # Server error page
    partials/               # Reusable template fragments
      activity_feed.html    # Reading room activity feed
      badge_grid.html       # Badge display grid
      dewey_gauge.html      # Dewey Score gauge
      game_feedback.html    # XP/badge feedback after actions
      review_result.html    # Review action result
      search_results.html   # Catalog search results
      streak_counter.html   # Streak display
      volume_card.html      # Volume card component
  static/
    css/styles.css          # Tailwind CSS + library card styles + pixel art foundations
    js/
      htmx.min.js           # HTMX library
      alpine.min.js         # Alpine.js for small UI state
      app.js                # Custom JS (minimal)
      gauges.js             # Visual gauge rendering
    icons/                  # Pre-rendered SVG assets (generated by scripts/build_icons.py)
  tests/                    # Test suite (pytest)
    conftest.py             # Pytest fixtures
    test_avatars.py         # Avatar rendering tests
    test_icons.py           # Icon rendering tests
  docs/                     # Guides and API reference
    api/                    # endpoints.md, authentication.md, errors.md, rate-limiting.md
    guides/                 # installation.md, quickstart.md, gameplay.md, bots.md, configuration.md
    architecture/           # overview.md
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

### Authentication Flow

1. Librarian registers or logs in via web form or API
2. Server issues a JWT library card signed with `settings.signing_secret_key` (HS256)
3. Web sessions store the token in a cookie via Starlette `SessionMiddleware`
4. API clients pass the token in the `Authorization: Bearer <token>` header
5. `signing_secret_key` is a `cached_property` that ensures >= 32 bytes for HS256 safety (short keys are hashed via SHA-256)

### Settings Page (Library Card Editor)

The settings page (`/settings`) renders a pixel art library card UI:

1. `GET /settings` loads the current librarian's card data (username, email, role, avatar)
2. Avatar selection uses an Alpine.js carousel with prev/next arrows
3. `POST /settings/card` validates and saves all editable fields with uniqueness checks
4. On success, a fresh JWT is issued to reflect any username/role changes
5. Errors are rendered inline on the card form

### Adding a New Pixel Art Icon

1. Choose the appropriate category file in `src/game/icons/` (e.g., `_books.py`, `_nature.py`)
2. Define the pixel map as a list of `(x, y, color)` tuples on a **16x16 grid** (coordinates 0-15)
3. Use colors from `_palette.py` -- apply 4-step shading ramps (highlight, base, shadow, deep_shadow)
4. Add a `register("your_icon_name", [...])` call inside the category's `register_icons()` function
5. Run `python scripts/build_icons.py` to generate the static SVG
6. If the icon needs a tinted variant, add it to `TINTED_ICON_NAMES` in `scripts/build_icons.py` and the corresponding set in `src/web/templates.py`
7. Use it in templates: `{{ render_icon("your_icon_name", 16) }}`

### Adding a New Avatar

1. Add the avatar definition to `AVATAR_CATALOG` in `src/game/avatars.py`
2. Define skin tone, hair style, hair color, glasses, and outfit color
3. Pick or create a hair builder function from `_HAIR_BUILDERS` (coordinates on **32x32 grid**, 0-31)
4. Use colors consistent with `src/game/icons/_catalog.py`.
5. Run `python scripts/build_icons.py` to update static SVGs
6. Use in templates: `{{ render_avatar("avatar_XX", 32) }}`

## Database Schema

| Table | Key Columns | Purpose |
|---|---|---|
| `librarians` | id, username, email, hashed_password, role, total_xp, is_bot, avatar_id | Authenticated users |
| `volumes` | id, title, content, shelf_id, author_id, last_reviewed_at, spine_seed | Knowledge entries |
| `shelves` | id, name, description, created_by | Volume categories |
| `reviews` | id, volume_id, librarian_id, reviewed_at, dewey_score_before | Review records |
| `xp_ledger` | id, librarian_id, amount, reason, created_at | XP award history |
| `badges` | id, librarian_id, badge_name, earned_at | Earned achievements |
| `streaks` | id, librarian_id, current_streak, longest_streak, last_review_date | Streak tracking |
| `bulletins` | id, url, events, secret, librarian_id, active | Webhook subscriptions |
| `volume_bookmarks` | volume_id, bookmark | Many-to-many tags |

## Game Balance Constants

Defined in `src/config/defaults.py`:

| Constant | Value | Description |
|---|---|---|
| `XP_SHELVE_VOLUME` | 10 | XP for creating a volume |
| `XP_REVIEW_CURRENT` | 5 | XP for reviewing a current volume |
| `XP_REVIEW_OVERDUE_MULTIPLIER` | 2x | Multiplier for overdue reviews |
| `XP_DAILY_STREAK_BONUS` | 15 | Bonus XP for daily streak |
| `XP_SHELF_BONUS` | 50 | Bonus when all shelf volumes are healthy |
| Ranks | Page (0) -> Shelver (100) -> Librarian (500) -> Archivist (2000) -> Head Librarian (5000) | Rank thresholds |
| Dewey decay | 3 pts / 10 sec (demo), 3 pts / 86400 sec (realistic) | Freshness decay rate |

## Testing

- **Test runner**: `pytest`
- **Linting**: `ruff check src/`
- **Formatting**: `ruff format src/`
- **Type checking**: `mypy` (strict mode)
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

## Environment Variables

All settings are configurable via environment variables prefixed with `OVERDUE_`:

| Variable | Default | Description |
|---|---|---|
| `OVERDUE_SECRET_KEY` | (insecure default) | JWT signing secret -- **set in production** |
| `OVERDUE_DATABASE_URL` | `sqlite+aiosqlite:///./overdue.db` | Database connection string |
| `OVERDUE_DEBUG` | `false` | Enable debug mode |
| `OVERDUE_TOKEN_EXPIRY_MINUTES` | `60` | JWT token lifetime |
| `OVERDUE_TOKEN_REFRESH_WINDOW_MINUTES` | `15` | Token refresh window |
| `OVERDUE_ALLOWED_ORIGINS` | `["*"]` | CORS allowed origins |
| `OVERDUE_HOST` | `0.0.0.0` | Server bind host |
| `OVERDUE_PORT` | `8000` | Server bind port |
| `OVERDUE_WEBHOOK_SECRET` | (empty) | Bulletin verification secret |
| `OVERDUE_DEWEY_DECAY_SECONDS` | `10` | Seconds per decay unit (86400 for daily) |
| `OVERDUE_STREAK_COOLDOWN_SECONDS` | `5` | Seconds between reviews for streak (86400 for daily) |
| `OVERDUE_SEARCH_MIN_SCORE` | `0.3` | Minimum catalog search relevance score |
| `OVERDUE_MAX_VOLUME_SIZE_KB` | `512` | Maximum volume content size |
