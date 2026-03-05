# Overdue

> Your knowledge is fading. Fight back.

Overdue is a gamified knowledge library where every fact you capture starts decaying the moment you shelve it. You're a **librarian** in a pixel art world -- shelving **volumes** of knowledge, watching their **Dewey Scores** crumble as dust settles, and racing to review them before they're lost. Earn XP ("pages read"), climb ranks from Page to Head Librarian, unlock badges, and keep your streak alive. Neglect your stacks and the Reading Room descends into chaos.

This isn't a to-do app with a theme. It's a game that happens to make you smarter.

## What Makes It Tick

- **Dewey Score decay** -- Every volume starts at 100 and rots toward 0. Review it to reset the clock. Ignore it and watch it crumble.
- **XP and ranks** -- Earn pages read for every action. Rise from Page (0 XP) through Shelver, Librarian, and Archivist to Head Librarian (5,000 XP).
- **11 badges across two tiers** -- From "First Shelve" (Common) to "Marathon Reader" (Rare, 30-day streak). Collect them all for the Completionist badge.
- **Streaks** -- Review daily for +15 bonus pages. Miss a day and your streak resets. The pressure is real.
- **Reading Room mood** -- The library's ambient atmosphere shifts from "Quiet Study" (golden glow) to "Closed for Renovation" (crisis mode) based on your collective Dewey Scores.
- **AI bot players** -- Casual, diligent, and obsessive bots populate the leaderboard and keep things competitive while you sleep.
- **Pixel art everything** -- 26 hand-crafted SVG icons, 8 heroic librarian avatars, custom dark parchment palette. Zero emoji.
- **Keyboard shortcuts** -- `Enter` to review, arrows to navigate, `Escape` to go back. Fly through your stacks.

## Quick Start

```bash
git clone https://github.com/onlydole/overdue.git
cd overdue
docker compose up --build
```

Open `http://localhost:8000`, register your first librarian, and start shelving.

The database, demo data, and bot players are all set up automatically. Manage the library with Docker Compose:

```bash
docker compose exec overdue overdue bots simulate    # Shuffle the leaderboard
docker compose exec overdue overdue stats             # Library statistics
docker compose exec overdue overdue seed demo         # Re-seed demo data
```

<details>
<summary>Running without Docker</summary>

```bash
git clone https://github.com/onlydole/overdue.git
cd overdue
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
uvicorn src.main:app --reload
```

</details>

## The Stack

| Layer | Tech |
|---|---|
| Backend | FastAPI (Python 3.12+), fully async |
| Frontend | Jinja2 + HTMX, Alpine.js for small UI state |
| Styling | Tailwind CSS with custom dark parchment palette |
| Database | SQLAlchemy async + aiosqlite (SQLite default) |
| Auth | PyJWT (HS256) with HMAC-safe key derivation |
| CLI | Typer with subcommands for everything |
| Deployment | Docker (Python 3.12-slim), non-root, healthcheck |

## API Quick Reference

| Endpoint | What It Does |
|---|---|
| `POST /api/librarians/register` | Get your library card |
| `POST /api/librarians/login` | Flash your credentials |
| `POST /api/volumes/` | Shelve new knowledge |
| `POST /api/volumes/{id}/review` | Brush off the dust |
| `GET /api/reading-room/health` | Check the library's mood |
| `GET /api/librarians/leaderboard` | See who's on top |

Full reference: [docs/api/endpoints.md](docs/api/endpoints.md)

## Configuration

All settings use the `OVERDUE_` prefix. Key variables:

| Variable | Default | What It Controls |
|---|---|---|
| `OVERDUE_SECRET_KEY` | insecure default | JWT signing -- **change in production** |
| `OVERDUE_DATABASE_URL` | `sqlite+aiosqlite:///./overdue.db` | Where your library lives |
| `OVERDUE_DEWEY_DECAY_SECONDS` | `10` | How fast dust settles (86400 for daily) |
| `OVERDUE_STREAK_COOLDOWN_SECONDS` | `5` | Seconds between streak-eligible reviews |
| `OVERDUE_PORT` | `8000` | Server port |
| `OVERDUE_ALLOWED_ORIGINS` | `["*"]` | CORS allowlist |

Full list: [docs/guides/configuration.md](docs/guides/configuration.md)

## Development

```bash
pytest                          # Run the test suite
ruff check src/ tests/          # Lint
ruff format src/ tests/         # Format
npm run css:build               # Rebuild Tailwind CSS
python scripts/build_icons.py   # Regenerate pixel art SVGs
```

## Project Structure

```text
src/
  api/          # REST endpoints (volumes, shelves, catalog, reading room, bulletins)
  auth/         # JWT library cards, session cookies, role-based access
  cli/          # Typer CLI (serve, seed, auth, stats, bots, shelves, volumes)
  config/       # Pydantic Settings, game balance constants, rate limiting
  db/           # Async engine, ORM tables, demo seed data
  errors/       # Library-themed exceptions and handlers
  game/         # XP engine, badges, streaks, mood, bots, pixel art icons & avatars
  models/       # Pydantic schemas and SQLAlchemy models
  web/          # HTML routes, Jinja2 template config, mood middleware
templates/      # Jinja2 templates and partials
static/         # CSS, JS, pre-rendered SVG pixel art
tests/          # pytest suite
docs/           # Guides, API reference, architecture, changelog
```

## Documentation

- [Installation](docs/guides/installation.md)
- [Quick Start](docs/guides/quickstart.md)
- [Configuration](docs/guides/configuration.md)
- [Gameplay Guide](docs/guides/gameplay.md) -- XP, ranks, badges, streaks, mood
- [Bot Players](docs/guides/bots.md) -- AI competition
- [API Endpoints](docs/api/endpoints.md)
- [Authentication](docs/api/authentication.md)
- [Architecture](docs/architecture/overview.md)
- [Changelog](docs/changelog/CHANGELOG.md)

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

[MIT](LICENSE)
