"""Property-based tests for the GET /notes?q= search endpoint."""

import pytest
from hypothesis import HealthCheck, given, settings, strategies as st
from starlette.testclient import TestClient

# Non-empty text; st.text() naturally includes %, _, \ which exercise
# the escape_like() path in the implementation.
note_text = st.text(min_size=1, max_size=200)

_hyp = dict(suppress_health_check=[HealthCheck.function_scoped_fixture])


@pytest.fixture
def client(tmp_path, monkeypatch, notes_app):
    """Fresh DB + sync in-process client per test function."""
    monkeypatch.setattr(notes_app, "DB_PATH", str(tmp_path / "notes.db"))
    notes_app.init_db()
    return TestClient(notes_app.app)


@given(q=note_text)
@settings(max_examples=200, **_hyp)
def test_search_never_crashes(q, client):
    """Any non-empty query string returns 200 — never a 5xx."""
    assert client.get("/notes", params={"q": q}).status_code == 200


@given(title=note_text, body=note_text)
@settings(max_examples=100, **_hyp)
def test_note_always_found_by_title(title, body, client):
    """A note is always retrievable by searching its own title.

    Exercises LIKE metachar escaping: titles containing %, _, or \\ must
    match exactly and not expand as wildcard patterns.
    """
    r = client.post("/notes", json={"title": title, "body": body})
    assert r.status_code == 201
    note_id = r.json()["id"]

    results = client.get("/notes", params={"q": title}).json()
    assert any(n["id"] == note_id for n in results)


@given(title=note_text, body=note_text)
@settings(max_examples=100, **_hyp)
def test_note_always_found_by_body(title, body, client):
    """A note is always retrievable by searching its own body."""
    r = client.post("/notes", json={"title": title, "body": body})
    assert r.status_code == 201
    note_id = r.json()["id"]

    results = client.get("/notes", params={"q": body}).json()
    assert any(n["id"] == note_id for n in results)


@given(q=note_text)
@settings(max_examples=100, **_hyp)
def test_search_results_are_subset_of_all_notes(q, client):
    """Search results are always a subset of all notes."""
    all_ids = {n["id"] for n in client.get("/notes").json()}
    search_ids = {n["id"] for n in client.get("/notes", params={"q": q}).json()}
    assert search_ids <= all_ids
