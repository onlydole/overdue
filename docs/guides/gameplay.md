---
title: Gameplay Guide
category: guides
---

# Gameplay Guide

Overdue isn't just a knowledge base -- it's a game. Keep your library healthy, earn XP, level up, and compete with fellow librarians.

## The game loop

1. **Shelve** new volumes of knowledge
2. Knowledge accumulates **dust** over time (Dewey Score decays)
3. **Review** volumes to keep them fresh
4. Earn **pages read** (XP) for your efforts
5. Level up your **rank** and unlock **badges**
6. Maintain your **review streak** for bonus pages

## Pages read (XP)

Every action in the library earns you "pages read" -- your experience points.

| Action | Pages earned |
|---|---|
| Shelve a new volume | +10 |
| Review an overdue volume | +25 |
| Review a current volume | +5 |
| Daily streak bonus | +15/day |
| All volumes on a shelf above Dewey 75 | +50 (shelf bonus) |

## Ranks

As you accumulate pages read, you level up through the librarian ranks:

| Rank | Pages required | Perks |
|---|---|---|
| Page | 0 | Basic access |
| Shelver | 100 | Can create shelves |
| Librarian | 500 | Can manage other librarians' volumes |
| Archivist | 2,000 | Can archive and restore |
| Head Librarian | 5,000 | Full admin access |

## Badges

Badges are achievements earned by reaching specific milestones:

| Badge | Description |
|---|---|
| First Shelve | Created your first volume |
| Dust Buster | Reviewed 10 overdue volumes |
| Streak Master | 7-day review streak |
| Pristine Stacks | All volumes above Dewey 75 at once |
| Encyclopedist | 50 volumes authored |
| Night Owl | Reviewed a volume after midnight |
| Speed Reader | Reviewed 5 volumes in under a minute |
| Completionist | Earned all other badges |

## Streaks

Review at least one volume each day to maintain your streak. The streak counter resets if you miss a day. Each day you maintain the streak, you earn +15 bonus pages.

## Reading Room mood

The library's mood reflects the overall health of your knowledge collection:

| Average Dewey Score | Mood | Visual |
|---|---|---|
| 80-100 | Quiet study | Warm golden light, soft ambient sounds |
| 60-79 | Gentle hum | Normal lighting, slight bustle |
| 40-59 | Getting noisy | Flickering lights, books slightly askew |
| 20-39 | Call for order | Red accents, warning indicators |
| 0-19 | Closed for renovation | Dimmed, urgent status |

## Avatars

When you register, you choose from 12 unique pixel art librarian avatars. Your avatar appears on your profile, the leaderboard, and in the navigation bar. Each avatar has a distinct look -- different skin tones, hairstyles, outfits, and accessories.

## AI Bot players

The leaderboard includes AI bot players that simulate library activity. Bots are marked with a robot indicator so you can tell them apart from real players. Their XP shifts each time the server restarts, keeping competition dynamic.

Bots come in three difficulty levels: **casual** (low activity), **diligent** (regular reviews), and **obsessive** (power users). See the [Bot Players guide](bots.md) for CLI management commands.

## API endpoints

- `GET /api/librarians/me/xp` -- Your XP summary, rank, and recent awards
- `GET /api/librarians/me/badges` -- Your earned badges
- `GET /api/librarians/me/streak` -- Your current streak info
- `GET /api/librarians/leaderboard` -- Top librarians by pages read
