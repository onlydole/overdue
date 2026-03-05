"""AI bot player engine for generating simulated library activity.

Bots populate the leaderboard and create a sense of community in the
knowledge library.  Each bot has a difficulty profile that determines
its XP range, volume count, review frequency, streak behaviour, and
badge collection.
"""

import random
from datetime import datetime, timedelta

from passlib.context import CryptContext
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.tables import (
    LibrarianRow,
    VolumeRow,
    ShelfRow,
    ReviewRow,
    XPLedgerRow,
    BadgeRow,
    StreakRow,
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ---------------------------------------------------------------------------
# Rank thresholds (mirrored from src.config.defaults for self-containment)
# ---------------------------------------------------------------------------
_RANKS: list[tuple[str, int]] = [
    ("Page", 0),
    ("Shelver", 100),
    ("Librarian", 500),
    ("Archivist", 2000),
    ("Head Librarian", 5000),
]

# ---------------------------------------------------------------------------
# Difficulty profiles
# ---------------------------------------------------------------------------
DIFFICULTY_PROFILES: dict[str, dict] = {
    "casual": {
        "xp_range": (50, 400),
        "volume_range": (1, 3),
        "review_range": (2, 5),
        "streak_range": (0, 3),
        "badge_range": (0, 1),
        "activity_xp_range": (1, 5),
        "streak_continue_chance": 0.4,
    },
    "diligent": {
        "xp_range": (400, 1500),
        "volume_range": (3, 7),
        "review_range": (5, 15),
        "streak_range": (3, 12),
        "badge_range": (1, 3),
        "activity_xp_range": (5, 20),
        "streak_continue_chance": 0.7,
    },
    "obsessive": {
        "xp_range": (1500, 4500),
        "volume_range": (7, 15),
        "review_range": (15, 40),
        "streak_range": (10, 45),
        "badge_range": (3, 6),
        "activity_xp_range": (20, 50),
        "streak_continue_chance": 0.9,
    },
}

# ---------------------------------------------------------------------------
# Themed name pools
# ---------------------------------------------------------------------------
NAME_POOLS: dict[str, list[str]] = {
    "casual": [
        "bookworm", "reader", "browser", "skimmer", "flipper",
        "scanner", "glancer", "peeker", "leafer", "drifter",
    ],
    "diligent": [
        "scholar", "student", "learner", "seeker", "thinker",
        "noter", "studier", "curator", "indexer", "reviewer",
    ],
    "obsessive": [
        "archivist_x", "libmaster", "tome_lord", "page_sage",
        "book_dragon", "stack_king", "lore_keeper", "ink_wizard",
        "shelf_titan", "data_monk",
    ],
}

# Badges a bot can earn
_BOT_BADGE_POOL = ["First Shelve", "Night Owl", "Streak Freak!", "Dust Buster"]

# Sample content fragments for bot-authored volumes
_VOLUME_TITLES = [
    "Quick Notes on Sorting Algorithms",
    "My Thoughts on REST APIs",
    "Introduction to Graph Theory",
    "Basics of SQL Joins",
    "Understanding HTTP Status Codes",
    "A Short Guide to Regex",
    "Exploring Data Structures",
    "Tips for Code Reviews",
    "Concurrency Patterns Cheat Sheet",
    "Functional Programming Primer",
    "How DNS Works",
    "Container Orchestration 101",
    "Git Branching Strategies",
    "Memory Management Fundamentals",
    "Event-Driven Architecture Notes",
]

_VOLUME_CONTENT_MAP: dict[str, str] = {
    "Quick Notes on Sorting Algorithms": (
        "Merge sort guarantees O(n log n) but needs extra memory for the merge step. "
        "Quicksort is faster in practice thanks to cache locality, though worst-case is O(n²) "
        "if you pick bad pivots. For small arrays insertion sort wins due to low overhead."
    ),
    "My Thoughts on REST APIs": (
        "Keep endpoints noun-based and let HTTP verbs do the work — POST to create, "
        "PUT to replace, PATCH to update fields. Consistent error shapes save hours of "
        "client-side debugging. Always version your API from day one."
    ),
    "Introduction to Graph Theory": (
        "A graph is just vertices and edges, but the problems you can model are endless. "
        "BFS finds shortest paths in unweighted graphs; Dijkstra handles weights. "
        "Watch out for cycles when doing DFS — track visited nodes or you'll loop forever."
    ),
    "Basics of SQL Joins": (
        "INNER JOIN returns only matching rows from both tables. LEFT JOIN keeps all rows "
        "from the left table, filling NULLs where nothing matches on the right. "
        "Self-joins are surprisingly useful for hierarchical data like org charts."
    ),
    "Understanding HTTP Status Codes": (
        "2xx means success, 3xx means redirect, 4xx means the client messed up, 5xx means "
        "the server did. The most misused is 403 vs 401 — 401 means not authenticated, "
        "403 means authenticated but not authorized. 204 is great for successful deletes."
    ),
    "A Short Guide to Regex": (
        "Start simple: \\d for digits, \\w for word characters, . for anything. "
        "Quantifiers like + and * are greedy by default — append ? to make them lazy. "
        "Named capture groups (?P<name>...) make extraction code much more readable."
    ),
    "Exploring Data Structures": (
        "Hash maps give O(1) average lookup but degrade to O(n) with bad hash functions. "
        "Linked lists shine for frequent insertions at arbitrary positions. "
        "A heap is the go-to when you need fast access to the min or max element."
    ),
    "Tips for Code Reviews": (
        "Focus on correctness and clarity first, style nits last. Ask questions instead of "
        "making demands — 'What happens if this is null?' lands better than 'Fix this.' "
        "Small PRs get better reviews; aim for under 400 lines of diff."
    ),
    "Concurrency Patterns Cheat Sheet": (
        "Mutexes protect shared state but can deadlock if you lock in inconsistent order. "
        "Channels (Go-style) or async queues (Python) decouple producers from consumers. "
        "The actor model avoids shared state entirely — each actor owns its data."
    ),
    "Functional Programming Primer": (
        "Pure functions always return the same output for the same input and have no side "
        "effects. Map, filter, and reduce replace most imperative loops. Immutable data "
        "structures prevent whole categories of bugs but can need careful memory management."
    ),
    "How DNS Works": (
        "Your browser asks a recursive resolver, which walks the hierarchy: root servers → "
        "TLD servers → authoritative nameservers. Results get cached at each layer based on "
        "TTL values. Low TTLs enable fast failover but increase lookup traffic."
    ),
    "Container Orchestration 101": (
        "Containers package an app with its dependencies; orchestrators decide where and "
        "how many to run. Kubernetes uses pods as the scheduling unit — a pod can hold "
        "tightly coupled containers that share networking. Start with Deployments and Services."
    ),
    "Git Branching Strategies": (
        "Trunk-based development keeps branches short-lived and merges frequently. "
        "Feature branches isolate work but diverge fast if left open too long. "
        "Rebase before merge for a linear history; squash if the intermediate commits are noise."
    ),
    "Memory Management Fundamentals": (
        "Stack allocation is fast but limited to known sizes and scopes. Heap allocation "
        "is flexible but slower and needs explicit or GC-managed cleanup. Reference counting "
        "handles most cases but can't collect cycles without a tracing GC pass."
    ),
    "Event-Driven Architecture Notes": (
        "Events decouple producers from consumers — the order service publishes "
        "'order.placed' without knowing who listens. Use an event broker like Kafka or "
        "RabbitMQ for durability. Idempotent handlers are essential since events can arrive twice."
    ),
}

_GENERIC_CONTENT_POOL: list[str] = [
    (
        "Spent an hour digging into this topic and the key insight is that the abstractions "
        "we use shape how we think about the problem. Understanding the fundamentals pays "
        "off every time you hit an edge case the framework doesn't cover."
    ),
    (
        "The official documentation is solid but skips some practical gotchas. Bookmarking "
        "this for the next time I need a refresher. The examples in chapter three were "
        "particularly useful for building intuition."
    ),
    (
        "Tried to summarize the core concepts in a way that would make sense to someone "
        "seeing this for the first time. The mental model that helped me most was thinking "
        "of each layer as a contract between components."
    ),
    (
        "These notes are from a deep-dive study session. The tricky part is knowing when "
        "to apply each technique — context matters more than any single rule. Revisiting "
        "this periodically keeps the patterns fresh."
    ),
    (
        "Collected the most important points from several sources and distilled them here. "
        "The common thread is that simplicity beats cleverness. When in doubt, write the "
        "straightforward version first and optimize only if measurements demand it."
    ),
]


# =========================================================================
# Helper: rank lookup
# =========================================================================

def get_rank_for_xp(xp: int) -> str:
    """Return the rank name corresponding to the given XP total."""
    current_rank = _RANKS[0][0]
    for rank_name, threshold in _RANKS:
        if xp >= threshold:
            current_rank = rank_name
    return current_rank


# =========================================================================
# Create a single bot
# =========================================================================

async def create_bot(
    session: AsyncSession,
    difficulty: str,
    name: str | None = None,
) -> LibrarianRow:
    """Create a fully-realised bot librarian with history.

    The bot receives a randomised XP total, volumes on existing shelves,
    review records, streak data, badges, and XP ledger entries -- all
    consistent with the chosen *difficulty* profile.

    Parameters
    ----------
    session:
        An active async database session (caller manages the transaction).
    difficulty:
        One of ``"casual"``, ``"diligent"``, or ``"obsessive"``.
    name:
        Optional username override.  When ``None`` a themed name is picked
        from the difficulty pool with a random two-digit suffix.

    Returns
    -------
    LibrarianRow
        The newly created (and flushed) bot row.
    """
    if difficulty not in DIFFICULTY_PROFILES:
        raise ValueError(
            f"Unknown difficulty {difficulty!r}; "
            f"choose from {list(DIFFICULTY_PROFILES)}"
        )

    profile = DIFFICULTY_PROFILES[difficulty]

    # -- username ----------------------------------------------------------
    if name is None:
        base = random.choice(NAME_POOLS[difficulty])
        suffix = random.randint(10, 99)
        name = f"{base}{suffix}"

    # -- XP & rank ---------------------------------------------------------
    total_xp = random.randint(*profile["xp_range"])
    role = get_rank_for_xp(total_xp)

    # -- avatar ------------------------------------------------------------
    avatar_num = random.randint(1, 12)
    avatar_id = f"avatar_{avatar_num:02d}"

    # -- hashed password (bots cannot log in) ------------------------------
    dummy_password = f"bot-no-login-{random.randint(100000, 999999)}"
    hashed_password = pwd_context.hash(dummy_password)

    # -- create the librarian row ------------------------------------------
    bot = LibrarianRow(
        username=name,
        email=f"{name}@bot.overdue.local",
        hashed_password=hashed_password,
        role=role,
        total_xp=total_xp,
        is_bot=True,
        bot_difficulty=difficulty,
        avatar_id=avatar_id,
    )
    session.add(bot)
    await session.flush()  # assigns bot.id

    now = datetime.utcnow()

    # -- XP ledger entries (staggered over past days) ----------------------
    remaining_xp = total_xp
    ledger_days = random.randint(5, 30)
    entries: list[XPLedgerRow] = []
    for i in range(ledger_days):
        if remaining_xp <= 0:
            break
        chunk = random.randint(1, max(1, remaining_xp // max(1, ledger_days - i)))
        chunk = min(chunk, remaining_xp)
        entry_time = now - timedelta(
            days=ledger_days - i,
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59),
        )
        entries.append(
            XPLedgerRow(
                librarian_id=bot.id,
                amount=chunk,
                reason="Bot activity",
                created_at=entry_time,
            )
        )
        remaining_xp -= chunk

    # Flush any leftover XP into the last entry
    if remaining_xp > 0:
        if entries:
            entries[-1].amount += remaining_xp
        else:
            entries.append(
                XPLedgerRow(
                    librarian_id=bot.id,
                    amount=remaining_xp,
                    reason="Bot activity",
                    created_at=now - timedelta(days=1),
                )
            )
    session.add_all(entries)

    # -- streak ------------------------------------------------------------
    streak_min, streak_max = profile["streak_range"]
    current_streak = random.randint(streak_min, streak_max)
    if current_streak > 0:
        longest_streak = random.randint(current_streak, max(current_streak, streak_max))
        streak = StreakRow(
            librarian_id=bot.id,
            current_streak=current_streak,
            longest_streak=longest_streak,
            last_review_date=now - timedelta(hours=random.randint(1, 20)),
        )
        session.add(streak)

    # -- badges ------------------------------------------------------------
    badge_min, badge_max = profile["badge_range"]
    num_badges = random.randint(badge_min, min(badge_max, len(_BOT_BADGE_POOL)))
    chosen_badges = random.sample(_BOT_BADGE_POOL, num_badges)
    for badge_name in chosen_badges:
        badge = BadgeRow(
            librarian_id=bot.id,
            badge_name=badge_name,
            earned_at=now - timedelta(days=random.randint(1, 60)),
        )
        session.add(badge)

    # -- volumes on existing shelves ---------------------------------------
    shelf_result = await session.execute(select(ShelfRow))
    shelves = shelf_result.scalars().all()

    volumes_created: list[VolumeRow] = []
    if shelves:
        vol_min, vol_max = profile["volume_range"]
        num_volumes = random.randint(vol_min, vol_max)
        available_titles = list(_VOLUME_TITLES)
        random.shuffle(available_titles)

        for i in range(num_volumes):
            title = available_titles[i % len(available_titles)]
            shelf = random.choice(shelves)
            created_at = now - timedelta(
                days=random.randint(1, 45),
                hours=random.randint(0, 23),
            )
            content = _VOLUME_CONTENT_MAP.get(title, random.choice(_GENERIC_CONTENT_POOL))
            volume = VolumeRow(
                title=title,
                content=content,
                shelf_id=shelf.id,
                author_id=bot.id,
                created_at=created_at,
                updated_at=created_at,
                last_reviewed_at=created_at,
                archived=False,
                spine_seed=random.randint(0, 9999),
            )
            session.add(volume)
            volumes_created.append(volume)

        await session.flush()  # assigns volume ids

    # -- reviews -----------------------------------------------------------
    if volumes_created:
        rev_min, rev_max = profile["review_range"]
        num_reviews = random.randint(rev_min, rev_max)
        for i in range(num_reviews):
            vol = random.choice(volumes_created)
            reviewed_at = now - timedelta(
                days=random.randint(0, 30),
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59),
            )
            review = ReviewRow(
                volume_id=vol.id,
                librarian_id=bot.id,
                reviewed_at=reviewed_at,
                dewey_score_before=round(random.uniform(20.0, 100.0), 2),
            )
            session.add(review)

    await session.flush()
    return bot


# =========================================================================
# Remove bots
# =========================================================================

async def remove_bot(session: AsyncSession, username: str) -> bool:
    """Remove a single bot and all of its related data.

    Returns ``True`` if the bot was found and deleted, ``False`` otherwise.
    """
    result = await session.execute(
        select(LibrarianRow).where(
            LibrarianRow.username == username,
            LibrarianRow.is_bot == True,  # noqa: E712
        )
    )
    bot = result.scalar_one_or_none()
    if bot is None:
        return False

    # Delete dependent rows that do not cascade automatically
    await session.execute(
        delete(ReviewRow).where(ReviewRow.librarian_id == bot.id)
    )
    await session.execute(
        delete(VolumeRow).where(VolumeRow.author_id == bot.id)
    )
    await session.execute(
        delete(XPLedgerRow).where(XPLedgerRow.librarian_id == bot.id)
    )
    await session.execute(
        delete(BadgeRow).where(BadgeRow.librarian_id == bot.id)
    )
    await session.execute(
        delete(StreakRow).where(StreakRow.librarian_id == bot.id)
    )

    await session.delete(bot)
    await session.flush()
    return True


async def remove_all_bots(session: AsyncSession) -> int:
    """Remove every bot in the database.  Returns the count of bots removed."""
    result = await session.execute(
        select(LibrarianRow).where(LibrarianRow.is_bot == True)  # noqa: E712
    )
    bots = result.scalars().all()
    count = 0
    for bot in bots:
        removed = await remove_bot(session, bot.username)
        if removed:
            count += 1
    return count


# =========================================================================
# List bots
# =========================================================================

async def list_bots(session: AsyncSession) -> list[dict]:
    """Return a summary list of all bot librarians."""
    result = await session.execute(
        select(LibrarianRow).where(LibrarianRow.is_bot == True)  # noqa: E712
    )
    bots = result.scalars().all()
    return [
        {
            "id": bot.id,
            "username": bot.username,
            "difficulty": bot.bot_difficulty,
            "total_xp": bot.total_xp,
            "role": bot.role,
            "avatar_id": bot.avatar_id,
        }
        for bot in bots
    ]


# =========================================================================
# Simulate ongoing activity
# =========================================================================

async def simulate_bot_activity(
    session: AsyncSession,
    bot_username: str | None = None,
) -> list[dict]:
    """Simulate a round of activity for one or all bots.

    For each bot the simulation:

    * Awards a difficulty-appropriate amount of XP.
    * Optionally creates a new review on one of the bot's volumes.
    * Updates the bot's streak (continue or reset, weighted by difficulty).
    * Recalculates the bot's rank.

    Parameters
    ----------
    session:
        An active async database session.
    bot_username:
        If given, only simulate that single bot.  Otherwise all bots
        are simulated.

    Returns
    -------
    list[dict]
        One entry per bot showing ``username``, ``xp_gained``,
        ``new_total_xp``, and ``new_rank``.
    """
    if bot_username is not None:
        result = await session.execute(
            select(LibrarianRow).where(
                LibrarianRow.username == bot_username,
                LibrarianRow.is_bot == True,  # noqa: E712
            )
        )
        bot = result.scalar_one_or_none()
        bots = [bot] if bot else []
    else:
        result = await session.execute(
            select(LibrarianRow).where(LibrarianRow.is_bot == True)  # noqa: E712
        )
        bots = list(result.scalars().all())

    now = datetime.utcnow()
    changes: list[dict] = []

    for bot in bots:
        profile = DIFFICULTY_PROFILES.get(bot.bot_difficulty or "casual", DIFFICULTY_PROFILES["casual"])

        # -- award XP ------------------------------------------------------
        xp_gained = random.randint(*profile["activity_xp_range"])
        bot.total_xp += xp_gained

        ledger_entry = XPLedgerRow(
            librarian_id=bot.id,
            amount=xp_gained,
            reason="Simulated bot activity",
            created_at=now,
        )
        session.add(ledger_entry)

        # -- maybe add a review --------------------------------------------
        vol_result = await session.execute(
            select(VolumeRow).where(VolumeRow.author_id == bot.id)
        )
        bot_volumes = vol_result.scalars().all()
        if bot_volumes and random.random() < profile["streak_continue_chance"]:
            vol = random.choice(bot_volumes)
            review = ReviewRow(
                volume_id=vol.id,
                librarian_id=bot.id,
                reviewed_at=now,
                dewey_score_before=round(random.uniform(20.0, 100.0), 2),
            )
            session.add(review)

        # -- update streak -------------------------------------------------
        streak_result = await session.execute(
            select(StreakRow).where(StreakRow.librarian_id == bot.id)
        )
        streak = streak_result.scalar_one_or_none()

        if streak is not None:
            if random.random() < profile["streak_continue_chance"]:
                streak.current_streak += 1
                if streak.current_streak > streak.longest_streak:
                    streak.longest_streak = streak.current_streak
            else:
                streak.current_streak = 0
            streak.last_review_date = now

        # -- recalculate rank ----------------------------------------------
        new_rank = get_rank_for_xp(bot.total_xp)
        bot.role = new_rank

        changes.append(
            {
                "username": bot.username,
                "xp_gained": xp_gained,
                "new_total_xp": bot.total_xp,
                "new_rank": new_rank,
            }
        )

    await session.flush()
    return changes
