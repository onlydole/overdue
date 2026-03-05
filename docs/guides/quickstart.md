---
title: Quick Start
category: guides
---

# Quick Start

Get your library open for business in under two minutes.

## 1. Launch with Docker Compose

```bash
git clone https://github.com/onlydole/overdue.git
cd overdue
docker compose up --build
```

That's it. The database is created, demo shelves and volumes are seeded, bot players are active, and the server is running. Open `http://localhost:8000`.

## 2. Register a librarian

Visit `http://localhost:8000/register` in your browser, pick an avatar, and create your account. You now have a library card.

## 3. Shelve your first volume

Navigate to any shelf and click **New Volume**. Give it a title and some content -- this is knowledge you want to keep fresh.

## 4. Watch the dust settle

Head to the Reading Room (`http://localhost:8000`). Your volume's Dewey Score is already ticking down. The clock is running.

## 5. Review before it's too late

Open your volume and hit **Review** (or press `Enter`). The score resets to 100, you earn XP, and your streak begins.

## 6. Check the leaderboard

Visit `/leaderboard` to see where you stack up against the bot players. They're already accumulating XP. Can you catch them?

## Using the CLI

Docker Compose commands for managing the library:

```bash
# Shuffle the bot leaderboard
docker compose exec overdue overdue bots simulate

# Add more bots to the competition
docker compose exec overdue overdue bots create obsessive --count 2

# Check library statistics
docker compose exec overdue overdue stats

# Re-seed demo data
docker compose exec overdue overdue seed demo
```

## Using the API

If you prefer curl, register and get a library card first:

```bash
# Register
curl -X POST http://localhost:8000/api/librarians/register \
  -H "Content-Type: application/json" \
  -d '{"username": "ada", "email": "ada@example.com", "password": "lovelace1815"}'

# Login (get your library card)
curl -X POST http://localhost:8000/api/librarians/login \
  -H "Content-Type: application/json" \
  -d '{"username": "ada", "password": "lovelace1815"}'

# Check the library's mood
curl http://localhost:8000/api/reading-room/health
```

## Next steps

- [Gameplay Guide](gameplay.md) -- XP, ranks, badges, streaks, and mood
- [Configuration](configuration.md) -- Tune decay rates and game balance
- [Bot Players](bots.md) -- Manage your AI competition
- [API Endpoints](../api/endpoints.md) -- Full endpoint reference
- [Architecture](../architecture/overview.md) -- How it all fits together
