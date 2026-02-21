# Overdue

> Don't let your knowledge expire. A retro pixel art knowledge library game.

**Overdue** is a FastAPI-powered knowledge library game wrapped in a retro pixel art aesthetic. Manage volumes of knowledge, keep them fresh, and level up as a librarian -- complete with 32x32 pixel art avatars, custom 16x16 pixel art icons, AI bot opponents, and a dark parchment palette straight out of a GBA-era library. Think of it as a Tamagotchi for your notes -- neglect the stacks and the reading room descends into chaos.

## What You'll Find Here

- A full-stack web app with an interactive **Reading Room** dashboard rendered in pixel art style
- A REST API with JWT auth, fuzzy search, webhooks, and rate limiting
- A game layer with XP, ranks, badges, and daily streaks
- **12 pixel art librarian avatars** -- diverse 32x32 shoulders-up portraits built from code
- **Custom pixel art icon system** -- 16x16 GBA-era SVG icons replacing all emoji throughout the UI
- **AI bot players** -- simulated librarians that populate the leaderboard with three difficulty tiers
- "Press Start 2P" headings and "VT323" body text for full retro typography
- All wrapped in a cozy library metaphor (your 404 says "That volume isn't on any of our shelves")

## Getting Started

### Option 1: Docker (fastest)

```bash
git clone https://github.com/onlydole/overdue.git
cd overdue
docker compose up --build
```

Open [http://localhost:8000](http://localhost:8000) and you're in the Reading Room.

### Option 2: Local Python

```bash
git clone https://github.com/onlydole/overdue.git
cd overdue

# Create a virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"

# Start the server
uvicorn src.main:app --reload
```

Open [http://localhost:8000](http://localhost:8000) for the dashboard, or hit the API at [http://localhost:8000/api](http://localhost:8000/api).

## The Game Loop

1. **Shelve** new volumes of knowledge onto categorized shelves
2. Watch knowledge accumulate **dust** over time (Dewey Score decay)
3. **Review** volumes to keep them fresh and earn pages read (XP)
4. Level up your **librarian rank** from Page all the way to Head Librarian
5. Unlock **badges** and maintain your **review streak** for bonus XP
6. Compete against **AI bot librarians** on the leaderboard

## Pixel Art Design System

Overdue uses a fully custom pixel art rendering pipeline -- no emoji, no icon fonts, everything built from code:

- **Avatars** (32x32): 12 diverse librarian portraits with unique hair styles, skin tones, outfits, and optional glasses. Rendered as inline SVG via `render_avatar()` in Jinja2 templates.
- **Icons** (16x16): GBA-era decorative pixel art icons for UI elements. Pre-rendered as static SVG files in `static/icons/`, served via `<img>` tags through `render_icon()` in Jinja2 templates.
- **Typography**: "Press Start 2P" for headings, "VT323" for body text.
- **Palette**: Dark parchment theme -- `#0f0e17` background, `#1a1a2e` surfaces, `#232342` cards, `#3d3d6b` borders, `#f0e6d3` parchment text, `#f0c543` gold accents.

## API at a Glance

| Endpoint | What it does |
|---|---|
| `POST /api/librarians/register` | Create an account |
| `POST /api/librarians/login` | Get a library card (JWT) |
| `POST /api/volumes/` | Shelve a new volume |
| `POST /api/volumes/{id}/review` | Review a volume |
| `POST /api/catalog/search` | Search the card catalog |
| `GET /api/reading-room/health` | Check library health |
| `GET /api/librarians/leaderboard` | See who's on top |

Full reference: [docs/api/endpoints.md](docs/api/endpoints.md)

## Librarian's Glossary

Everything in Overdue is library-themed. Here's the translation guide:

| Real Concept | Overdue Term |
|---|---|
| Knowledge entry | **Volume** |
| Category/collection | **Shelf** |
| Authenticated user | **Librarian** |
| JWT token | **Library Card** |
| Freshness score (0-100) | **Dewey Score** |
| Search | **Catalog** |
| Health dashboard | **Reading Room** |
| Rate limit | **Quiet Hours** |
| Error | **Incident** |
| Webhook | **Bulletin** |
| Tags | **Bookmarks** |
| XP / points | **Pages Read** |
| Level/rank | **Rank** |
| Achievement | **Badge** |

## Project Structure

```
overdue/
  src/
    main.py               # FastAPI app entry point
    api/                   # REST API endpoints
    auth/                  # Authentication & authorization
    config/                # Settings and constants
    errors/                # Exception handling
    game/
      avatars.py           # 12 pixel art librarian avatars (32x32 SVG)
      icons/               # Pixel art icon system (16x16 SVG, GBA-era)
      bots.py              # AI bot player engine
      xp.py                # XP / pages-read calculations
      badges.py            # Badge unlock logic
      streaks.py           # Daily streak tracking
      mood.py              # Volume mood / dust state
      engine.py            # Game action processor
    models/                # Pydantic & SQLAlchemy models
    db/                    # Database engine and seed data
    web/                   # Dashboard routes and template config
  templates/               # Jinja2 HTML templates
    partials/              # Reusable template fragments
  static/                  # CSS, JS, pre-rendered icon SVGs
  tests/                   # Test suite
  docs/                    # Guides and API reference
```

## Configuration

All settings use environment variables prefixed with `OVERDUE_`:

| Variable | Default | Description |
|---|---|---|
| `OVERDUE_SECRET_KEY` | `change-me-in-production` | JWT signing key |
| `OVERDUE_DATABASE_URL` | `sqlite+aiosqlite:///./overdue.db` | Database connection |
| `OVERDUE_DEBUG` | `false` | Enable debug mode |
| `OVERDUE_PORT` | `8000` | Server port (Docker) |

See [docs/guides/configuration.md](docs/guides/configuration.md) for the full list.

## Tech Stack

- **Python 3.12+**
- **FastAPI** -- API and web server
- **Jinja2 + HTMX** -- Interactive dashboard without heavy JS
- **Tailwind CSS** -- Dark parchment-themed styling
- **SQLAlchemy (async)** -- Database with aiosqlite
- **Pydantic v2** -- Request/response validation
- **Custom pixel art renderer** -- Programmatic SVG generation for avatars and icons
- **Docker** -- Containerized deployment

## Documentation

- [Installation](docs/guides/installation.md)
- [Quick Start](docs/guides/quickstart.md)
- [Configuration](docs/guides/configuration.md)
- [API Endpoints](docs/api/endpoints.md)
- [Authentication](docs/api/authentication.md)
- [Gameplay Guide](docs/guides/gameplay.md)
- [Bot Players Guide](docs/guides/bots.md)
- [Architecture](docs/architecture/overview.md)
- [AGENTS.md](AGENTS.md) -- AI agent conventions and project guide
- [CLAUDE.md](CLAUDE.md) -- Symlink to AGENTS.md

## Contributing

We'd love your help! Check out [CONTRIBUTING.md](CONTRIBUTING.md) to get started.

## License

[MIT](LICENSE)
