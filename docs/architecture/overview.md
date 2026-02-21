---
title: Architecture Overview
category: architecture
---

# Architecture Overview

Overdue follows a layered architecture with clear separation of concerns.

## Layers

```
┌─────────────────────────────────┐
│         Web Dashboard           │  Jinja2 + HTMX templates
├─────────────────────────────────┤
│           API Layer             │  FastAPI routers
├─────────────────────────────────┤
│        Game Mechanics           │  XP, badges, streaks, mood
├─────────────────────────────────┤
│       Business Logic            │  Dewey Scores, catalog
├─────────────────────────────────┤
│         Data Layer              │  SQLAlchemy async + Pydantic
├─────────────────────────────────┤
│          Database               │  SQLite (dev) / PostgreSQL
└─────────────────────────────────┘
```

## Module responsibilities

### `src/api/`
REST API endpoints organized by domain. Each router handles a specific resource type (volumes, shelves, catalog, reading room).

### `src/auth/`
Authentication and authorization. Librarian registration and login, JWT "library card" generation, and role-based access control via the circulation desk.

### `src/config/`
Application settings (via pydantic-settings), constants (Dewey thresholds, XP values, rank definitions), and rate limiting configuration.

### `src/game/`
Game mechanic calculations. XP awarding, rank progression, badge tracking, streak management, and reading room mood calculation based on aggregate Dewey Scores.

### `src/models/`
Pydantic models for request/response validation and SQLAlchemy table definitions for persistence.

### `src/db/`
Database engine configuration and session management using SQLAlchemy's async engine.

### `src/web/`
Server-side rendered dashboard routes. Returns HTML responses using Jinja2 templates with HTMX for interactive updates.

### `src/errors/`
Library-themed exception classes and FastAPI exception handlers. Each error type has a unique code (TS-001+) and a friendly message.

### `src/cli/`
Typer-based command-line interface for managing the library without the web UI.

## Data flow

1. Request arrives at API or web route
2. Authentication middleware validates the library card (JWT)
3. Route handler processes the request
4. Game mechanics are triggered where appropriate (XP, badges, streaks)
5. Data is persisted via SQLAlchemy
6. Response is returned (JSON for API, HTML for web)

## Dewey Score calculation

Dewey Scores decay over time. Each volume starts with a score of 100 (pristine) and loses points daily based on the configured decay rate. Reviewing a volume resets its score to 100. The calculation is synchronous -- scores are computed on read based on the time elapsed since the last review.
