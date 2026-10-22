---
title: Project health audit, October 22, 2026
category: audits
freshness:
  exclude: true
---

# Project health audit, October 22, 2026

The tested library workflows pass after the fixes below. This is not a clean production security assessment. The container still has Debian advisories without published fixes, and bulletins do not deliver events.

The audit started from commit `abcbb4356e79722de45565926e66d7d2489fa28f`, which matched remote main when checked. The audit ran on `teedole/project-health-audit`. No deployment, release, or repository settings changed.

The baseline passed 238 tests, Ruff lint and formatting, and strict mypy. New workflow tests then reproduced 14 failures. A separate concurrency test reproduced four reviews and duplicate XP from simultaneous requests for one volume.

The fixes reject null PATCH values for required fields, return a conflict for duplicate shelf names, deduplicate bookmarks, validate web shelf selections and shelf name length, and return a proper missing-profile page. Volume creation and its game awards now commit together. Review requests use a conditional timestamp update so only one request can award XP for the same review. Quiet Hours now expires inactive clients that never make another request. API and CLI versions both read the installed package metadata.

Browser testing caught another failure. HTMX discarded HTML validation responses with status 400, leaving the form unchanged. The app now displays those responses for submitted forms. Browser checks confirmed that errors appear and that valid submissions, reviews, avatar changes, and card saves still work.

Compatible Python updates include FastAPI 0.159.1, SQLAlchemy 2.1.6, Pydantic 2.14.1, PyJWT 2.15.1, Certifi 2026.10.19, Uvicorn 0.54.0, Ruff 0.17.1, and mypy 2.4.0. The approved WebSockets upgrade moves from 16.0 to 17.3. The PyJWT minimum also increased to prevent an older vulnerable version from satisfying the manifest. HTMX moved from 1.9.10 to 1.9.12 and Alpine.js from 3.14.9 to 3.17.5. Both browser libraries now have locked npm dependencies and a reproducible copy script. A compatible file-watcher override removes the vulnerable braces dependency, and source-map-js updated to its patched release.

Docker moved to [Python 3.14.9](https://www.python.org/downloads/release/python-3149/), an expedited security release. It now installs the committed uv lockfile and omits development dependencies. Removing the unused compiler and pip bundle cleared the image's four Python package findings. Compose Watch rebuilds on lockfile changes. Local Makefile checks also use uv and the lockfile instead of the host's default Python.

CI retains the existing test, lint, and types jobs and adds Python 3.14 tests and frontend checks. Installs enforce lockfiles. Frontend checks audit npm dependencies, check JavaScript syntax, and compare regenerated CSS and browser libraries with their committed files. Python CI also checks generated icons. Repository branch protection was not changed; making the new jobs required remains a repository setting.

Verification completed locally:

- All 258 tests pass on Python 3.12.15 and Python 3.14.9. The 20 added cases cover invalid inputs, API and browser workflows, transaction rollback, concurrent reviews, metadata, and inactive rate-limit clients.
- `make check` passes, including Ruff lint, formatting, strict mypy, and pytest. Statement coverage increased from 50% to 67%.
- `pip-audit` and `npm audit` report zero known advisories in the locked application and development dependencies.
- A clean npm install builds the assets. Regeneration leaves CSS, browser libraries, and all 45 SVG assets unchanged.
- Actionlint validates all five GitHub Actions workflow files. The documentation freshness check passes for all 15 included pages, with a median score of 100 and a minimum of 75.
- The Docker image builds and becomes healthy. Authenticated CLI commands, bot listing, shelves, volumes, and personal stats work. SQLite integrity checks pass with no foreign-key violations. Restarting preserves the database without reseeding librarians.
- Four simultaneous reviews return successfully but create one review and award 50 pages once, compared with 140 pages before the fix.
- Browser checks cover login, HTMX navigation and polling, volume creation, duplicate bookmarks, review feedback and history, visible form errors, avatar selection, card saves, and the mobile menu. Reading Room, Shelves, and Settings have no horizontal overflow or broken images at 375 CSS pixels. The browser loaded all app assets. Expected HTTP 400 diagnostics came from deliberate invalid submissions.

Remaining limits:

- Trivy reports 44 high-severity Debian package findings across eight CVEs and zero critical findings. None lists a fixed Debian version. Several findings concern local mount or privilege-management tools; the image runs as a non-root librarian, but this audit does not establish that every advisory is unreachable. The exact CVEs and affected packages are in [the evidence file](2026-10-22-evidence.json). Python packages and the uv binary have no high or critical image findings.
- Bulletin creation, listing, and deletion work. There is no event dispatcher. The endpoint reference now states that subscriptions are stored but events are not delivered.
- The default configuration is for a demo. It ships a public signing-secret placeholder, automatic demo seeding, and accelerated decay and streak intervals. A production deployment needs its own secret and HTTPS cookie configuration. No live deployment configuration was available to assess.
- WebSockets 17.3 was approved and tested with an isolated echo fixture through Uvicorn with text, binary, ping, and close exchanges. The automatic, Sans-I/O, and legacy transports pass on both Python versions. The legacy transport emits its expected deprecation warning; the app uses automatic selection. HTMX stays on its current major version. Python 3.15 was not tested. The tested database is SQLite; other database engines and sustained load were not tested.
- At audit completion, the changes were uncommitted and hosted CI had not run them. The local checks and container results do not establish deployment health or complete test coverage.

To repeat the main checks, run `make check`, `npm ci --ignore-scripts`, `npm audit`, `npm run js:build`, `npm run css:build`, and `uv run --locked python scripts/build_icons.py`. Run pytest in separate locked environments for Python 3.12 and 3.14. Rebuild the Docker image and rerun the advisory scans before a release because package and advisory state changes.
