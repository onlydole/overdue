---
title: Installation
category: guides
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

## Development dependencies

The `[dev]` extra installs:

- **pytest** + **pytest-asyncio** -- test runner with async support
- **pytest-cov** -- coverage reporting
- **ruff** -- linter and formatter
- **mypy** -- static type checking
