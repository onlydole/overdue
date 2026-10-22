"""Exercise library workflows and invalid requests against an isolated database."""

import asyncio
from datetime import timedelta
from importlib.metadata import version

import pytest
from sqlalchemy import func, select

from src.db.tables import ShelfRow, VolumeRow, XPLedgerRow
from src.utils import utcnow
from tests.test_security import (  # noqa: F401
    _auth,
    _make_librarian,
    _make_shelf,
    _make_volume,
    client,
    session_factory,
)


async def _register_and_login(web_client):
    response = await web_client.post(
        "/register",
        data={
            "username": "workflow",
            "email": "workflow@example.com",
            "password": "Library123!",
            "confirm_password": "Library123!",
            "avatar_id": "avatar_02",
        },
    )
    assert response.status_code == 302


@pytest.mark.parametrize("field", ["title", "content", "shelf_id"])
async def test_volume_patch_rejects_null_required_fields(client, session_factory, field):  # noqa: F811
    owner = await _make_librarian(session_factory, "owner")
    shelf = await _make_shelf(session_factory, owner)
    volume = await _make_volume(session_factory, owner, shelf)
    response = await client.patch(
        f"/api/volumes/{volume}", json={field: None}, headers=_auth(owner, "owner", "Page")
    )
    assert response.status_code == 422
    assert (await client.get(f"/api/volumes/{volume}")).json()["title"] == "Title"


async def test_shelf_patch_rejects_null_name(client, session_factory):  # noqa: F811
    owner = await _make_librarian(session_factory, "owner")
    shelf = await _make_shelf(session_factory, owner)
    response = await client.patch(
        f"/api/shelves/{shelf}", json={"name": None}, headers=_auth(owner, "owner", "Page")
    )
    assert response.status_code == 422


async def test_shelf_patch_reports_duplicate_name(client, session_factory):  # noqa: F811
    owner = await _make_librarian(session_factory, "owner")
    shelf = await _make_shelf(session_factory, owner, "First")
    await _make_shelf(session_factory, owner, "Second")
    response = await client.patch(
        f"/api/shelves/{shelf}", json={"name": "Second"}, headers=_auth(owner, "owner", "Page")
    )
    assert response.status_code == 409
    assert (await client.get(f"/api/shelves/{shelf}")).json()["name"] == "First"


async def test_repeated_bookmarks_are_stored_once(client, session_factory):  # noqa: F811
    owner = await _make_librarian(session_factory, "owner")
    shelf = await _make_shelf(session_factory, owner)
    response = await client.post(
        "/api/volumes/",
        json={
            "title": "Bookmarks",
            "content": "Body",
            "shelf_id": shelf,
            "bookmarks": ["python", "python", "async"],
        },
        headers=_auth(owner, "owner", "Page"),
    )
    assert response.status_code == 201
    volume = response.json()["id"]
    assert response.json()["bookmarks"] == ["python", "async"]
    response = await client.patch(
        f"/api/volumes/{volume}",
        json={"bookmarks": ["new", "new"]},
        headers=_auth(owner, "owner", "Page"),
    )
    assert response.status_code == 200
    assert response.json()["bookmarks"] == ["new"]


@pytest.mark.parametrize("shelf_id", ["not-a-number", "99999", "0", "-1"])
async def test_web_volume_rejects_invalid_shelf(client, session_factory, shelf_id):  # noqa: F811
    await _register_and_login(client)
    response = await client.post(
        "/volumes/create", data={"title": "Bad shelf", "content": "Body", "shelf_id": shelf_id}
    )
    assert response.status_code == 400
    assert "Please select a valid shelf." in response.text
    async with session_factory() as session:
        assert (await session.execute(select(func.count()).select_from(VolumeRow))).scalar() == 0


async def test_web_volume_deduplicates_bookmarks(client, session_factory):  # noqa: F811
    await _register_and_login(client)
    shelf = await _make_shelf(session_factory, 1)
    response = await client.post(
        "/volumes/create",
        data={
            "title": "Bookmarks",
            "content": "Body",
            "shelf_id": shelf,
            "bookmarks": "python, python, async",
        },
    )
    assert response.status_code == 302
    volume = (await client.get("/api/volumes/")).json()["items"][0]
    assert set(volume["bookmarks"]) == {"python", "async"}


