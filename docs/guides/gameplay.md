---
title: Gameplay Guide
category: guides
---

# Gameplay Guide

Overdue isn't just a knowledge base -- it's a game where your memory is the battlefield. Every volume you shelve starts pristine and immediately begins gathering dust. Your job: fight the decay, climb the ranks, and keep the library from descending into chaos.

## The game loop

1. **Shelve** new volumes of knowledge
2. Knowledge accumulates **dust** over time (Dewey Score decays)
3. **Review** volumes to brush off the dust and reset their score to 100
4. Earn **pages read** (XP) for your efforts
5. Level up your **rank** and unlock **badges**
6. Maintain your **review streak** for bonus pages
7. Watch the Reading Room **mood** shift based on your library's health

## Pages read (XP)

Every action in the library earns you "pages read" -- your experience points. Overdue volumes are worth double.

| Action | XP earned |
|---|---|
| Shelve a new volume | +10 XP (10 pages) |
| Review a current volume | +5 XP (5 pages) |
| Review an overdue volume | +10 XP (10 pages, 2x multiplier) |
| Rescue bonus (for overdue review) | +20 XP (20 pages) |
| Daily streak bonus | +15 XP/day (15 pages) |
| All volumes on a shelf above Dewey 75 | +50 XP (50 pages, shelf bonus) |

## Ranks

As you accumulate pages read, you level up through the librarian ranks:

| Rank | Pages required | Perks |
|---|---|---|
| Page | 0 | Basic access |
| Shelver | 100 | Can create shelves |
| Librarian | 500 | Can manage other librarians' volumes |
| Archivist | 2,000 | Can archive and restore |
| Head Librarian | 5,000 | Full admin access |
| Living Document | 10,000 | The ultimate librarian: you've read so many pages you've become self-updating |

## Badges

Badges are achievements you unlock by hitting milestones. They come in two tiers: **Common** (consistent effort) and **Rare** (serious dedication).

### Common badges

| Badge | How to earn it |
|---|---|
| First Shelve | Create your first volume |
| Dust Buster | Review 10 overdue volumes |
| Streak Freak! | Hit a 7-day review streak |
| Pristine Stacks | Get all your volumes above Dewey 75 at once |
| Encyclopedist | Author 50 volumes |
| Night Owl | Review a volume after midnight |
| Speed Reader | Review 5 volumes in under a minute |
| Completionist | Earn every other badge |

### Rare badges

| Badge | How to earn it |
|---|---|
| Marathon Reader | Maintain a 30-day review streak |
| Dewey Devotee | Maintain an average Dewey Score above 90 |
| Centurion | Review 100 volumes total |

## Streaks

Review at least one volume each day to keep your streak alive. Every day you maintain it, you earn +15 bonus pages. Miss a day and the counter resets to zero. Streaks show up on the leaderboard, so everyone knows who's been putting in the work.

Hit 7 days for the Streak Freak! badge. Hit 30 and you earn the rare Marathon Reader.

## The Dewey Score

Every volume has a freshness score from 0 to 100. It starts at 100 when you create or review it, then decays over time.

| Score | Status | What it means |
|---|---|---|
| 75-100 | Pristine | Freshly reviewed, perfectly current |
| 50-74 | Good | Slightly dusty, still reliable |
| 25-49 | Dusty | Getting stale, needs attention soon |
| 0-24 | Overdue | Significantly outdated -- review immediately |

## Reading Room mood

The library's ambient atmosphere reflects your collective Dewey Scores. Keep your stacks healthy and the mood stays calm. Let things decay and the atmosphere turns hostile.

| Average Dewey Score | Mood | What happens |
|---|---|---|
| 80-100 | Quiet Study | Warm golden light, everything is serene |
| 60-79 | Gentle Hum | Normal lighting, a slight bustle in the air |
| 40-59 | Getting Noisy | Flickering lights, books slightly askew |
| 20-39 | Call for Order | Red accents, warning indicators everywhere |
| 0-19 | Closed for Renovation | The library is in crisis. Review everything! |

## Keyboard shortcuts

Navigate the library at speed with keyboard shortcuts (desktop browsers):

| Page | Key | Action |
|---|---|---|
| Volume detail | `Enter` | Review / next volume / done (priority order) |
| Volume detail | `Escape` / `ArrowLeft` | Back to shelf |
| Volume detail | `ArrowRight` | Next volume |
| Shelves listing | `Enter` | Open the most overdue shelf |

## Avatars

When you register, you choose from 8 unique pixel art heroic librarian avatars -- each with a distinct silhouette, palette, and lore. Your avatar appears on your profile, the leaderboard, and in the navigation bar.

## AI bot players

The leaderboard includes AI bot players that simulate library activity. Bots are marked with a robot indicator so you can tell them apart from real players. Their XP shifts each time the server restarts, keeping competition dynamic.

Bots come in three difficulty levels: **casual** (low activity), **diligent** (regular reviews), and **obsessive** (power users). See the [Bot Players guide](bots.md) for CLI management commands.

## API endpoints

- `GET /api/librarians/me/xp` -- Your XP summary, rank, and recent awards
- `GET /api/librarians/me/badges` -- Your earned badges
- `GET /api/librarians/me/streak` -- Your current streak info
- `GET /api/librarians/leaderboard` -- Top librarians by pages read
