---
title: Changelog
category: changelog
---

# Changelog

All notable changes to Overdue will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/), and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added
- Automated documentation update workflow using GitHub Actions and Claude Code Action to detect documentation drift after PRs are merged to main.
- Observability improvements to doc-update workflow: reasoning displayed in GitHub Actions job summary via `display_report: true` for transparent automated documentation decisions. Removed `show_full_output: true` to prevent secrets exposure in logs and `use_sticky_comment: true` which only works in tag mode (PR #26, #27).
- Architecture documentation at `docs/architecture/ci-cd.md` documenting the doc-update workflow's configuration, tool permissions, safety guards, and troubleshooting.
- Party mode easter egg: library card barcode on settings page is a hidden clickable toggle (default cursor stays normal, revealing the secret only on hover). Subtle gold glow hint and faster scan animation appear on hover to aid discovery. Click activates party mode with cycling rainbow borders, purple scan line animations, audio, and localStorage persistence.
- Keyboard accessibility for party mode toggle (`Tab` to focus, `Enter`/`Space` to activate) with `prefers-reduced-motion` support.
- Safety guards: skips bot-authored PRs and respects `skip-docs-check` label to prevent infinite loops and allow opt-out.
- Rescue bonus: +20 XP awarded when reviewing volumes in Overdue territory (Dewey Score 0-24), in addition to the existing 2x multiplier. Total XP for overdue reviews increased from 10 to 30 XP (5 base × 2 + 20 rescue bonus).

### Changed
- Documentation update workflow triggers on all merged PRs instead of only those touching `docs/` or `src/` paths.
- XP display labels updated from "+N pages" format to "+N XP (N pages)" format throughout the UI for clarity.

### Fixed
- Documentation update workflow authentication by adding required `id-token: write` permission for OIDC authentication with Claude Code Action.
- Documentation update workflow by adding `--allowedTools "Bash(git:*),Bash(gh:*)"` to claude_args configuration. This resolved the "This command requires approval" error that was blocking Claude from creating branches, committing, pushing, and opening PRs (PR #29).
- Documentation update workflow by adding file manipulation tools (Read, Edit, Write, Glob, Grep) to allowedTools. This resolved the root cause of PR #31's failure where Claude had 3 permission denials and couldn't read code changes or modify documentation files. The original allowedTools from PR #29 only included git/gh bash subcommands (PR #33).
- Documentation update workflow by adding missing Bash tool permissions (git diff, git log, git status, git branch, ls) to allowedTools. These tools were causing workflow failures when Claude attempted to analyze repository changes, resulting in exhausted turn limits from permission denials (PR #38).
- Documentation update workflow by replacing fragile list of individual `Bash(git diff:*)`, `Bash(git log:*)`, etc. patterns with unrestricted `Bash` in `--allowedTools`. Claude naturally uses arbitrary shell commands (find, cat, compound commands, env-prefixed commands) that don't match specific patterns. Each denied command wasted a turn, causing failures with `--max-turns 15`. The workflow runs on ephemeral GitHub Actions runners with no production access, so the security boundary is GitHub Actions permissions, not Bash tool restrictions (PR #40).

## [1.0.0] - 2026-03-04

### Added
- Dosu branding: shields.io badge in README, Reference Desk card on How to Play page, and secondary CTA on 404 page.
- `?` keyboard shortcut opens the Reference Desk modal from any page -- links to Dosu for project questions.
- "Made with <3 by the Dosu team" in the global footer.
- Keyboard shortcut documented in the How to Play shortcuts grid.

## [0.9.0] - 2026-03-04

### Added
- Docker Compose watch support for hot-reload during development.
- Tab-style navigation with active states and `hx-boost` page transitions.
- Interactive library card UI on settings page with material variants (stone, gelatin, chitin, spectral).
- Keyboard-accessible avatar picker with arrow button navigation.
- Keyboard shortcuts for volume detail (`Enter`/`Escape`/arrows) and shelves listing (`Enter` for most overdue).
- Tiered loading indicator: silent <300ms, pixel progress bar at 300ms+, full overlay at 2s+.
- Paginated review history with HTMX-driven "load more" on volume detail.
- Keyboard shortcuts section on the how-to-play page.
- Mood-appropriate colors on how-to-play mood icons and Reading Room mood title.
- Mobile sticky action bars for volume review.
- Live-updating Reading Room dashboard with HTMX polling.
- Mood backdrop system with ambient gradient, vignette, and particle effects per mood level.

### Changed
- Replaced 5 icon modules (~4,000 lines of 16x16 pixel-coordinate tuples) with single `_catalog.py` file defining 26 icons as SVG path strings on 24x24 viewBox.
- Replaced 12 procedurally-generated 48x48 monster librarian avatars (~1,200 lines) with 8 hand-crafted 32x32 heroic librarian silhouettes (~150 lines) using SVG paths.
- Icons now scale cleanly and support CSS `currentColor` tinting. Bare exports default to parchment for `<img>` tag visibility.
- Replaced `trophy` icon with `award` across badge definitions and tinted icon sets.
- Renamed "Streak Master" badge to "Streak Freak!" for more personality.
- Upgraded frontend with material-changing library card effects, stamp animations, and barcode scan animations.
- Enhanced volume review UX with pristine volume detection and disabled states.
- Improved rate limiting to exclude static files and return styled 429 pages for web requests and JSON for API requests.

### Fixed
- How-to-play: overdue review XP corrected from +25 to +10 (matching 5 x 2 multiplier).
- How-to-play: badge tier count corrected from "three tiers" to "two tiers".
- How-to-play: Dewey Devotee description updated to match code (removed "for 7 days").

### Removed
- Catalog search feature: removed `POST /api/catalog/search` endpoint and `/search` web route. Autocomplete retained via `GET /api/catalog/autocomplete`.
- Removed `scroll`, `trophy` icons and extra avatar SVGs (avatar_09 through avatar_12).

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
