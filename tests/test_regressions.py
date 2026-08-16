"""Regression tests for the repo-review fixes.

These lock in:
  - API review endpoint no-ops on pristine volumes (XP farming guard)
  - Volume PATCH enforces content size and shelf existence like create
  - Shelf bonus awarded when a review brings the whole shelf into good shape
  - Badge uniqueness under duplicate grants
  - Demo seed password matches the hash stored in the database
  - Bots only receive avatar ids that exist in the catalog
  - remove_bot leaves no orphaned reviews or bookmark rows
  - Registration normalizes emails to lowercase
"""

from datetime import timedelta

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from src.auth.passwords import verify_password
from src.config.defaults import XP_SHELF_BONUS
from src.config.settings import settings
from src.db.tables import (
    BadgeRow,
    LibrarianRow,
    ReviewRow,
    VolumeRow,
    XPLedgerRow,
    volume_bookmarks,
)
from src.game.avatars import AVATAR_CATALOG
from src.game.badges import grant_badge
from src.game.bots import create_bot, remove_bot
from src.game.engine import on_volume_reviewed
from src.utils import utcnow

# Reuse the isolated-DB fixtures from the security suite.
from tests.test_security import (  # noqa: F401
    _auth,
    _make_librarian,
    _make_shelf,
    client,
    session_factory,
)


async def _make_volume_reviewed_at(factory, author_id, shelf_id, reviewed_at, title="Title"):
    async with factory() as s:
        vol = VolumeRow(
            title=title,
            content="Body",
            shelf_id=shelf_id,
            author_id=author_id,
            last_reviewed_at=reviewed_at,
        )
        s.add(vol)
        await s.commit()
        await s.refresh(vol)
        return vol.id


def _overdue_timestamp():
    """A last_reviewed_at old enough to decay the score to 0."""
    decay_units_to_zero = 100 / settings.dewey_decay_rate + 1
    return utcnow() - timedelta(seconds=decay_units_to_zero * settings.dewey_decay_seconds)


# --- API review farming guard ------------------------------------------------


async def test_api_review_of_pristine_volume_is_noop(client, session_factory):  # noqa: F811
    owner = await _make_librarian(session_factory, "owner")
    shelf = await _make_shelf(session_factory, owner)
    volume = await _make_volume_reviewed_at(session_factory, owner, shelf, utcnow())

    resp = await client.post(f"/api/volumes/{volume}/review", headers=_auth(owner, "owner", "Page"))
    assert resp.status_code == 200

    async with session_factory() as s:
        reviews = (await s.execute(select(ReviewRow))).scalars().all()
        xp_rows = (await s.execute(select(XPLedgerRow))).scalars().all()
    assert reviews == []
    assert xp_rows == []


async def test_api_review_of_decayed_volume_awards_xp(client, session_factory):  # noqa: F811
    owner = await _make_librarian(session_factory, "owner")
    shelf = await _make_shelf(session_factory, owner)
    volume = await _make_volume_reviewed_at(session_factory, owner, shelf, _overdue_timestamp())

    resp = await client.post(f"/api/volumes/{volume}/review", headers=_auth(owner, "owner", "Page"))
    assert resp.status_code == 200
    assert resp.json()["dewey_score"] == 100.0

    async with session_factory() as s:
        reviews = (await s.execute(select(ReviewRow))).scalars().all()
        xp_rows = (await s.execute(select(XPLedgerRow))).scalars().all()
    assert len(reviews) == 1
    assert xp_rows  # review XP (plus overdue/rescue/streak bonuses)


# --- Volume PATCH validation -------------------------------------------------


async def test_patch_rejects_oversized_content(client, session_factory):  # noqa: F811
    owner = await _make_librarian(session_factory, "owner")
    shelf = await _make_shelf(session_factory, owner)
    volume = await _make_volume_reviewed_at(session_factory, owner, shelf, utcnow())

    too_big = "x" * (settings.max_volume_size_kb * 1024 + 1)
    resp = await client.patch(
        f"/api/volumes/{volume}",
        json={"content": too_big},
        headers=_auth(owner, "owner", "Page"),
    )
    assert resp.status_code == 413
    assert resp.json()["incident"]["code"] == "TS-011"


async def test_patch_rejects_nonexistent_shelf(client, session_factory):  # noqa: F811
    owner = await _make_librarian(session_factory, "owner")
    shelf = await _make_shelf(session_factory, owner)
    volume = await _make_volume_reviewed_at(session_factory, owner, shelf, utcnow())

    resp = await client.patch(
        f"/api/volumes/{volume}",
        json={"shelf_id": 9999},
        headers=_auth(owner, "owner", "Page"),
    )
    assert resp.status_code == 404

    async with session_factory() as s:
        row = await s.get(VolumeRow, volume)
        assert row.shelf_id == shelf


# --- Shelf bonus ---------------------------------------------------------------


async def test_shelf_bonus_awarded_when_last_straggler_reviewed(session_factory):  # noqa: F811
    owner = await _make_librarian(session_factory, "owner")
    shelf = await _make_shelf(session_factory, owner)
    healthy = await _make_volume_reviewed_at(  # noqa: F841
        session_factory, owner, shelf, utcnow(), title="Healthy"
    )
    straggler = await _make_volume_reviewed_at(
        session_factory, owner, shelf, _overdue_timestamp(), title="Straggler"
    )

    async with session_factory() as s:
        vol = await s.get(VolumeRow, straggler)
        vol.last_reviewed_at = utcnow()
        result = await on_volume_reviewed(s, owner, straggler, dewey_score_before=10.0)
        await s.commit()

    reasons = [entry["reason"] for entry in result.xp_breakdown]
    assert "Shelf bonus (all volumes healthy)" in reasons
    assert result.xp_awarded >= XP_SHELF_BONUS


