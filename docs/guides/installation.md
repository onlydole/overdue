---
title: Installation
category: guides
critical: true
freshness:
  ttl_days: 90
  sources:
    - "Dockerfile"
    - "docker-compose.yml"
    - "pyproject.toml"
    - "src/main.py"
    - "src/cli/main.py"
---

# Installation

## Prerequisites

- Python 3.12 or higher
- pip (or your preferred Python package manager)
- Node.js and npm (for Tailwind CSS builds, optional)

## Option 1: Docker (fastest)

```bash
git clone https://github.com/onlydole/overdue.git
cd overdue
docker compose up --build
```

Open `http://localhost:8000`. Done. The database, demo data, and bot players are all set up automatically.

## Option 2: Install from source

```bash
git clone https://github.com/onlydole/overdue.git
cd overdue
pip install -e ".[dev]"
```

This also installs the `overdue` console script -- the canonical CLI entry point used throughout these docs (`overdue serve`, `overdue bots list`, ...).

### Verify the installation

```bash
# Start the server
uvicorn src.main:app --reload

# In another terminal, check the health endpoint
curl http://localhost:8000/api/reading-room/health
```

You should see a JSON response with the library's mood and health stats.

### Build CSS (optional)

If you modify templates and add new Tailwind classes:

```bash
npm install
npm run css:build
```

### Regenerate pixel art assets (optional)

If you modify icon or avatar source code:

```bash
python scripts/build_icons.py
```

## Configuration

A fresh install works out of the box, but a few environment variables are worth knowing on day one:

- `OVERDUE_DATABASE_URL` -- database connection string. Docker Compose points it at a named volume; source installs default to a local SQLite file.
- `OVERDUE_SECRET_KEY` -- JWT signing secret. The docker-compose default is `change-me-in-production`, which triggers a loud insecure-secret warning at startup. Set your own value before exposing the server.
- `OVERDUE_DEBUG` -- enable debug mode (defaults to `false`).
- `OVERDUE_PORT` -- remaps the host port in the docker-compose port mapping (defaults to 8000).

See the [configuration guide](configuration.md) for the full list of settings.

## Demo credentials

On first startup with an empty database, Overdue auto-seeds three demo librarians -- **archie**, **paige**, and **dewey** -- with a generated password that is printed to the server log. Set `OVERDUE_DEMO_PASSWORD` to control the password yourself, or run `overdue seed seed`, which prints the password it used.

## Development dependencies

The `[dev]` extra installs:

- **pytest** + **pytest-asyncio** -- test runner with async support
- **pytest-cov** -- coverage reporting
- **ruff** -- linter and formatter
- **mypy** -- static type checking
- **PyYAML** -- YAML parsing for freshness metadata
- **tree-sitter** -- AST parser for symbol extraction
- **tree-sitter-typescript** -- TypeScript grammar for tree-sitter
