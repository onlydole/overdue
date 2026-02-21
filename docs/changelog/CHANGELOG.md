---
title: Changelog
category: changelog
---

# Changelog

All notable changes to Overdue will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/), and this project adheres to [Semantic Versioning](https://semver.org/).

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
