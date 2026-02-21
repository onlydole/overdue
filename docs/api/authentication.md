---
title: Authentication
category: api
---

# Authentication

Overdue uses JWT tokens ("library cards") for authentication. All write operations require a valid library card.

## Overview

Library cards are issued when a librarian logs in and expire after 24 hours. Include the token in the `Authorization` header as a Bearer token.

## Registration

Create a new librarian account:

```bash
curl -X POST http://localhost:8000/api/librarians/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "ada",
    "email": "ada@example.com",
    "password": "lovelace1815"
  }'
```

**Requirements:**
- Username: 3-100 characters, unique
- Email: valid email format, unique
- Password: minimum 8 characters

## Login

Obtain a library card:

```bash
curl -X POST http://localhost:8000/api/librarians/login \
  -H "Content-Type: application/json" \
  -d '{"username": "ada", "password": "lovelace1815"}'
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 86400
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
- **Expiry:** 24 hours (configurable via `OVERDUE_TOKEN_EXPIRY_MINUTES`)
- **Payload:** librarian ID, username, role

## Refreshing your library card

Library cards can be refreshed before they expire:

```bash
curl -X POST http://localhost:8000/api/librarians/refresh \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..."
```

This returns a new library card with a fresh expiry.

## Roles and permissions

Overdue uses a rank-based permission system. See the [gameplay guide](../guides/gameplay.md) for rank details.

| Role | Permissions |
|---|---|
| Page | Read volumes, create volumes on existing shelves |
| Shelver | All Page permissions + create shelves |
| Librarian | All Shelver permissions + manage other librarians' volumes |
| Archivist | All Librarian permissions + archive and restore volumes |
| Head Librarian | Full admin access |

## Error responses

- **401:** "You'll need a library card to access the stacks." (missing or invalid token)
- **401:** "Your library card has expired. Renew at POST /librarians/login." (expired token)
- **403:** "Only the head librarian has access to the restricted section." (insufficient role)