async def test_no_shelf_bonus_on_single_volume_shelf(session_factory):  # noqa: F811
    owner = await _make_librarian(session_factory, "owner")
    shelf = await _make_shelf(session_factory, owner)
    only = await _make_volume_reviewed_at(
        session_factory, owner, shelf, _overdue_timestamp(), title="Only"
    )

    async with session_factory() as s:
        vol = await s.get(VolumeRow, only)
        vol.last_reviewed_at = utcnow()
        result = await on_volume_reviewed(s, owner, only, dewey_score_before=10.0)
        await s.commit()

    # A lone volume decaying and being re-reviewed must not mint +50 each cycle
    reasons = [entry["reason"] for entry in result.xp_breakdown]
    assert "Shelf bonus (all volumes healthy)" not in reasons


async def test_no_shelf_bonus_while_other_volumes_unhealthy(session_factory):  # noqa: F811
    owner = await _make_librarian(session_factory, "owner")
    shelf = await _make_shelf(session_factory, owner)
    for title in ("Straggler A", "Straggler B"):
        await _make_volume_reviewed_at(
            session_factory, owner, shelf, _overdue_timestamp(), title=title
        )

    async with session_factory() as s:
        vol_id = (
            (await s.execute(select(VolumeRow.id).where(VolumeRow.title == "Straggler A")))
            .scalars()
            .one()
        )
        vol = await s.get(VolumeRow, vol_id)
        vol.last_reviewed_at = utcnow()
        result = await on_volume_reviewed(s, owner, vol_id, dewey_score_before=10.0)
        await s.commit()

    reasons = [entry["reason"] for entry in result.xp_breakdown]
    assert "Shelf bonus (all volumes healthy)" not in reasons


# --- Badge uniqueness ----------------------------------------------------------


async def test_grant_badge_is_idempotent(session_factory):  # noqa: F811
    owner = await _make_librarian(session_factory, "owner")
    async with session_factory() as s:
        assert await grant_badge(s, owner, "First Shelve") is True
        assert await grant_badge(s, owner, "First Shelve") is False
        await s.commit()

    async with session_factory() as s:
        badges = (await s.execute(select(BadgeRow))).scalars().all()
    assert len(badges) == 1


async def test_duplicate_badge_rejected_by_constraint(session_factory):  # noqa: F811
    owner = await _make_librarian(session_factory, "owner")
    async with session_factory() as s:
        s.add(BadgeRow(librarian_id=owner, badge_name="Night Owl"))
        await s.commit()
    async with session_factory() as s:
        s.add(BadgeRow(librarian_id=owner, badge_name="Night Owl"))
        with pytest.raises(IntegrityError):
            await s.commit()


# --- Demo seed password ---------------------------------------------------------


async def test_seed_password_matches_stored_hash(session_factory, monkeypatch):  # noqa: F811
    from src.db import seed as seed_module

    monkeypatch.delenv("OVERDUE_DEMO_PASSWORD", raising=False)
    async with session_factory() as s:
        password = await seed_module.seed_demo_data(s)

    async with session_factory() as s:
        archie = (
            (await s.execute(select(LibrarianRow).where(LibrarianRow.username == "archie")))
            .scalars()
            .one()
        )
    assert verify_password(password, archie.hashed_password)


# --- Bots -----------------------------------------------------------------------


async def test_bots_only_get_catalog_avatars(session_factory):  # noqa: F811
    async with session_factory() as s:
        for i in range(6):
            bot = await create_bot(s, "casual", name=f"testbot{i}")
            assert bot.avatar_id in AVATAR_CATALOG
        await s.commit()


async def test_remove_bot_cleans_up_reviews_and_bookmarks(session_factory):  # noqa: F811
    human = await _make_librarian(session_factory, "human")
    await _make_shelf(session_factory, human)

    async with session_factory() as s:
        bot = await create_bot(s, "diligent", name="cleanupbot")
        bot_id = bot.id
        await s.commit()

    async with session_factory() as s:
        bot_volume = (
            (await s.execute(select(VolumeRow).where(VolumeRow.author_id == bot_id).limit(1)))
            .scalars()
            .one()
        )
        # A human reviews and tags the bot's volume
        s.add(
            ReviewRow(
                volume_id=bot_volume.id,
                librarian_id=human,
                dewey_score_before=50.0,
            )
        )
        await s.execute(
            volume_bookmarks.insert().values(volume_id=bot_volume.id, bookmark="human-tag")
        )
        await s.commit()

    async with session_factory() as s:
        assert await remove_bot(s, "cleanupbot") is True
        await s.commit()

    async with session_factory() as s:
        volumes = (
            (await s.execute(select(VolumeRow).where(VolumeRow.author_id == bot_id)))
            .scalars()
            .all()
        )
        reviews = (await s.execute(select(ReviewRow))).scalars().all()
        bookmarks = (await s.execute(select(volume_bookmarks.c.bookmark))).all()
    assert volumes == []
    assert reviews == []
    assert bookmarks == []


# --- Email normalization ---------------------------------------------------------


async def test_api_registration_lowercases_email(client, session_factory):  # noqa: F811
    resp = await client.post(
        "/api/librarians/register",
        json={
            "username": "CaseTester",
            "email": "Mixed.Case@Example.COM",
            "password": "Sup3rSecret!",
        },
    )
    assert resp.status_code == 201

    async with session_factory() as s:
        row = (
            (await s.execute(select(LibrarianRow).where(LibrarianRow.username == "CaseTester")))
            .scalars()
            .one()
        )
    assert row.email == "mixed.case@example.com"
