---
title: Configuration
category: guides
---

# Configuration

Overdue uses environment variables for configuration. All variables are prefixed with `OVERDUE_`.

## Environment variables

| Variable | Default | Description |
|---|---|---|
| `OVERDUE_APP_NAME` | `Overdue` | Application display name |
| `OVERDUE_DEBUG` | `false` | Enable debug mode |
| `OVERDUE_DATABASE_URL` | `sqlite+aiosqlite:///./overdue.db` | Database connection string |
| `OVERDUE_SECRET_KEY` | `change-me-in-production` | Secret key for JWT signing |
| `OVERDUE_TOKEN_EXPIRY_MINUTES` | `1440` | Library card (JWT) expiry in minutes (24 hours) |
| `OVERDUE_CORS_ORIGINS` | `["*"]` | Allowed CORS origins |
| `OVERDUE_HOST` | `0.0.0.0` | Server bind address |
| `OVERDUE_PORT` | `8000` | Server port |

## Example `.env` file

```bash
OVERDUE_DEBUG=true
OVERDUE_SECRET_KEY=my-secret-key-for-development
OVERDUE_DATABASE_URL=sqlite+aiosqlite:///./dev.db
```

## Production notes

- Always set a strong `OVERDUE_SECRET_KEY` in production
- Use a production database like PostgreSQL instead of SQLite
- Set `OVERDUE_CORS_ORIGINS` to your frontend domain
- Set `OVERDUE_DEBUG=false`
