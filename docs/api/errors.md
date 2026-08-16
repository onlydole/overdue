---
title: Error Reference
category: api
freshness:
  ttl_days: 90
  sources:
    - "src/errors/codes.py"
    - "src/errors/handlers.py"
    - "src/errors/incidents.py"
    - "src/main.py"
---

# Error Reference

Most errors in Overdue are plain FastAPI HTTP errors. They are serialized as a bare `detail` object with no incident code:

```json
{
  "detail": "That volume isn't on any of our shelves. Check the catalog and try again."
}
```

For example, the duplicate-shelf conflict returns:

```json
{
  "detail": "A shelf with that name already exists."
}
```

with status 409, and validation failures use FastAPI's standard 422 response.

## The incident envelope

A small set of errors are "incidents" -- subclasses of `LibraryIncident` rendered by the incident handler with a coded envelope:

```json
{
  "incident": {
    "code": "TS-005",
    "detail": "Only the volume's keeper or a head librarian may change it."
  }
}
```

Only two incident codes are wired to live responses:

| Code | HTTP Status | Raised as | Messages |
|---|---|---|---|
| TS-005 | 403 | `InsufficientPermissions` | Resource-specific, e.g. "Only the volume's keeper or a head librarian may change it.", "Only the shelf's creator or a head librarian may delete it." |
| TS-011 | 413 | `VolumeTooLarge` | "That volume is too thick for our shelves. Maximum: {max_size_kb}KB." |

## Incident code registry

The full registry lives in `src/errors/codes.py` for tracking and documentation. Most codes are **registry-only**: the situations they describe return plain `detail` responses (or nothing at all) rather than incident envelopes.

| Code | HTTP Status | Description | Wired to a live response? |
|---|---|---|---|
| TS-001 | 404 | Volume not found | No -- routes raise a plain 404 with a `detail` message |
| TS-002 | 404 | Shelf not found | No -- plain 404 `detail` message |
| TS-003 | 401 | Invalid library card | No -- plain 401 `detail` message |
| TS-004 | 401 | Expired library card | No -- plain 401 `detail` message |
| TS-005 | 403 | Insufficient permissions | **Yes** -- incident envelope (see above) |
| TS-006 | 409 | Duplicate entry | No -- plain 409, e.g. "A shelf with that name already exists." |
| TS-007 | 429 | Rate limit exceeded | No -- written inline by the quiet-hours middleware (see below) |
| TS-008 | 422 | Validation error | No -- FastAPI's standard validation response |
| TS-009 | 404 | Bulletin not found | No -- registry-only; no exception class exists |
| TS-010 | 502 | Webhook delivery failed | No -- registry-only; no exception class exists |
| TS-011 | 413 | Volume too large | **Yes** -- incident envelope (see above) |
| TS-012 | 400 | Deprecated feature used | No -- `DeprecatedFeature` exists but is never raised; deprecations go through Python's warnings module |

## Rate limiting (429)

Quiet-hours responses are written directly by the rate-limiting middleware in `src/main.py`, not by the incident handler. The shape depends on the path:

**API paths** (`/api/...`) get JSON with a `Retry-After` header:

```
HTTP/1.1 429 Too Many Requests
Retry-After: 45

{
  "detail": "Quiet hours, please. Try again in 45s."
}
```

**Web paths** get a full pixel-art "Quiet Hours" HTML page with a live countdown (and the same `Retry-After` header) instead of JSON.