async def test_web_shelf_enforces_name_limit(client, session_factory):  # noqa: F811
    await _register_and_login(client)
    response = await client.post("/shelves/create", data={"name": "x" * 256})
    assert response.status_code == 400
    assert "255 characters" in response.text
    async with session_factory() as session:
        assert (await session.execute(select(func.count()).select_from(ShelfRow))).scalar() == 0


async def test_missing_profile_returns_not_found(client):  # noqa: F811
    assert (await client.get("/profile/9999")).status_code == 404


async def test_create_volume_rolls_back_if_game_award_fails(client, session_factory, monkeypatch):  # noqa: F811
    import src.game.engine as game_engine

    owner = await _make_librarian(session_factory, "owner")
    shelf = await _make_shelf(session_factory, owner)

    async def fail_award(*args):
        raise RuntimeError("Award failure")

    monkeypatch.setattr(game_engine, "on_volume_shelved", fail_award)
    with pytest.raises(RuntimeError, match="Award failure"):
        await client.post(
            "/api/volumes/",
            json={"title": "Atomic", "content": "Body", "shelf_id": shelf},
            headers=_auth(owner, "owner", "Page"),
        )
    async with session_factory() as session:
        assert (await session.execute(select(func.count()).select_from(VolumeRow))).scalar() == 0


async def test_library_workflow(client, session_factory):  # noqa: F811
    await _register_and_login(client)
    response = await client.post("/shelves/create", data={"name": "Workflow shelf"})
    assert response.status_code == 302
    shelf = int(response.headers["location"].rsplit("/", 1)[1])
    response = await client.post(
        "/volumes/create",
        data={"title": "Workflow volume", "content": "Knowledge", "shelf_id": shelf},
    )
    assert response.status_code == 302
    volume = int(response.headers["location"].rsplit("/", 1)[1])

    for path in [
        "/",
        "/reading-room/live",
        "/shelves",
        f"/shelves/{shelf}",
        f"/volumes/{volume}",
        "/my-library",
        "/profile/1",
        "/settings",
        "/leaderboard",
        "/how-to-play",
    ]:
        response = await client.get(path)
        assert response.status_code == 200, path

    async with session_factory() as session:
        row = await session.get(VolumeRow, volume)
        row.last_reviewed_at = utcnow() - timedelta(days=365)
        await session.commit()
    response = await client.post(f"/volumes/{volume}/review", headers={"HX-Request": "true"})
    assert response.status_code == 200
    assert "gameEvent" in response.headers["HX-Trigger"]
    assert (await client.get(f"/volumes/{volume}/reviews?page=2")).status_code == 200
    async with session_factory() as session:
        assert (await session.execute(select(func.sum(XPLedgerRow.amount)))).scalar() >= 10

    response = await client.post(
        "/settings/card",
        data={"username": "renamed", "email": "renamed@example.com", "avatar_id": "avatar_03"},
    )
    assert response.status_code == 302
    assert "renamed" in (await client.get("/settings")).text
    assert (await client.post("/logout")).status_code == 302
    assert (await client.get("/my-library")).status_code == 302


async def test_api_version_matches_package(client):  # noqa: F811
    assert (await client.get("/openapi.json")).json()["info"]["version"] == version("overdue")


