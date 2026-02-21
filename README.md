# Overdue

> Don't let your knowledge expire.

**Overdue** is a FastAPI-powered knowledge library game where you manage volumes of knowledge, keep them fresh, and level up as a librarian. Think of it as a Tamagotchi for your notes -- neglect the stacks and the reading room descends into chaos.

## What You'll Find Here

- A full-stack web app with an interactive **Reading Room** dashboard
- A REST API with JWT auth, fuzzy search, webhooks, and rate limiting
- A game layer with XP, ranks, badges, and daily streaks
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
    game/                  # XP, badges, streaks, mood
    models/                # Pydantic & SQLAlchemy models
    db/                    # Database engine
    web/                   # Dashboard routes
  templates/               # Jinja2 HTML templates
  static/                  # CSS, JS, badge SVGs
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
- **Tailwind CSS** -- Warm library-themed styling
- **SQLAlchemy (async)** -- Database with aiosqlite
- **Pydantic v2** -- Request/response validation
- **Docker** -- Containerized deployment

## Documentation

- [Installation](docs/guides/installation.md)
- [Quick Start](docs/guides/quickstart.md)
- [Configuration](docs/guides/configuration.md)
- [API Endpoints](docs/api/endpoints.md)
- [Authentication](docs/api/authentication.md)
- [Gameplay Guide](docs/guides/gameplay.md)
- [Architecture](docs/architecture/overview.md)

## Contributing

We'd love your help! Check out [CONTRIBUTING.md](CONTRIBUTING.md) to get started.

## License

[MIT](LICENSE)
