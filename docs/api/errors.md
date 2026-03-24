---
title: Error Reference
category: api
---

# Error Reference

All errors in Overdue are called "incidents" and follow a consistent format:

```json
{
  "incident": {
    "code": "TS-001",
    "detail": "That volume isn't on any of our shelves. Check the catalog and try again."
  }
}
```

## Incident codes

| Code | HTTP Status | Description | Message |
|---|---|---|---|
| TS-001 | 404 | Volume not found | "That volume isn't on any of our shelves. Check the catalog and try again." |
| TS-002 | 404 | Shelf not found | "That shelf isn't in our library. Check the catalog and try again." |
| TS-003 | 401 | Invalid library card | "You'll need a library card to access the stacks." |
| TS-004 | 401 | Expired library card | "Your library card has expired. Renew at POST /librarians/login." |
| TS-005 | 403 | Insufficient permissions | "Only the head librarian has access to the restricted section." |
| TS-006 | 409 | Duplicate entry | "A volume with that title is already shelved in this section." |
| TS-007 | 429 | Rate limit exceeded | "Quiet hours, please. Try again in {retry_after}s." |
| TS-008 | 422 | Validation error | Varies by field |
| TS-009 | 404 | Bulletin not found | "That bulletin subscription was not found." |
| TS-010 | 502 | Webhook delivery failed | "The bulletin could not be delivered to the subscriber." |
| TS-011 | 413 | Volume too large | "The volume content exceeds the maximum allowed size." |
| TS-012 | 410 | Deprecated feature used | "A deprecated feature or config option was used." |

## Rate limit errors (TS-007)

When you exceed the rate limit, the response includes a `Retry-After` header indicating how many seconds to wait:

```
HTTP/1.1 429 Too Many Requests
Retry-After: 45

{
  "incident": {
    "code": "TS-007",
    "detail": "Quiet hours, please. Try again in 45s."
  }
}
```
