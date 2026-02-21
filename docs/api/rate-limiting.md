---
title: Rate Limiting
category: api
---

# Rate Limiting (Quiet Hours)

Overdue enforces "quiet hours" to prevent abuse. Rate limits apply per client IP address.

## Limits

| Parameter | Value |
|---|---|
| Requests per minute | 60 |
| Window | 60 seconds (sliding) |

## Response headers

When rate limited, the response includes:

- **HTTP Status:** `429 Too Many Requests`
- **Retry-After:** Number of seconds until the next request will be accepted

## Example

```
HTTP/1.1 429 Too Many Requests
Retry-After: 12

{
  "incident": {
    "code": "TS-007",
    "detail": "Quiet hours, please. Try again in 12s."
  }
}
```

## Configuration

Rate limits are defined in `src/config/defaults.py` and can be adjusted:

- `QUIET_HOURS_REQUESTS_PER_MINUTE` -- Maximum requests per minute (default: 60)
- `QUIET_HOURS_BURST` -- Burst allowance (default: 10)
