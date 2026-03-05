---
title: Configuration
category: guides
---

# Configuration

Overdue uses environment variables for configuration. All variables are prefixed with `OVERDUE_`. With Docker Compose, set them in `docker-compose.yml` under `environment`.

## Environment variables

### Core

| Variable | Default | Description |
|---|---|---|
| `OVERDUE_APP_NAME` | `Overdue` | Application display name |
| `OVERDUE_DEBUG` | `false` | Enable debug mode |
| `OVERDUE_DATABASE_URL` | `sqlite+aiosqlite:///./overdue.db` | Database connection string |
| `OVERDUE_SECRET_KEY` | insecure default | Secret key for JWT signing -- **set a strong value in production** |
| `OVERDUE_HOST` | `0.0.0.0` | Server bind address |
| `OVERDUE_PORT` | `8000` | Server port |
| `OVERDUE_ALLOWED_ORIGINS` | `["*"]` | CORS allowed origins |

### Authentication

| Variable | Default | Description |
|---|---|---|
| `OVERDUE_TOKEN_EXPIRY_MINUTES` | `60` | Library card (JWT) expiry in minutes |
| `OVERDUE_TOKEN_REFRESH_WINDOW_MINUTES` | `15` | Window before expiry when refresh is allowed |
| `OVERDUE_WEBHOOK_SECRET` | `""` | Secret for bulletin (webhook) signature verification |

### Game balance

These control how fast the game moves. The defaults create a fast demo experience. For realistic daily gameplay, set decay to `86400` and streak cooldown to `86400`.

| Variable | Default | Description |
|---|---|---|
| `OVERDUE_DEWEY_DECAY_SECONDS` | `10` | Seconds per decay unit (10 = fast demo, 86400 = daily) |
| `OVERDUE_DEWEY_DECAY_RATE` | `3` | Points lost per decay unit |
| `OVERDUE_DEWEY_RECALC_INTERVAL_MINUTES` | `15` | Background recalculation interval |
| `OVERDUE_STREAK_COOLDOWN_SECONDS` | `5` | Seconds between reviews for streak eligibility (86400 = daily) |
| `OVERDUE_SEARCH_MIN_SCORE` | `0.3` | Minimum catalog search relevance score |
| `OVERDUE_MAX_VOLUME_SIZE_KB` | `512` | Maximum volume content size in KB |

## Example `.env` file

```bash
OVERDUE_DEBUG=true
OVERDUE_SECRET_KEY=my-secret-key-for-development
OVERDUE_DATABASE_URL=sqlite+aiosqlite:///./dev.db
OVERDUE_DEWEY_DECAY_SECONDS=86400
OVERDUE_STREAK_COOLDOWN_SECONDS=86400
```

## Docker Compose

The `docker-compose.yml` includes sensible defaults. Override them in the `environment` section:

```yaml
services:
  overdue:
    environment:
      OVERDUE_SECRET_KEY: "your-production-secret"
      OVERDUE_DEWEY_DECAY_SECONDS: "86400"
      OVERDUE_STREAK_COOLDOWN_SECONDS: "86400"
```

## Production notes

- Always set a strong `OVERDUE_SECRET_KEY` -- the default is insecure
- Use a production database like PostgreSQL instead of SQLite
- Set `OVERDUE_ALLOWED_ORIGINS` to your frontend domain(s)
- Set `OVERDUE_DEBUG=false`
- Set `OVERDUE_DEWEY_DECAY_SECONDS=86400` and `OVERDUE_STREAK_COOLDOWN_SECONDS=86400` for daily gameplay
