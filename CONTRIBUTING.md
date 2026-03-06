# Contributing to Overdue

Thanks for wanting to help out! Whether you're fixing a typo, adding a feature, or reporting a bug, every contribution makes the library a better place.

## Getting Set Up

### With Docker

The fastest way to get a working environment:

```bash
git clone https://github.com/onlydole/overdue.git
cd overdue
docker compose up --build
```

The app will be running at [http://localhost:8000](http://localhost:8000).

### Without Docker

```bash
git clone https://github.com/onlydole/overdue.git
cd overdue

# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install with dev dependencies
pip install -e ".[dev]"

# Start the dev server
uvicorn src.main:app --reload
```

## Running Tests

```bash
pytest
```

To run with coverage:

```bash
pytest --cov=src
```

## Code Style

We use [Ruff](https://docs.astral.sh/ruff/) for linting and formatting. Run both before submitting a PR:

```bash
ruff check src/ tests/
ruff format src/ tests/
```

## Commit Conventions

We follow [Conventional Commits](https://www.conventionalcommits.org/). Scope is optional but encouraged:

```
feat(game): add Marathon Reader badge
fix(catalog): handle empty search queries
docs: update quickstart guide
test(auth): add token refresh tests
chore: bump dependencies
```

## Making a Pull Request

1. Fork the repo and create a branch from `main`
2. Make your changes -- keep commits focused and atomic
3. Run `pytest` and `ruff check` to make sure everything's clean
4. Push your branch and open a PR
5. Describe what you changed and why in the PR body

That's it. We'll review and get back to you.

## Automated Documentation Updates

After your PR is merged to `main`, an automated workflow checks whether any documentation needs updating based on your changes. Here's how it works:

- **Automatic checks:** If your PR modifies files in `src/` or `docs/`, Claude Code Action analyzes the changes and determines if any documentation is out of sync
- **Follow-up PRs:** When updates are needed, the workflow opens a new PR with the proposed documentation changes for review
- **Visible reasoning:** Claude posts a comment on your merged PR explaining what it analyzed and what documentation updates (if any) were made. The full analysis is also available in the workflow logs
- **Opt out:** Add the `skip-docs-check` label to your PR if you want to skip the automated documentation check
- **Safety guards:** The workflow only runs for merged PRs from repository members and collaborators, and skips bot-authored PRs to prevent loops

This automation helps keep documentation in sync with code changes. The posted comment gives you transparency into Claude's decision-making without needing to dig through CI logs. If you get a follow-up documentation PR, review it like any other contribution -- the changes are suggestions, not automatic merges.

## Reporting Issues

Found a bug or have an idea? [Open an issue](https://github.com/onlydole/overdue/issues/new). Include:

- What you expected to happen
- What actually happened
- Steps to reproduce (if applicable)

## Architecture

If you're diving into the code, [docs/architecture/overview.md](docs/architecture/overview.md) gives you the lay of the land.

## License

By contributing, you agree that your contributions will be licensed under the [MIT License](LICENSE).
