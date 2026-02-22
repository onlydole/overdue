---
title: API Endpoints
category: api
---

# API Endpoints

All API endpoints are prefixed with `/api`. Endpoints marked with a lock icon require a valid library card (JWT token) in the `Authorization` header.

## Librarians

### `POST /api/librarians/register`
Register a new librarian account.

**Request body:**
```json
{
  "username": "ada",
  "email": "ada@example.com",
  "password": "lovelace1815"
}
```

**Response:** `201 Created` with the librarian profile.

### `POST /api/librarians/login`
Log in and receive a library card (JWT token).

**Request body:**
```json
{
  "username": "ada",
  "password": "lovelace1815"
}
```

**Response:** Library card with `access_token`, `token_type`, and `expires_in`.

### `GET /api/librarians/me/xp`
Get the authenticated librarian's XP summary, rank, and recent awards. Requires library card.

### `GET /api/librarians/me/badges`
Get the authenticated librarian's earned badges. Requires library card.

### `GET /api/librarians/me/streak`
Get the authenticated librarian's review streak info. Requires library card.

### `GET /api/librarians/leaderboard`
Get the top librarians ranked by pages read.

**Query parameters:**
- `limit` (int, default: 10) -- Number of entries to return

## Volumes

### `POST /api/volumes/`
Create a new volume (shelve knowledge).

**Request body:**
```json
{
  "title": "The Art of Code Review",
  "content": "A comprehensive guide...",
  "shelf_id": 1,
  "bookmarks": ["code-review", "best-practices"]
}
```

**Response:** `201 Created` with the new volume including its Dewey Score.

### `GET /api/volumes/`
List all volumes in the library.

**Query parameters:**
- `page` (int, default: 1) -- Page number
- `per_page` (int, default: 20) -- Items per page
- `shelf_id` (int, optional) -- Filter by shelf

**Response:** Paginated list of volumes.

### `GET /api/volumes/{volume_id}`
Get a specific volume by ID.

**Response:** Volume with current Dewey Score.

### `PATCH /api/volumes/{volume_id}`
Update a volume's title, content, shelf, or bookmarks.

**Request body:** Any subset of volume fields.

**Response:** Updated volume.

### `DELETE /api/volumes/{volume_id}`
Archive a volume (soft delete).

**Response:** `204 No Content`

### `POST /api/volumes/{volume_id}/review`
Review a volume, resetting its Dewey Score to 100 (pristine).

**Response:** Updated volume with reset score.

## Shelves

### `POST /api/shelves/`
Create a new shelf.

**Request body:**
```json
{
  "name": "Software Engineering",
  "description": "Volumes about software development practices."
}
```

**Response:** `201 Created` with the new shelf.

### `GET /api/shelves/`
List all shelves with volume counts and average Dewey Scores.

### `GET /api/shelves/{shelf_id}`
Get a specific shelf by ID.

### `PATCH /api/shelves/{shelf_id}`
Update a shelf's name or description.

### `DELETE /api/shelves/{shelf_id}`
Delete a shelf and all its volumes.

**Response:** `204 No Content`

## Catalog

### `GET /api/catalog/suggest`
Get autocomplete suggestions from volume titles.

**Query parameters:**
- `q` (string, required) -- Search query
- `limit` (int, default: 5) -- Maximum suggestions

**Response:** List of title suggestions.

## Reading Room

### `GET /api/reading-room/health`
Get the library's overall health status.

**Response:**
```json
{
  "status": "healthy",
  "mood": "Quiet study",
  "description": "Warm golden light fills the reading room.",
  "total_volumes": 42,
  "overdue_volumes": 3,
  "average_dewey_score": 82.5
}
```

### `GET /api/reading-room/overdue`
Get a report of volumes needing review.

**Response:** Lists of overdue volumes and volumes needing attention with their Dewey Scores.

## Bulletins

### `POST /api/bulletins/`
Subscribe to webhook notifications for library events.

### `GET /api/bulletins/`
List your webhook subscriptions.

### `DELETE /api/bulletins/{bulletin_id}`
Remove a webhook subscription.
