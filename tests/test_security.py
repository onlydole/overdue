"""Security regression tests: object-level authorization, CORS, secrets, limits.

These lock in the fixes for:
  - IDOR / broken object-level authorization on volume & shelf mutate/delete
  - CORS wildcard + credentials misconfiguration
  - Insecure default signing-secret detection
  - Unbounded pagination limits
"""

import time

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

import src.main as main_module
from src.auth.circulation import can_manage_resource
from src.auth.library_card import create_library_card
from src.auth.passwords import hash_password
from src.config.settings import Settings, settings
from src.db.engine import get_session
from src.db.tables import Base, LibrarianRow, ShelfRow, VolumeRow
from src.main import app
from src.web import mood_middleware


@pytest_asyncio.fixture
async def session_factory():
    """An isolated in-memory database that persists across sessions in a test."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    yield factory
    await engine.dispose()


@pytest_asyncio.fixture
async def client(session_factory):
    """Async client wired to the isolated DB, with the rate limiter reset."""
    main_module._request_counts.clear()
    # Prime the mood cache so the web-route MoodMiddleware does not reach for the
    # real (non-overridden) engine and litter a stray ./overdue.db during tests.
    mood_middleware._mood_cache["ambiance"] = "soft_pages"
    mood_middleware._mood_cache["expires_at"] = time.time() + 3600

    async def _override_get_session():
        async with session_factory() as session:
            yield session

    app.dependency_overrides[get_session] = _override_get_session
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
    app.dependency_overrides.clear()


async def _make_librarian(factory, username: str, role: str = "Page") -> int:
    async with factory() as s:
        lib = LibrarianRow(
            username=username,
            email=f"{username}@test.dev",
            hashed_password="not-a-real-hash",
            role=role,
        )
        s.add(lib)
        await s.commit()
        await s.refresh(lib)
        return lib.id


async def _make_shelf(factory, created_by: int, name: str = "Shelf") -> int:
    async with factory() as s:
        shelf = ShelfRow(name=name, created_by=created_by)
        s.add(shelf)
        await s.commit()
        await s.refresh(shelf)
        return shelf.id


async def _make_volume(factory, author_id: int, shelf_id: int) -> int:
    async with factory() as s:
        vol = VolumeRow(title="Title", content="Body", shelf_id=shelf_id, author_id=author_id)
        s.add(vol)
        await s.commit()
        await s.refresh(vol)
        return vol.id


def _auth(librarian_id: int, username: str, role: str) -> dict[str, str]:
    token = create_library_card(librarian_id, username, role)
    return {"Authorization": f"Bearer {token}"}


# --- IDOR: volumes ----------------------------------------------------------


async def test_non_owner_cannot_update_volume(client, session_factory):
    owner = await _make_librarian(session_factory, "owner")
    intruder = await _make_librarian(session_factory, "intruder")
    shelf = await _make_shelf(session_factory, owner)
    volume = await _make_volume(session_factory, owner, shelf)

    resp = await client.patch(
        f"/api/volumes/{volume}",
        json={"title": "Hijacked"},
        headers=_auth(intruder, "intruder", "Page"),
    )
    assert resp.status_code == 403
    # The 403 is returned through the library-incident envelope (TS-005), not a bare detail.
    assert resp.json()["incident"]["code"] == "TS-005"


async def test_owner_can_update_own_volume(client, session_factory):
    owner = await _make_librarian(session_factory, "owner")
    shelf = await _make_shelf(session_factory, owner)
    volume = await _make_volume(session_factory, owner, shelf)

    resp = await client.patch(
        f"/api/volumes/{volume}",
        json={"title": "Revised"},
        headers=_auth(owner, "owner", "Page"),
    )
    assert resp.status_code == 200
    assert resp.json()["title"] == "Revised"


async def test_head_librarian_can_curate_others_volume(client, session_factory):
    owner = await _make_librarian(session_factory, "owner")
    curator = await _make_librarian(session_factory, "curator", role="Head Librarian")
    shelf = await _make_shelf(session_factory, owner)
    volume = await _make_volume(session_factory, owner, shelf)

    resp = await client.patch(
        f"/api/volumes/{volume}",
        json={"title": "Curated"},
        headers=_auth(curator, "curator", "Head Librarian"),
    )
    assert resp.status_code == 200


async def test_non_owner_cannot_archive_volume(client, session_factory):
    owner = await _make_librarian(session_factory, "owner")
    intruder = await _make_librarian(session_factory, "intruder")
    shelf = await _make_shelf(session_factory, owner)
    volume = await _make_volume(session_factory, owner, shelf)

    resp = await client.delete(
        f"/api/volumes/{volume}", headers=_auth(intruder, "intruder", "Page")
    )
    assert resp.status_code == 403

    # The volume must remain un-archived (no side effect from the denied call).
    async with session_factory() as s:
        row = await s.get(VolumeRow, volume)
        assert row.archived is False


# --- IDOR: shelves ----------------------------------------------------------


async def test_non_owner_cannot_delete_shelf(client, session_factory):
    owner = await _make_librarian(session_factory, "owner")
    intruder = await _make_librarian(session_factory, "intruder")
    shelf = await _make_shelf(session_factory, owner)

    resp = await client.delete(f"/api/shelves/{shelf}", headers=_auth(intruder, "intruder", "Page"))
    assert resp.status_code == 403

    async with session_factory() as s:
        assert await s.get(ShelfRow, shelf) is not None


async def test_owner_can_delete_own_shelf(client, session_factory):
    owner = await _make_librarian(session_factory, "owner")
    shelf = await _make_shelf(session_factory, owner)

    resp = await client.delete(f"/api/shelves/{shelf}", headers=_auth(owner, "owner", "Page"))
    assert resp.status_code == 204


# --- CORS -------------------------------------------------------------------


async def test_cors_wildcard_does_not_allow_credentials(client):
    """Wildcard origins must not advertise credential support (CSRF/credential theft)."""
    resp = await client.options(
        "/api/volumes/",
        headers={
            "Origin": "https://evil.example",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert resp.headers.get("access-control-allow-credentials") != "true"


# --- Secrets ----------------------------------------------------------------


def test_default_secret_flagged_as_insecure():
    # The shipped default is a public placeholder and must be flagged.
    assert settings.is_using_insecure_secret() is True


def test_strong_secret_not_flagged():
    strong = Settings(secret_key="x" * 48)
    assert strong.is_using_insecure_secret() is False


# --- Pagination limits ------------------------------------------------------


async def test_volume_list_rejects_oversized_page_size(client):
    resp = await client.get("/api/volumes/", params={"per_page": 100_000})
    assert resp.status_code == 422


# --- IDOR: shelf UPDATE (the mutate half, alongside delete) -----------------


async def test_non_owner_cannot_update_shelf(client, session_factory):
    owner = await _make_librarian(session_factory, "owner")
    intruder = await _make_librarian(session_factory, "intruder")
    shelf = await _make_shelf(session_factory, owner, name="Owned")

    resp = await client.patch(
        f"/api/shelves/{shelf}",
        json={"name": "Hijacked"},
        headers=_auth(intruder, "intruder", "Page"),
    )
    assert resp.status_code == 403

    async with session_factory() as s:
        row = await s.get(ShelfRow, shelf)
        assert row.name == "Owned"


async def test_owner_can_update_own_shelf(client, session_factory):
    owner = await _make_librarian(session_factory, "owner")
    shelf = await _make_shelf(session_factory, owner)

    resp = await client.patch(
        f"/api/shelves/{shelf}",
        json={"name": "Renamed Shelf"},
        headers=_auth(owner, "owner", "Page"),
    )
    assert resp.status_code == 200
    assert resp.json()["name"] == "Renamed Shelf"


# --- Authentication gate (independent of the ownership check) ---------------


async def test_unauthenticated_request_cannot_mutate(client, session_factory):
    owner = await _make_librarian(session_factory, "owner")
    shelf = await _make_shelf(session_factory, owner)
    volume = await _make_volume(session_factory, owner, shelf)

    # No Authorization header: the auth gate must reject before the owner check
    # ever runs (FastAPI's HTTPBearer returns 403 on a missing credential).
    vol_resp = await client.patch(f"/api/volumes/{volume}", json={"title": "x"})
    assert vol_resp.status_code in (401, 403)
    shelf_resp = await client.delete(f"/api/shelves/{shelf}")
    assert shelf_resp.status_code in (401, 403)


# --- Reads stay public (authorization is scoped to mutations only) ----------


async def test_reads_remain_open_to_non_owners(client, session_factory):
    owner = await _make_librarian(session_factory, "owner")
    shelf = await _make_shelf(session_factory, owner)
    volume = await _make_volume(session_factory, owner, shelf)

    # Unauthenticated reads must still succeed -- the fix locks writes, not reads.
    assert (await client.get(f"/api/volumes/{volume}")).status_code == 200
    assert (await client.get(f"/api/shelves/{shelf}")).status_code == 200


# --- can_manage_resource: owner / curator / fail-closed branches ------------


def test_can_manage_resource_allows_owner_and_curators():
    assert can_manage_resource({"sub": "5", "role": "Page"}, 5) is True
    assert can_manage_resource({"sub": "9", "role": "Head Librarian"}, 5) is True
    assert can_manage_resource({"sub": "9", "role": "Living Document"}, 5) is True


def test_can_manage_resource_denies_non_owner_and_malformed_tokens():
    assert can_manage_resource({"sub": "9", "role": "Page"}, 5) is False
    assert can_manage_resource({"sub": "9", "role": "Archivist"}, 5) is False
    # Fail closed when the subject claim is missing or non-numeric.
    assert can_manage_resource({}, 5) is False
    assert can_manage_resource({"sub": "not-an-int"}, 5) is False


# --- CORS credential decision (both branches, in-process) -------------------


def test_cors_credentials_disabled_for_wildcard_origins():
    assert Settings(allowed_origins=["*"]).cors_allow_credentials() is False


def test_cors_credentials_enabled_for_explicit_allowlist():
    assert Settings(allowed_origins=["https://app.example"]).cors_allow_credentials() is True


# --- Session cookie hardening -----------------------------------------------


def test_session_https_only_defaults_off_and_is_configurable():
    assert Settings().session_https_only is False
    assert Settings(session_https_only=True).session_https_only is True


async def test_web_login_sets_samesite_lax_session_cookie(client, session_factory):
    # Seed a librarian with a real password hash so the web login succeeds.
    async with session_factory() as s:
        s.add(
            LibrarianRow(
                username="weblogin",
                email="weblogin@test.dev",
                hashed_password=hash_password("Lovelace1815!"),
            )
        )
        await s.commit()

    resp = await client.post("/login", data={"username": "weblogin", "password": "Lovelace1815!"})
    assert resp.status_code == 302
    set_cookie = resp.headers.get("set-cookie", "").lower()
    assert "session=" in set_cookie
    assert "samesite=lax" in set_cookie
    assert "httponly" in set_cookie


# --- Secret detection: empty / whitespace keys are the most dangerous --------


def test_empty_or_whitespace_secret_flagged_as_insecure():
    # An empty/whitespace key hashes to a single globally-predictable value, so
    # it must be flagged just like the public placeholders.
    assert Settings(secret_key="").is_using_insecure_secret() is True
    assert Settings(secret_key="   ").is_using_insecure_secret() is True


# --- Cascade guard: a shelf delete must not destroy others' volumes ---------


async def test_non_curator_cannot_delete_shelf_holding_foreign_volumes(client, session_factory):
    owner = await _make_librarian(session_factory, "owner")
    other = await _make_librarian(session_factory, "other")
    shelf = await _make_shelf(session_factory, owner)
    await _make_volume(session_factory, other, shelf)  # volume authored by someone else

    resp = await client.delete(f"/api/shelves/{shelf}", headers=_auth(owner, "owner", "Page"))
    assert resp.status_code == 403
    async with session_factory() as s:
        assert await s.get(ShelfRow, shelf) is not None  # nothing was deleted


async def test_head_librarian_can_delete_shelf_holding_foreign_volumes(client, session_factory):
    owner = await _make_librarian(session_factory, "owner")
    other = await _make_librarian(session_factory, "other")
    curator = await _make_librarian(session_factory, "curator", role="Head Librarian")
    shelf = await _make_shelf(session_factory, owner)
    await _make_volume(session_factory, other, shelf)

    resp = await client.delete(
        f"/api/shelves/{shelf}", headers=_auth(curator, "curator", "Head Librarian")
    )
    assert resp.status_code == 204


async def test_owner_can_delete_shelf_holding_only_own_volumes(client, session_factory):
    owner = await _make_librarian(session_factory, "owner")
    shelf = await _make_shelf(session_factory, owner)
    await _make_volume(session_factory, owner, shelf)  # owner's own volume

    resp = await client.delete(f"/api/shelves/{shelf}", headers=_auth(owner, "owner", "Page"))
    assert resp.status_code == 204
