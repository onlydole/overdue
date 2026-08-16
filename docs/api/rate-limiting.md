---
title: Rate Limiting
category: api
freshness:
  ttl_days: 90
  sources:
    - "src/main.py"
    - "src/config/quiet_hours.py"
---

# Rate Limiting (Quiet Hours)

Overdue enforces "quiet hours" to prevent abuse. The limiter is implemented as the `quiet_hours_middleware` in `src/main.py`: a fixed limit of 60 requests per minute per client IP, tracked in-memory over a sliding 60-second window. Requests to `/static` and `/favicon.ico` are exempt so asset loading never blocks the app.

## Limits

| Parameter | Value |
|---|---|
| Requests per minute | 60 (fixed, per client IP) |
| Window | 60 seconds (sliding) |
| Exempt paths | `/static/*`, `/favicon.ico` |

## Response headers

When rate limited, the response includes:

- **HTTP Status:** `429 Too Many Requests`
- **Retry-After:** Number of seconds until the next request will be accepted

API requests (paths under `/api`) receive a JSON body; web requests receive a styled HTML page.

## Example

```
HTTP/1.1 429 Too Many Requests
Retry-After: 12

{
  "detail": "Quiet hours, please. Try again in 12s."
}
```

## Configuration

The limit is defined in `src/config/defaults.py`:

- `QUIET_HOURS_REQUESTS_PER_MINUTE` -- Maximum requests per minute (default: 60)
- `QUIET_HOURS_BURST` -- Burst allowance (default: 10). **Not implemented:** this constant is carried on the `QuietHoursPolicy` dataclass in `src/config/quiet_hours.py` but the live middleware does not use it.
