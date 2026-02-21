"""Demo data seeder for the Overdue knowledge library."""

import os
import secrets
import string
from datetime import datetime, timedelta

from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.tables import (
    BadgeRow,
    LibrarianRow,
    ReviewRow,
    ShelfRow,
    StreakRow,
    VolumeRow,
    XPLedgerRow,
    volume_bookmarks,
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def _generate_demo_password() -> str:
    """Generate a random password meeting complexity requirements."""
    alpha = string.ascii_letters + string.digits + "!@#$%"
    return "".join(secrets.choice(alpha) for _ in range(16))


def _get_demo_password() -> str:
    """Get demo password from env var, or generate one at startup."""
    return os.environ.get("OVERDUE_DEMO_PASSWORD", _generate_demo_password())


async def is_db_empty(session: AsyncSession) -> bool:
    """Check if the database has any librarians."""
    result = await session.execute(select(LibrarianRow).limit(1))
    return result.scalar_one_or_none() is None


async def seed_demo_data(session: AsyncSession) -> None:
    """Populate database with demo data for an interesting initial experience."""
    now = datetime.utcnow()

    # --- Librarians at varying XP levels ---
    # Password comes from OVERDUE_DEMO_PASSWORD env var or is randomly generated
    demo_password = _get_demo_password()
    hashed = pwd_context.hash(demo_password)
    librarians = [
        LibrarianRow(
            username="archie",
            email="archie@overdue.dev",
            hashed_password=hashed,
            role="Archivist",
            total_xp=2500,
            avatar_id="avatar_01",
        ),
        LibrarianRow(
            username="paige",
            email="paige@overdue.dev",
            hashed_password=hashed,
            role="Librarian",
            total_xp=750,
            avatar_id="avatar_07",
        ),
        LibrarianRow(
            username="dewey",
            email="dewey@overdue.dev",
            hashed_password=hashed,
            role="Page",
            total_xp=45,
            avatar_id="avatar_05",
        ),
    ]
    for lib in librarians:
        session.add(lib)
    await session.flush()

    # --- Shelves ---
    shelf_defs = [
        ("Cloud Architecture", "Patterns and practices for cloud-native systems"),
        ("Programming Languages", "Language deep-dives, idioms, and paradigms"),
        ("DevOps", "CI/CD, infrastructure as code, and operational excellence"),
        ("Security", "Application security, threat modeling, and defense in depth"),
        ("Data Engineering", "Pipelines, storage engines, and data modeling"),
    ]
    shelves = []
    for name, desc in shelf_defs:
        shelf = ShelfRow(name=name, description=desc, created_by=librarians[0].id)
        session.add(shelf)
        shelves.append(shelf)
    await session.flush()

    # --- Volumes with staggered review times for varied Dewey scores ---
    # Offsets in "decay units" (default: 10 seconds each).
    # This creates a nice spread of scores immediately on startup.
    from src.config.settings import settings
    decay_unit = settings.dewey_decay_seconds  # seconds per decay unit

    volume_defs = [
        # (title, shelf_index, author_index, decay_units_ago, bookmarks)
        ("Kubernetes Pod Scheduling", 0, 0, 1, ["k8s", "scheduling"]),
        ("AWS VPC Design Patterns", 0, 0, 5, ["aws", "networking"]),
        ("Multi-Region Failover", 0, 1, 12, ["aws", "reliability"]),
        ("Serverless Event Architectures", 0, 1, 25, ["serverless", "events"]),
        ("Rust Ownership Model", 1, 0, 2, ["rust", "memory"]),
        ("Python Async Patterns", 1, 1, 8, ["python", "async"]),
        ("Go Concurrency Primitives", 1, 0, 18, ["go", "concurrency"]),
        ("TypeScript Type Gymnastics", 1, 2, 30, ["typescript", "types"]),
        ("GitOps with ArgoCD", 2, 0, 3, ["gitops", "argocd"]),
        ("Terraform State Management", 2, 1, 10, ["terraform", "iac"]),
        ("GitHub Actions Deep Dive", 2, 2, 22, ["github", "ci-cd"]),
        ("OWASP Top 10 (2025)", 3, 0, 4, ["owasp", "appsec"]),
        ("Zero Trust Architecture", 3, 1, 15, ["zero-trust", "security"]),
        ("Supply Chain Security", 3, 0, 35, ["supply-chain", "sbom"]),
        ("Apache Kafka Internals", 4, 0, 6, ["kafka", "streaming"]),
        ("Data Lakehouse Patterns", 4, 1, 20, ["lakehouse", "analytics"]),
        ("SQLite Internals", 4, 2, 9, ["sqlite", "database"]),
    ]

    volumes = []
    for title, shelf_idx, author_idx, units_ago, bmarks in volume_defs:
        vol = VolumeRow(
            title=title,
            content=f"Comprehensive notes on {title.lower()}. This volume covers key concepts, best practices, and real-world examples gathered from production experience.",
            shelf_id=shelves[shelf_idx].id,
            author_id=librarians[author_idx].id,
            last_reviewed_at=now - timedelta(seconds=units_ago * decay_unit),
        )
        session.add(vol)
        volumes.append((vol, bmarks))
    await session.flush()

    # Add bookmarks
    for vol, bmarks in volumes:
        for tag in bmarks:
            await session.execute(
                volume_bookmarks.insert().values(volume_id=vol.id, bookmark=tag)
            )

    # --- Reviews ---
    # (vol_idx, author_idx, decay_units_ago, score_before)
    review_data = [
        (0, 0, 1, 95.0),
        (1, 0, 5, 85.0),
        (4, 0, 2, 94.0),
        (8, 0, 3, 91.0),
        (11, 0, 4, 88.0),
        (5, 1, 8, 76.0),
        (2, 1, 12, 55.0),
        (9, 1, 10, 64.0),
        (12, 1, 15, 46.0),
        (7, 2, 30, 5.0),
        (10, 2, 22, 25.0),
        (16, 2, 9, 70.0),
    ]
    for vol_idx, author_idx, units_ago, score_before in review_data:
        review = ReviewRow(
            volume_id=volumes[vol_idx][0].id,
            librarian_id=librarians[author_idx].id,
            reviewed_at=now - timedelta(seconds=units_ago * decay_unit),
            dewey_score_before=score_before,
        )
        session.add(review)

    # --- XP Ledger ---
    xp_entries = [
        (0, 10, "Shelved a new volume", 1),
        (0, 5, "Reviewed a current volume", 1),
        (0, 10, "Reviewed an overdue volume (2x bonus)", 2),
        (0, 15, "Streak bonus", 1),
        (1, 10, "Shelved a new volume", 3),
        (1, 5, "Reviewed a current volume", 5),
        (2, 10, "Shelved a new volume", 10),
    ]
    for lib_idx, amount, reason, units_ago in xp_entries:
        entry = XPLedgerRow(
            librarian_id=librarians[lib_idx].id,
            amount=amount,
            reason=reason,
            created_at=now - timedelta(seconds=units_ago * decay_unit),
        )
        session.add(entry)

    # --- Streaks ---
    cooldown = settings.streak_cooldown_seconds
    streaks = [
        StreakRow(librarian_id=librarians[0].id, current_streak=12, longest_streak=45, last_review_date=now - timedelta(seconds=cooldown)),
        StreakRow(librarian_id=librarians[1].id, current_streak=3, longest_streak=8, last_review_date=now - timedelta(seconds=cooldown)),
    ]
    for s in streaks:
        session.add(s)

    # --- Badges ---
    badge_entries = [
        (0, "First Shelve"),
        (0, "Encyclopedist"),
        (0, "Streak Master"),
        (0, "Night Owl"),
        (1, "First Shelve"),
        (2, "First Shelve"),
    ]
    for lib_idx, badge_name in badge_entries:
        badge = BadgeRow(
            librarian_id=librarians[lib_idx].id,
            badge_name=badge_name,
            earned_at=now - timedelta(days=lib_idx * 5 + 1),
        )
        session.add(badge)

    await session.commit()

    # --- Seed Bots for an active leaderboard out-of-box ---
    from src.game.bots import create_bot

    await create_bot(session, "casual", name="bookworm42")
    await create_bot(session, "diligent", name="scholar_jane")
    await session.commit()
