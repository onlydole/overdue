# Overdue

> Don't let your knowledge expire.

**Overdue** is a FastAPI-powered knowledge library game. Manage volumes of knowledge on shelves, earn XP for keeping the library healthy, unlock badges, and maintain review streaks. Neglect the library and volumes go "overdue" -- the reading room mood shifts from "quiet study" to "closed for renovation."

## The game loop

1. **Shelve** new volumes of knowledge onto categorized shelves
2. Watch knowledge accumulate **dust** over time (Dewey Score decay)
3. **Review** volumes to keep them fresh and earn pages read (XP)
4. Level up your **librarian rank** and unlock **badges**
5. Maintain your **review streak** for bonus pages

## Quick start

```bash
# Clone the repository
git clone https://github.com/onlydole/overdue.git
cd overdue

# Install dependencies
pip install -e ".[dev]"

# Run the server
uvicorn src.main:app --reload

# Open http://localhost:8000 for the Reading Room dashboard
```

## Tech stack

- **Python 3.11+**
- **FastAPI** -- API and web server
- **Jinja2 + HTMX** -- Interactive dashboard
- **Tailwind CSS** -- Styling
- **SQLAlchemy (async)** -- Database
- **Pydantic v2** -- Validation
- **Typer** -- CLI

## Librarian's glossary

| Real concept | Overdue term |
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
| Archive/soft-delete | **Archive** |
| Admin | **Head Librarian** |
| XP / points | **Pages Read** |
| Level/rank | **Rank** |
| Achievement | **Badge** |
| Daily streak | **Streak** |

## Project structure

```
overdue/
  src/
    main.py               # FastAPI app entry point
    api/                   # REST API endpoints
    auth/                  # Authentication & authorization
    config/                # Settings and constants
    cli/                   # Typer CLI
    errors/                # Exception handling
    game/                  # XP, badges, streaks, mood
    models/                # Pydantic & SQLAlchemy models
    db/                    # Database engine
    web/                   # Dashboard routes
  templates/               # Jinja2 HTML templates
  static/                  # CSS, JS, images
  tests/                   # Test suite
  docs/                    # Documentation
```

## Documentation

- [Installation](docs/guides/installation.md)
- [Configuration](docs/guides/configuration.md)
- [Architecture overview](docs/architecture/overview.md)

## License

MIT
