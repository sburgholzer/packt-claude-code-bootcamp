"""
Pytest suite for the Notes API (module-04/winner/app.py).

Each test gets a fresh SQLite database via tmp_path + monkeypatch.
The ASGI app runs in-process through httpx.AsyncClient + ASGITransport —
no network socket, no HTTP mocks.
"""
import httpx
import pytest


# ── fixtures ─────────────────────────────────────────────────────────────────


@pytest.fixture
async def client(tmp_path, monkeypatch, notes_app):
    """Fresh DB + in-process ASGI client per test."""
    monkeypatch.setattr(notes_app, "DB_PATH", str(tmp_path / "notes.db"))
    notes_app.init_db()
    transport = httpx.ASGITransport(app=notes_app.app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


def _note(title: str = "Hello", body: str = "World") -> dict:
    return {"title": title, "body": body}


async def _create(client: httpx.AsyncClient, **kw) -> dict:
    r = await client.post("/notes", json=_note(**kw))
    assert r.status_code == 201
    return r.json()


# ── create ───────────────────────────────────────────────────────────────────


@pytest.mark.anyio
async def test_create_status_201(client):
    r = await client.post("/notes", json=_note())
    assert r.status_code == 201


@pytest.mark.anyio
async def test_create_returns_all_fields(client):
    r = await client.post("/notes", json=_note("My Note", "Some body"))
    data = r.json()
    assert data["title"] == "My Note"
    assert data["body"] == "Some body"
    assert isinstance(data["id"], int)
    assert "created_at" in data
    assert "updated_at" in data


@pytest.mark.anyio
async def test_create_ids_are_unique(client):
    a = await _create(client)
    b = await _create(client)
    assert a["id"] != b["id"]


# ── list ─────────────────────────────────────────────────────────────────────


@pytest.mark.anyio
async def test_list_empty_db(client):
    r = await client.get("/notes")
    assert r.status_code == 200
    assert r.json() == []


@pytest.mark.anyio
async def test_list_returns_all_created(client):
    for i in range(3):
        await _create(client, title=f"Note {i}")
    r = await client.get("/notes")
    assert len(r.json()) == 3


# ── search ───────────────────────────────────────────────────────────────────


@pytest.mark.anyio
async def test_search_matches_title(client):
    await _create(client, title="Python tips", body="irrelevant")
    await _create(client, title="Java tips", body="irrelevant")
    r = await client.get("/notes", params={"q": "Python"})
    assert r.status_code == 200
    titles = [n["title"] for n in r.json()]
    assert titles == ["Python tips"]


@pytest.mark.anyio
async def test_search_matches_body(client):
    await _create(client, title="Note A", body="contains needle")
    await _create(client, title="Note B", body="no match here")
    r = await client.get("/notes", params={"q": "needle"})
    assert len(r.json()) == 1
    assert r.json()[0]["body"] == "contains needle"


@pytest.mark.anyio
async def test_search_no_match_returns_empty_list(client):
    await _create(client, title="Alpha", body="Beta")
    r = await client.get("/notes", params={"q": "zzznomatch"})
    assert r.json() == []


# ── get one ──────────────────────────────────────────────────────────────────


@pytest.mark.anyio
async def test_get_one_returns_correct_note(client):
    created = await _create(client, title="Solo", body="Unique body")
    r = await client.get(f"/notes/{created['id']}")
    assert r.status_code == 200
    assert r.json()["title"] == "Solo"
    assert r.json()["id"] == created["id"]


# ── update ───────────────────────────────────────────────────────────────────


@pytest.mark.anyio
async def test_update_returns_200_with_new_values(client):
    note = await _create(client)
    r = await client.patch(f"/notes/{note['id']}", json={"title": "New", "body": "Updated"})
    assert r.status_code == 200
    assert r.json()["title"] == "New"
    assert r.json()["body"] == "Updated"


@pytest.mark.anyio
async def test_update_advances_updated_at_not_created_at(client):
    original = await _create(client)
    updated = (
        await client.patch(f"/notes/{original['id']}", json={"title": "X", "body": "Y"})
    ).json()
    assert updated["created_at"] == original["created_at"]
    assert updated["updated_at"] >= original["updated_at"]


# ── delete ───────────────────────────────────────────────────────────────────


@pytest.mark.anyio
async def test_delete_returns_204(client):
    note = await _create(client)
    r = await client.delete(f"/notes/{note['id']}")
    assert r.status_code == 204


@pytest.mark.anyio
async def test_delete_removes_note_from_list(client):
    note = await _create(client)
    await client.delete(f"/notes/{note['id']}")
    r = await client.get("/notes")
    ids = [n["id"] for n in r.json()]
    assert note["id"] not in ids


# ── 404 ──────────────────────────────────────────────────────────────────────


@pytest.mark.anyio
async def test_get_nonexistent_note_returns_404(client):
    r = await client.get("/notes/9999")
    assert r.status_code == 404
    assert r.json() == {"error": "not found"}


@pytest.mark.anyio
async def test_update_nonexistent_note_returns_404(client):
    r = await client.patch("/notes/9999", json=_note())
    assert r.status_code == 404
    assert r.json() == {"error": "not found"}


@pytest.mark.anyio
async def test_delete_nonexistent_note_returns_404(client):
    r = await client.delete("/notes/9999")
    assert r.status_code == 404
    assert r.json() == {"error": "not found"}


@pytest.mark.anyio
async def test_get_after_delete_returns_404(client):
    note = await _create(client)
    await client.delete(f"/notes/{note['id']}")
    r = await client.get(f"/notes/{note['id']}")
    assert r.status_code == 404


# ── 422 ──────────────────────────────────────────────────────────────────────


@pytest.mark.anyio
async def test_create_empty_title_returns_422(client):
    r = await client.post("/notes", json={"title": "", "body": "ok"})
    assert r.status_code == 422


@pytest.mark.anyio
async def test_create_empty_body_returns_422(client):
    r = await client.post("/notes", json={"title": "ok", "body": ""})
    assert r.status_code == 422


@pytest.mark.anyio
async def test_create_missing_body_returns_422(client):
    r = await client.post("/notes", json={"title": "only title"})
    assert r.status_code == 422


@pytest.mark.anyio
async def test_create_missing_title_returns_422(client):
    r = await client.post("/notes", json={"body": "only body"})
    assert r.status_code == 422


@pytest.mark.anyio
async def test_update_empty_title_returns_422(client):
    note = await _create(client)
    r = await client.patch(f"/notes/{note['id']}", json={"title": "", "body": "ok"})
    assert r.status_code == 422


@pytest.mark.anyio
async def test_update_empty_body_returns_422(client):
    note = await _create(client)
    r = await client.patch(f"/notes/{note['id']}", json={"title": "ok", "body": ""})
    assert r.status_code == 422
