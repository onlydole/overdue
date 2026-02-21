---
title: API Endpoints
category: api
---

# API Endpoints

All API endpoints are prefixed with `/api`.

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
