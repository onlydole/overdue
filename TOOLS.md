# TOOLS.md -- Overdue Developer & Agent Tooling Reference

This document catalogs every tool, command, and script available for developing, testing, deploying, and operating the Overdue application. It is designed for both human contributors and AI agents.

## CLI (`overdue`)

The Overdue CLI is built with [Typer](https://typer.tiangolo.com/) and registered as a console script via `pyproject.toml`. Install with `pip install -e .` to get the `overdue` command.

### Top-Level Commands

| Command | Description |
|---|---|
| `overdue version` | Print the current version (`0.1.0a1`) |
| `overdue serve` | Start the FastAPI server via uvicorn |

**`overdue serve` options:**

| Flag | Default | Description |
|---|---|---|
| `--host` | `0.0.0.0` | Bind address |
| `--port` | `8000` | Bind port |
| `--reload` | `false` | Enable auto-reload for development |

### Subcommand Groups

#### `overdue auth` -- Librarian management

| Command | Description |
|---|---|
| `overdue auth create` | Create a new librarian account |
| `overdue auth remove` | Remove a librarian account |

#### `overdue shelves` -- Shelf management

| Command | Description |
|---|---|
| `overdue shelves list` | List all shelves |
| `overdue shelves create` | Create a new shelf |

#### `overdue volumes` -- Volume management

| Command | Description |
|---|---|
| `overdue volumes list` | List all volumes |
| `overdue volumes create` | Create a new volume |

#### `overdue bots` -- AI bot player management

| Command | Description |
|---|---|
| `overdue bots add` | Add bot librarians (casual, diligent, obsessive) |
| `overdue bots simulate` | Run a round of simulated bot activity |
| `overdue bots remove` | Remove all bot librarians and their data |

#### `overdue seed` -- Demo data

| Command | Description |
|---|---|
| `overdue seed demo` | Seed the database with demo shelves, volumes, and bots |

#### `overdue stats` -- Statistics

| Command | Description |
|---|---|
| `overdue stats` | Display library statistics (librarians, volumes, shelves, XP) |

## Scripts

### `scripts/build_icons.py`

Pre-renders all pixel art icons and avatars as static SVG files to `static/icons/`.

```bash
python scripts/build_icons.py
```

**What it does:**
- Renders all 26 base icons as bare SVGs (no width/height/class attributes)
- Generates tinted variants for icons used in templates:
  - `{name}--green.svg` for: `checkmark`, `play`
  - `{name}--gold.svg` for: `book-open`, `books`, `chart`, `crown`, `fire`, `gamepad`, `house`, `award`
  - `{name}--flame.svg` for: `fire`
- Renders all 8 avatar SVGs (`avatar_01.svg` through `avatar_08.svg`)
- Prunes stale tinted SVG files no longer referenced by templates
- Reports count of written and pruned files

**When to run:** After any change to icon pixel maps (`src/game/icons/_*.py`), avatar definitions (`src/game/avatars.py`), or tint configuration.

## CSS Build (Tailwind)

Overdue uses Tailwind CSS with a custom configuration. The built output lives at `static/css/tailwind.css`.

```bash
# One-time build
npm run css:build

# Watch mode (auto-rebuild on template changes)
npm run css:watch
```

**When to run:** After adding or removing Tailwind utility classes in any template file.

## Development Tools

### Testing

```bash
# Run the full test suite
pytest

# Run with coverage
pytest --cov=src

# Run a specific test file
pytest tests/test_icons.py
```

Test configuration is in `pyproject.toml` under `[tool.pytest.ini_options]`:
- `asyncio_mode = "auto"` -- async tests run without explicit markers
- `testpaths = ["tests"]`

### Linting & Formatting

```bash
# Lint (errors, style, imports, naming, upgrades)
ruff check src/

# Auto-fix lint issues
ruff check src/ --fix

# Format code
ruff format src/

# Full quality check
pytest && ruff check src/
```

Ruff configuration (`pyproject.toml`):
- Target: Python 3.12
- Line length: 100
- Rules: E (pycodestyle errors), F (pyflakes), I (isort), N (naming), W (warnings), UP (pyupgrade)

### Type Checking

```bash
mypy src/
```

Configuration: strict mode, Python 3.12 target.

## REST API Endpoints

All API routes are mounted under `/api/`. Authentication uses JWT bearer tokens (library cards).

### Librarians (`/api/librarians`)

| Method | Path | Auth | Description |
|---|---|---|---|
| `POST` | `/api/librarians/register` | None | Register a new librarian |
| `POST` | `/api/librarians/login` | None | Authenticate and receive a library card (JWT) |
| `POST` | `/api/librarians/refresh` | Bearer | Refresh an expiring library card |
| `GET` | `/api/librarians/leaderboard` | None | Top librarians ranked by pages read |

### Volumes (`/api/volumes`)

| Method | Path | Auth | Description |
|---|---|---|---|
| `GET` | `/api/volumes` | Bearer | List volumes (filterable) |
| `POST` | `/api/volumes` | Bearer | Create a new volume |
| `GET` | `/api/volumes/{id}` | Bearer | Get a single volume |
| `PATCH` | `/api/volumes/{id}` | Bearer | Update a volume |
| `DELETE` | `/api/volumes/{id}` | Bearer | Delete a volume |
| `POST` | `/api/volumes/{id}/review` | Bearer | Review a volume (triggers game engine) |

### Shelves (`/api/shelves`)

| Method | Path | Auth | Description |
|---|---|---|---|
| `GET` | `/api/shelves` | Bearer | List all shelves |
| `POST` | `/api/shelves` | Bearer | Create a new shelf |
| `GET` | `/api/shelves/{id}` | Bearer | Get a shelf with its volumes |
| `DELETE` | `/api/shelves/{id}` | Bearer | Delete a shelf |

### Catalog (`/api/catalog`)

| Method | Path | Auth | Description |
|---|---|---|---|
| `GET` | `/api/catalog/autocomplete` | Bearer | Quick autocomplete suggestions |

### Reading Room (`/api/reading-room`)

| Method | Path | Auth | Description |
|---|---|---|---|
| `GET` | `/api/reading-room/health` | None | Library health snapshot (used by Docker healthcheck) |
| `GET` | `/api/reading-room/overdue` | Bearer | Report of overdue volumes |

### Bulletins (`/api/bulletins`)

| Method | Path | Auth | Description |
|---|---|---|---|
| `GET` | `/api/bulletins` | Bearer | List webhook subscriptions |
| `POST` | `/api/bulletins` | Bearer | Create a webhook subscription |
| `DELETE` | `/api/bulletins/{id}` | Bearer | Remove a webhook subscription |

## Web Routes

Web routes serve HTML pages via Jinja2 templates. Authentication uses session cookies.

| Path | Method | Description |
|---|---|---|
| `/` | GET | Reading room dashboard |
| `/login` | GET, POST | Login page and form handler |
| `/register` | GET, POST | Registration page and form handler |
| `/logout` | GET | Log out and clear session |
| `/shelves` | GET | Browse all shelves |
| `/shelves/create` | GET, POST | Create a new shelf |
| `/shelves/{id}` | GET | View a shelf and its volumes |
| `/volumes/{id}` | GET | View a volume with review action |
| `/volumes/create` | GET, POST | Create a new volume |
| `/my-library` | GET | Personal library view |
| `/profile/{id}` | GET | Librarian profile page |
| `/settings` | GET | Library card editor |
| `/settings/card` | POST | Save library card changes (username, email, role, avatar) |
| `/settings/avatar` | POST | Legacy avatar update route (redirects to /settings/card) |
| `/leaderboard` | GET | Leaderboard page |
| `/how-to-play` | GET | How to play guide |

### Keyboard Shortcuts

| Page | Key | Action |
|---|---|---|
| Volume detail (`/volumes/{id}`) | `Enter` | Review / next volume / done (priority order) |
| Volume detail (`/volumes/{id}`) | `Escape` / `ArrowLeft` | Back to shelf |
| Volume detail (`/volumes/{id}`) | `ArrowRight` | Next volume |
| Shelf detail (`/shelves/{id}`) | `Enter` | Open the most overdue volume for review |
| Shelf detail (`/shelves/{id}`) | `Escape` / `ArrowLeft` | Back to shelves list |

## Docker

### Build and Run

```bash
# Build and start
docker compose up --build

# Run in background
docker compose up -d

# Stop
docker compose down
```

### Environment Variables (docker-compose.yml)

| Variable | Default | Description |
|---|---|---|
| `OVERDUE_PORT` | `8000` | Host port mapping |
| `OVERDUE_SECRET_KEY` | `change-me-in-production` | JWT signing secret |
| `OVERDUE_DATABASE_URL` | `sqlite+aiosqlite:////app/data/overdue.db` | Database path inside container |
| `OVERDUE_DEBUG` | `false` | Debug mode |

### Container Details

- **Base image**: `python:3.12-slim`
- **User**: `librarian` (non-root)
- **Data volume**: `overdue-data` mounted at `/app/data/`
- **Healthcheck**: `GET /api/reading-room/health` every 30 seconds
- **Restart policy**: `unless-stopped`

## Dependencies

### Runtime (from `pyproject.toml`)

| Package | Purpose |
|---|---|
| `fastapi` | Web framework |
| `uvicorn[standard]` | ASGI server |
| `sqlalchemy[asyncio]` | ORM with async support |
| `aiosqlite` | Async SQLite driver |
| `pydantic[email]` | Data validation |
| `pydantic-settings` | Settings from environment variables |
| `PyJWT` | JWT library card encoding/decoding |
| `passlib[bcrypt]` | Password hashing |
| `bcrypt` | bcrypt backend |
| `typer` | CLI framework |
| `rich` | CLI output formatting |
| `jinja2` | Template engine |
| `python-multipart` | Form data parsing |
| `httpx` | Async HTTP client (webhooks) |
| `itsdangerous` | Session cookie signing |

### Development

| Package | Purpose |
|---|---|
| `pytest` | Test runner |
| `pytest-asyncio` | Async test support |
| `pytest-cov` | Coverage reporting |
| `ruff` | Linter and formatter |
| `mypy` | Static type checker |

Install dev dependencies: `pip install -e ".[dev]"`

## Automation & CI

### Dependabot (`.github/dependabot.yml`)

Automated dependency updates configured for:
- **pip**: Weekly updates, prefix `chore(deps):`
- **docker**: Weekly updates, prefix `chore(deps):`
- **github-actions**: Weekly updates, prefix `chore(deps):`

## Jinja2 Template Globals & Filters

Registered in `src/web/templates.py` and available in all templates:

### Globals

| Name | Signature | Description |
|---|---|---|
| `render_avatar` | `(avatar_id: str, size: int = 32) -> Markup` | Render a monster librarian avatar as inline SVG |
| `render_icon` | `(name: str, size: int = 16, color: str \| None = None) -> Markup` | Render a pixel art icon (static `<img>` or inline SVG for custom tints) |

### Filters

| Name | Signature | Description |
|---|---|---|
| `title_hash` | `(title: str) -> int` | Derive a stable integer from a string (used for visual variation) |

## Key Internal APIs

### Game Engine (`src/game/engine.py`)

The central game action processor. Call it from routes after a librarian action:

```python
from src.game.engine import process_review

result = await process_review(session, librarian_id, volume_id)
# result = {"xp_gained": 10, "badges_earned": [...], "streak": 5, ...}
```

### Icon Rendering (`src/game/icons`)

```python
from src.game.icons import render_icon_svg, render_icon_svg_bare, get_icon_names

# Full SVG with width/height/class (for inline use)
svg_html = render_icon_svg("star", size=16)

# Bare SVG without attributes (for static files)
svg_bare = render_icon_svg_bare("star")

# List all registered icon names
names = get_icon_names()  # ["books", "star", "award", ...]
```

### Avatar Rendering (`src/game/avatars.py`)

```python
from src.game.avatars import render_avatar_svg, render_avatar_svg_bare, AVATAR_CATALOG, get_avatar_choices

# Full SVG with size attributes
svg_html = render_avatar_svg("avatar_01", size=32)

# Bare SVG for static files
svg_bare = render_avatar_svg_bare("avatar_01")

# Catalog of all avatars (dict keyed by avatar_id)
catalog = AVATAR_CATALOG

# List of avatar choices with id and display name (for forms)
choices = get_avatar_choices()  # [{"id": "avatar_01", "name": "..."}, ...]
```

### Auth Helpers (`src/auth/library_card.py`)

```python
from src.auth.library_card import create_library_card, verify_library_card

# Issue a JWT
token = create_library_card(librarian_id=1, username="archie", role="Librarian")

# Verify (used as FastAPI dependency)
# payload = verify_library_card(credentials)
```

### Settings (`src/config/settings.py`)

```python
from src.config.settings import settings

settings.secret_key              # Raw secret from env
settings.signing_secret_key      # HMAC-safe key (>= 32 bytes, cached)
settings.database_url            # Database connection string
settings.token_expiry_minutes    # JWT lifetime
```
