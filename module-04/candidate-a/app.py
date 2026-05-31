"""Notes API — Track A (FastAPI + Pydantic v2 + sqlite3 stdlib).

Single process, single file. Schema is initialised at startup; no migration
framework. Timestamps are ISO 8601 UTC.
"""

from __future__ import annotations

import sqlite3
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

DB_PATH = "notes.db"


def now_iso() -> str:
    """Current time as ISO 8601 UTC, e.g. 2026-05-30T12:34:56.789012+00:00."""
    return datetime.now(timezone.utc).isoformat()


def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with get_conn() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS notes (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                title      TEXT NOT NULL,
                body       TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="Notes API", lifespan=lifespan)


# ---- Schemas ---------------------------------------------------------------


class NoteIn(BaseModel):
    title: str = Field(min_length=1)
    body: str = Field(min_length=1)


class NoteUpdate(BaseModel):
    title: str = Field(min_length=1)
    body: str = Field(min_length=1)


class Note(BaseModel):
    id: int
    title: str
    body: str
    created_at: str
    updated_at: str


def row_to_note(row: sqlite3.Row) -> Note:
    return Note(**dict(row))


# ---- Routes ----------------------------------------------------------------


@app.post("/notes", response_model=Note, status_code=201)
def create_note(note: NoteIn) -> Note:
    ts = now_iso()
    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO notes (title, body, created_at, updated_at) "
            "VALUES (?, ?, ?, ?)",
            (note.title, note.body, ts, ts),
        )
        row = conn.execute(
            "SELECT * FROM notes WHERE id = ?", (cur.lastrowid,)
        ).fetchone()
    return row_to_note(row)


@app.get("/notes", response_model=list[Note])
def list_notes(q: Optional[str] = Query(default=None)) -> list[Note]:
    with get_conn() as conn:
        if q:
            like = f"%{q}%"
            rows = conn.execute(
                "SELECT * FROM notes WHERE title LIKE ? OR body LIKE ? "
                "ORDER BY id",
                (like, like),
            ).fetchall()
        else:
            rows = conn.execute("SELECT * FROM notes ORDER BY id").fetchall()
    return [row_to_note(r) for r in rows]


@app.get("/notes/{note_id}", response_model=Note)
def get_note(note_id: int) -> Note:
    with get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM notes WHERE id = ?", (note_id,)
        ).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="not found")
    return row_to_note(row)


@app.put("/notes/{note_id}", response_model=Note)
def update_note(note_id: int, note: NoteUpdate) -> Note:
    ts = now_iso()
    with get_conn() as conn:
        cur = conn.execute(
            "UPDATE notes SET title = ?, body = ?, updated_at = ? WHERE id = ?",
            (note.title, note.body, ts, note_id),
        )
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="not found")
        row = conn.execute(
            "SELECT * FROM notes WHERE id = ?", (note_id,)
        ).fetchone()
    return row_to_note(row)


@app.delete("/notes/{note_id}", status_code=204)
def delete_note(note_id: int) -> None:
    with get_conn() as conn:
        cur = conn.execute("DELETE FROM notes WHERE id = ?", (note_id,))
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="not found")


# ---- Error shape -----------------------------------------------------------


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    """Render errors as {"error": "..."} per the spec's 404 example."""
    return JSONResponse(status_code=exc.status_code, content={"error": exc.detail})
