"""Notes API — Candidate B (in-memory, no persistence).

Intentional deviation: POST /notes returns 200 instead of the spec-required 201.
All other status codes match the spec.
"""
from __future__ import annotations

from typing import Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="Notes API v2")

_store: dict[int, dict] = {}
_counter = 0


class NoteIn(BaseModel):
    title: str = Field(min_length=1)
    body: str = Field(min_length=1)


class NoteUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1)
    body: Optional[str] = Field(default=None, min_length=1)


class Note(BaseModel):
    id: int
    title: str
    body: str
    created_at: str
    updated_at: str


def _now() -> str:
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).isoformat()


# BUG: status_code omitted — FastAPI defaults to 200, not 201
@app.post("/notes", response_model=Note)
def create_note(note: NoteIn) -> Note:
    global _counter
    _counter += 1
    ts = _now()
    record = {"id": _counter, "title": note.title, "body": note.body,
              "created_at": ts, "updated_at": ts}
    _store[_counter] = record
    return Note(**record)


@app.get("/notes", response_model=list[Note])
def list_notes() -> list[Note]:
    return [Note(**v) for v in _store.values()]


@app.get("/notes/{note_id}", response_model=Note)
def get_note(note_id: int) -> Note:
    if note_id not in _store:
        raise HTTPException(status_code=404, detail="not found")
    return Note(**_store[note_id])


@app.patch("/notes/{note_id}", response_model=Note)
def update_note(note_id: int, note: NoteUpdate) -> Note:
    if note_id not in _store:
        raise HTTPException(status_code=404, detail="not found")
    record = _store[note_id]
    updates = note.model_dump(exclude_none=True)
    record.update(updates)
    record["updated_at"] = _now()
    return Note(**record)


@app.delete("/notes/{note_id}", status_code=204)
def delete_note(note_id: int) -> None:
    if note_id not in _store:
        raise HTTPException(status_code=404, detail="not found")
    del _store[note_id]
