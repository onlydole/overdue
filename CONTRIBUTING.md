# Contributing to Overdue

Thank you for your interest in contributing to Overdue! This document provides guidelines and information for contributors.

## Development setup

```bash
# Clone the repository
git clone https://github.com/onlydole/overdue.git
cd overdue

# Create a virtual environment
python -m venv .venv
source .venv/bin/activate

# Install with dev dependencies
pip install -e ".[dev]"
```

## Running tests

```bash
pytest
```

## Code style

We use [Ruff](https://docs.astral.sh/ruff/) for linting and formatting:

```bash
ruff check src/ tests/
ruff format src/ tests/
```

## Commit conventions

We follow [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` new feature
- `fix:` bug fix
- `docs:` documentation changes
- `test:` adding or updating tests
- `refactor:` code changes that neither fix a bug nor add a feature
- `chore:` maintenance tasks

## Pull requests

1. Create a feature branch from `main`
2. Make your changes with clear, focused commits
3. Ensure tests pass and linting is clean
4. Open a PR with a descriptive title and summary

## Architecture

See [docs/architecture/overview.md](docs/architecture/overview.md) for an overview of the project architecture.

## Questions?

Open an issue or start a discussion. We're happy to help!