@pytest.mark.parametrize("route", ["/api/volumes", "/volumes"])
async def test_concurrent_reviews_award_once(client, tmp_path, route):  # noqa: F811
    from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

    from src.config.defaults import (
        XP_DAILY_STREAK_BONUS,
        XP_RESCUE_BONUS,
        XP_REVIEW_CURRENT,
        XP_REVIEW_OVERDUE_MULTIPLIER,
    )
    from src.db.engine import get_session
    from src.db.tables import Base, ReviewRow
    from src.main import app

    engine = create_async_engine(f"sqlite+aiosqlite:///{tmp_path / 'concurrent.db'}")
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async def get_file_session():
        async with factory() as session:
            yield session

    app.dependency_overrides[get_session] = get_file_session
    await _register_and_login(client)
    owner = 1
    shelf = await _make_shelf(factory, owner)
    volume = await _make_volume(factory, owner, shelf)
    async with factory() as session:
        row = await session.get(VolumeRow, volume)
        row.last_reviewed_at = utcnow() - timedelta(days=365)
        await session.commit()

    try:
        responses = await asyncio.gather(
            *[
                client.post(
                    f"{route}/{volume}/review",
                    headers={**_auth(owner, "workflow", "Page"), "HX-Request": "true"},
                )
                for _ in range(4)
            ]
        )
        assert [r.status_code for r in responses] == [200] * 4
        async with factory() as session:
            assert (
                await session.execute(select(func.count()).select_from(ReviewRow))
            ).scalar() == 1
            xp = (await session.execute(select(func.sum(XPLedgerRow.amount)))).scalar()
        assert (
            xp
            == XP_REVIEW_CURRENT * XP_REVIEW_OVERDUE_MULTIPLIER
            + XP_RESCUE_BONUS
            + XP_DAILY_STREAK_BONUS
        )
    finally:
        await engine.dispose()


async def test_quiet_hours_expires_clients_that_do_not_return(client, monkeypatch):  # noqa: F811
    import time

    import src.main as main_module

    main_module._request_counts["inactive"] = [time.time() - 120]
    main_module._request_counts["active"] = [time.time()]
    monkeypatch.setattr(main_module, "_next_quiet_hours_cleanup", 0.0)
    assert (await client.get("/api/reading-room/health")).status_code == 200
    assert "inactive" not in main_module._request_counts
    assert "active" in main_module._request_counts


async def test_api_library_lifecycle(client):  # noqa: F811
    credentials = {"username": "api-librarian", "password": "Library123!"}
    response = await client.post(
        "/api/librarians/register", json={**credentials, "email": "api@example.com"}
    )
    assert response.status_code == 201
    response = await client.post("/api/librarians/login", json=credentials)
    assert response.status_code == 200
    headers = {"Authorization": f"Bearer {response.json()['access_token']}"}
    assert (await client.post("/api/librarians/refresh", headers=headers)).status_code == 200
    response = await client.post("/api/shelves/", json={"name": "API shelf"}, headers=headers)
    assert response.status_code == 201
    shelf = response.json()["id"]
    response = await client.post(
        "/api/volumes/",
        headers=headers,
        json={"title": "API volume", "content": "Body", "shelf_id": shelf},
    )
    assert response.status_code == 201
    volume = response.json()["id"]
    assert (await client.get("/api/catalog/autocomplete?q=API")).json()["suggestions"] == [
        "API volume"
    ]
    response = await client.patch(
        f"/api/volumes/{volume}", json={"content": "Updated"}, headers=headers
    )
    assert response.status_code == 200
    assert response.json()["content"] == "Updated"
    response = await client.post(
        "/api/bulletins/",
        headers=headers,
        json={"url": "https://example.com/events", "events": ["volume.reviewed"]},
    )
    assert response.status_code == 201
    bulletin = response.json()["id"]
    assert (await client.get("/api/bulletins/", headers=headers)).json()["total"] == 1
    assert (await client.delete(f"/api/bulletins/{bulletin}", headers=headers)).status_code == 204
    assert (await client.get("/api/bulletins/", headers=headers)).json()["total"] == 0
    assert (await client.delete(f"/api/volumes/{volume}", headers=headers)).status_code == 204
    assert (await client.get("/api/volumes/")).json()["total"] == 0
    assert (await client.post(f"/api/volumes/{volume}/review", headers=headers)).status_code == 404
    assert (await client.delete(f"/api/shelves/{shelf}", headers=headers)).status_code == 204
    assert (await client.get("/api/shelves/")).json()["total"] == 0
