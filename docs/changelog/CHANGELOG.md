---
title: Changelog
category: changelog
---

# Changelog

All notable changes to Overdue will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/), and this project adheres to [Semantic Versioning](https://semver.org/).

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
