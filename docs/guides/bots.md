---
title: AI Bot Players
category: guides
---

# AI Bot Players

Overdue includes AI bot players that populate the leaderboard with simulated activity. Bots create a dynamic competitive environment -- their XP shifts each time the server starts, keeping the leaderboard interesting.

## Overview

Bots are managed via CLI commands. Each bot has a **difficulty** profile that determines how active it is:

| Difficulty | XP Range | Typical Rank | Behavior |
|---|---|---|---|
| `casual` | 50--400 | Page / Shelver | Few volumes, short streaks, things decay |
| `diligent` | 400--1,500 | Librarian | Regular reviews, decent streaks |
| `obsessive` | 1,500--4,500 | Archivist+ | Many volumes, long streaks, high XP |

Bots appear on the leaderboard with a robot indicator so real players can distinguish them.

## Managing bots with Docker Compose

The recommended way to run CLI commands is through Docker Compose. This ensures the commands run against the same database the server uses.

### Add bots

```bash
# Add a single casual bot
docker compose exec overdue python -m src.cli.main bots add casual

# Add 3 diligent bots
docker compose exec overdue python -m src.cli.main bots add diligent --count 3

# Add an obsessive bot with a custom name
docker compose exec overdue python -m src.cli.main bots add obsessive --name overlord99
```

### List bots

```bash
docker compose exec overdue python -m src.cli.main bots list
```

Displays a table with each bot's username, difficulty, XP, rank, and avatar.

### Simulate activity

Bot activity is automatically simulated each time the server starts. You can also trigger it manually:

```bash
# Simulate all bots
docker compose exec overdue python -m src.cli.main bots simulate

# Simulate a specific bot
docker compose exec overdue python -m src.cli.main bots simulate --name bookworm42
```

Each simulation round awards XP, may add reviews, and updates streaks based on the bot's difficulty profile.

### Remove bots

```bash
# Remove a specific bot
docker compose exec overdue python -m src.cli.main bots remove bookworm42

# Remove all bots
docker compose exec overdue python -m src.cli.main bots remove --all
```

Removing a bot deletes all its related data (volumes, reviews, XP ledger, badges, streaks).

## Running locally (without Docker)

If you're running Overdue directly on your machine:

```bash
# Use the overdue CLI entry point
overdue bots add casual --count 2
overdue bots list
overdue bots simulate
overdue bots remove --all
```

## Seed bots

When the database is first created (auto-seed on startup), two bots are included automatically:

- **bookworm42** -- a casual bot
- **scholar_jane** -- a diligent bot

These provide an active leaderboard out of the box. You can remove them with `bots remove --all` and add your own mix.

## How simulation works

On each server startup, `simulate_bot_activity()` runs for all existing bots:

1. Each bot gains XP based on its difficulty tier
2. Bots may create new reviews on their volumes
3. Streaks are extended or reset (weighted by difficulty -- obsessive bots rarely lose streaks)
4. Ranks are recalculated if XP crosses a threshold

This means every server restart shuffles the leaderboard slightly, creating a living competitive environment.

## Bot avatars

Each bot is assigned a random pixel art avatar from the 12 available designs. These appear on the leaderboard and profile pages alongside the robot indicator.
