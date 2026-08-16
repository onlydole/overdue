---
title: Authentication
category: api
critical: true
freshness:
  ttl_days: 90
  sources:
    - "src/auth/library_card.py"
    - "src/auth/web_session.py"
    - "src/auth/librarian.py"
    - "src/auth/circulation.py"
---

# Authentication

Overdue uses JWT tokens ("library cards") for authentication. All write operations require a valid library card.

## Overview

Library cards are issued when a librarian logs in and expire after 1 hour (60 minutes). Include the token in the `Authorization` header as a Bearer token.

## Registration

Create a new librarian account:

```bash
curl -X POST http://localhost:8000/api/librarians/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "ada",
    "email": "ada@example.com",
    "password": "Lovelace1815!"
  }'
```

**Requirements:**
- Username: 3-100 characters, unique
- Email: valid email format, unique
- Password: at least 8 characters and must include an uppercase letter, a
  lowercase letter, a digit, and a special character (`@$!%*?&`)

## Login

Obtain a library card:

```bash
curl -X POST http://localhost:8000/api/librarians/login \
  -H "Content-Type: application/json" \
  -d '{"username": "ada", "password": "Lovelace1815!"}'
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

## Using your library card

Include the token in the `Authorization` header:

```bash
curl -X POST http://localhost:8000/api/volumes/ \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..." \
  -H "Content-Type: application/json" \
  -d '{"title": "My Volume", "content": "...", "shelf_id": 1}'
```

## Token details

- **Algorithm:** HS256
- **Expiry:** 60 minutes (configurable via `OVERDUE_TOKEN_EXPIRY_MINUTES`)
- **Payload:** librarian ID, username, role

## Refreshing your library card

Library cards can be refreshed before they expire:

```bash
curl -X POST http://localhost:8000/api/librarians/refresh \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..."
```

This returns a new library card with a fresh expiry.

## Roles and permissions

Authorization is **object-level**, based on who created a resource. Any librarian
with a valid library card can read the library and create their own shelves and
volumes. Mutating or deleting an existing resource is restricted to its owner:

| Action | Who may perform it |
|---|---|
| Read volumes/shelves, search the catalog | Anyone (no card required) |
| Create a shelf or volume | Any librarian with a library card |
| Review any volume | Any librarian with a library card |
| Update / archive a volume | The volume's **author**, or a **Head Librarian** |
| Update / delete a shelf | The shelf's **creator**, or a **Head Librarian** |

"Head Librarian" is the rank earned at 5000 pages read (see the
[gameplay guide](../guides/gameplay.md)); reaching it grants library-wide
curation rights. Roles are carried in the signed library card, so they cannot be
forged as long as `OVERDUE_SECRET_KEY` is set to a strong value.

## Error responses

- **401:** "You'll need a library card to access the stacks." (missing or invalid token)
- **401:** "Your library card has expired. Renew at POST /librarians/login." (expired token)
- **403:** "Only the keeper of this item or a head librarian may change it." (mutating a resource you don't own; returned as a `TS-005` incident)
