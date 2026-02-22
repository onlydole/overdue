---
title: Changelog
category: changelog
---

# Changelog

All notable changes to Overdue will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/), and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added
- Docker Compose watch support for hot-reload during development.
- Tab-style navigation with active states and `hx-boost` page transitions.
- Interactive library card UI on settings page with material variants (stone, gelatin, chitin, spectral).
- Keyboard-accessible avatar picker with arrow button navigation.
- Global HTMX loading overlay with animated book icon.
- Mobile sticky action bars for volume review.

### Changed
- Replaced 5 icon modules (~4,000 lines of 16x16 pixel-coordinate tuples) with single `_catalog.py` file defining 28 icons as SVG path strings on 24x24 viewBox.
- Replaced 12 procedurally-generated 48x48 monster librarian avatars (~1,200 lines) with 8 hand-crafted 32x32 heroic librarian silhouettes (~150 lines) using SVG paths.
- Icons now scale cleanly and support CSS `currentColor` tinting. Bare exports default to parchment for `<img>` tag visibility.
- Upgraded frontend with material-changing library card effects, stamp animations, and barcode scan animations.
- Enhanced volume review UX with pristine volume detection and disabled states.
- Improved rate limiting to exclude static files and return styled 429 pages for web requests and JSON for API requests.

### Removed
- Catalog search feature: removed `POST /api/catalog/search` endpoint and `/search` web route. Autocomplete retained via `GET /api/catalog/autocomplete`.

## [0.8.0] - 2026-02-21

### Added
- AI bot players with CLI lifecycle commands, seeded activity simulation, and unique bot-generated volume content.
- Avatar selection wired through registration, profile, navigation, and a dedicated settings page.
- Pixel art icon package split into categorized modules with a shared palette utility system.
- Persisted visual book spine styles for shelf and volume presentation variety.
- Volume detail byline with librarian avatar and author metadata.
- Dependabot configuration for weekly dependency updates.

### Changed
- Replaced remaining emoji across the interface with pixel art icons.
- Upgraded avatar artwork to refined GBA-era portraits and then served them from pre-rendered static SVG assets.
- Enhanced review UX with celebratory toasts, loading skeletons, smoother transitions, and improved Dewey gauge animation.
- Polished shelf cards, typography, animations, and activity feed presentation in the Reading Room.
- Refreshed project docs for the pixel-art system, bot behavior, and current app architecture.
- Reused the shared Jinja2 templates instance in error handlers to keep rendering behavior consistent.

### Fixed
- Replaced `python-jose` with `PyJWT` to resolve a security vulnerability in token handling dependencies.
- Restored review animations by removing a conflicting animation delay.

## [0.7.0] - 2026-02-20

### Added
- Cookie-based web authentication (login/register flows) for the dashboard experience.
- Web forms for shelves, volumes, reviews, and catalog search.
- Responsive mobile-first styling and lightweight client-side interaction enhancements.
- Bulletin webhook subscriptions, persistence, and related incident codes (`TS-009`, `TS-010`).
- Security hardening with 1-hour access tokens, refresh endpoint support, and password complexity validation.
- Background Dewey Score recalculation task for periodic freshness updates.
- Catalog search v2 with fuzzy matching and excerpted result snippets.
- Game progression updates including Rare badges, overdue review XP multiplier, timeframe leaderboard filters, and streak ranking widgets.
- Docker and Docker Compose setup for local and containerized development.
- CLI power-user commands for serving, seeding, auth, library stats, and bot operations.
- Demo data seeding, startup auto-seed behavior, and custom web error pages.
- Python 3.12 baseline plus `max_volume_size_kb` config and new incident codes (`TS-011`, `TS-012`).
- Pixel art visual overhaul and the `/how-to-play` experience.

### Changed
- Wired game mechanics responses into API and web flows.
- Updated contributor docs and licensing materials for the expanded dev workflow.

### Fixed
- Resolved Docker build/runtime issues in containerized runs.
- Added `itsdangerous` and pinned `bcrypt` for web-session and passlib compatibility.

## [0.6.0] - 2025-02-26

### Added
- Web dashboard served by FastAPI with Jinja2 templates
- Reading Room dashboard page with mood indicator and Dewey Score distribution
- Shelf browsing page with visual bookshelf grid and color-coded progress bars
- Shelf detail page with book spine visualization
- Volume detail page with Dewey Score gauge and review history
- Librarian profile page with rank, XP progress bar, badge grid, and streak counter
- Leaderboard page with rankings table
- HTMX partials for interactive updates
- Static assets (Tailwind CSS, custom styles, HTMX, Alpine.js, Dewey gauge JS)
- Badge SVG icons (book-open, sparkles, fire, star, library, moon, zap, trophy)

## [0.5.0] - 2025-02-19

### Added
- XP system ("pages read") with awards for shelving and reviewing
- Rank progression (Page -> Shelver -> Librarian -> Archivist -> Head Librarian)
- 8 achievement badges with automatic tracking
- Daily review streak tracking with bonus XP
- Reading Room mood calculation based on aggregate Dewey Scores
- Game API endpoints (GET /librarians/me/xp, /me/badges, /me/streak, /leaderboard)
- Gameplay guide documentation

## [0.4.0] - 2025-02-12

### Added
- Card catalog search (POST /catalog/search)
- Autocomplete suggestions (GET /catalog/suggest)
- Overdue report endpoint (GET /reading-room/overdue)
- Dewey Score decay calculation with configurable rate
- Overdue detection based on score thresholds

## [0.3.0] - 2025-02-05

### Added
- 8 library-themed incident types (TS-001 through TS-008)
- Structured error responses with incident codes
- Rate limiting middleware (quiet hours) -- 60 requests/minute
- Error reference documentation
- Rate limiting documentation

## [0.2.0] - 2025-01-29

### Added
- Librarian registration and login endpoints
- JWT "library card" authentication (24-hour expiry)
- Role-based access control (circulation desk)
- Protected endpoints require valid library card
- Authentication documentation

### Changed
- Volume and shelf write endpoints now require authentication

## [0.1.0] - 2025-01-22

### Added
- FastAPI application with lifespan and CORS middleware
- Volume CRUD endpoints (create, list, get, update, archive, review)
- Shelf CRUD endpoints (create, list, get, update, delete)
- Reading Room health check endpoint
- Dewey Score calculation (synchronous, decay-based)
- API endpoint documentation
- Quick start guide

## [0.1.0-alpha] - 2025-01-15

### Added
- Project scaffolding and directory structure
- Configuration system with pydantic-settings
- Dewey Score thresholds and XP constants
- Rate limiting configuration (quiet hours)
- README with librarian's glossary
- Initial documentation (installation, configuration, architecture)
- Development tooling (ruff, pytest, mypy)
