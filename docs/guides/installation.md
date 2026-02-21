---
title: Installation
category: guides
---

# Installation

## Prerequisites

- Python 3.11 or higher
- pip (or your preferred Python package manager)

## Install from source

```bash
git clone https://github.com/onlydole/overdue.git
cd overdue
pip install -e ".[dev]"
```

## Verify the installation

```bash
# Start the server
uvicorn src.main:app --reload

# In another terminal, check the health endpoint
curl http://localhost:8000/api/reading-room/health
```

You should see a JSON response with the library's health status.

## Development dependencies

The `[dev]` extra installs:

- **pytest** -- test runner
- **pytest-asyncio** -- async test support
- **pytest-cov** -- coverage reporting
- **ruff** -- linter and formatter
- **mypy** -- type checking
