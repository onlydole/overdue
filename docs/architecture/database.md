---
title: Database Schema
category: architecture
freshness:
  ttl_days: 180
  sources:
    - "src/db/tables.py"
    - "src/db/engine.py"
    - "src/db/seed.py"
    - "src/models/*.py"
---

# Database Schema

Overdue persists state through SQLAlchemy 2.x with an async engine. Tables are declared in `src/db/tables.py` using the modern declarative base.

## Engine

`Base` is a DeclarativeBase subclass; every ORM class inherits from it. The async engine and AsyncSession factory live in `src/db/engine.py`. SQLite (aiosqlite) is the default, configurable via `OVERDUE_DATABASE_URL`.

## Tables

| Class | Table | Purpose |
|---|---|---|
| `VolumeRow` | `volumes` | Knowledge entries on a shelf |
| `ShelfRow` | `shelves` | Categorized container for volumes |
| `LibrarianRow` | `librarians` | Authenticated users (humans and bots) |
| `ReviewRow` | `reviews` | Each time a librarian reviews a volume |
| `XPLedgerRow` | `xp_ledger` | Append-only XP awards |
| `BadgeRow` | `badges` | Earned achievements |
| `StreakRow` | `streaks` | Per-librarian daily review streak |
| `BulletinRow` | `bulletins` | Webhook subscriptions |
| `volume_bookmarks` | `volume_bookmarks` | Many-to-many tag join (Table object, not ORM class) |

## Relationships

A `VolumeRow` belongs to one shelf (`ShelfRow`) and one author (`LibrarianRow`), and owns many reviews (`ReviewRow`) -- reviews cascade-delete with the volume. A `ShelfRow` owns many volumes; deleting a shelf cascades to the volumes on it. A `LibrarianRow` owns the volumes they created and the reviews they performed, with the same cascade semantics.

The relationship metadata lives directly on the ORM classes; see the `relationship(...)` assignments in `src/db/tables.py` for cascade rules and back-populates.

## Migrations

Schema lives entirely in `tables.py`; there is no Alembic migration history. On startup the engine calls `metadata.create_all`, which is safe for the alpha because no schema has ever been removed -- only additive changes have shipped. Adding a destructive change means introducing migrations; that work is not yet planned.

## Seeding

`src/db/seed.py` provides demo data (default shelves, sample volumes, bot players). It is invoked from the CLI (`overdue seed demo`) and from the FastAPI lifespan in development mode.
