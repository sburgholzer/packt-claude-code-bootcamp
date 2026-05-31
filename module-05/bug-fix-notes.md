# Bug Fix Notes — module-04/winner/app.py

---

## Bug 1 — `update_note` crashes with 500 on missing note

**Symptom:** `PATCH /notes/999` (non-existent ID) returns a 500 Internal Server Error instead of 404.

**Cause:** After the UPDATE, the code re-selects the row but has no null guard. If the note doesn't exist, `fetchone()` returns `None` and `row_to_note(None)` throws `TypeError`.

**Claude's diagnosis:** `get_note` and `delete_note` both guard against missing rows; `update_note` simply omitted the check. The RETURNING * rewrite (see Bug 5) makes this moot for the happy path, but the explicit null guard after `fetchone()` is still the safety net.

**Fix:** Replaced the separate UPDATE + SELECT with a single `UPDATE ... RETURNING *`. If the row didn't exist, `fetchone()` returns `None` → `HTTPException(404)`.

---

## Bug 2 — LIKE wildcard injection in `list_notes`

**Symptom:** `GET /notes?q=%` matches every row. `q=_` matches any single-character title/body. Callers can control match semantics the API never advertises.

**Cause:** `f"%{q}%"` interpolates user input verbatim into a LIKE pattern before parameterizing, so `%` and `_` retain their wildcard meaning.

**Claude's diagnosis:** The query is parameterized (no SQL injection risk), but the pattern itself is user-controlled. Not advertised behavior and could leak data or bypass expected filtering.

**Fix:** Added `escape_like()` that escapes `\`, `%`, and `_` in `q` before wrapping it in `%…%`, and added `ESCAPE '\\'` to both LIKE clauses.

---

## Bug 3 — PATCH requires both fields (broken partial-update semantics)

**Symptom:** `PATCH /notes/1 {"title": "new title"}` returns 422 Unprocessable Entity.

**Cause:** `NoteUpdate` declared both `title` and `body` as required (`min_length=1`, no `Optional`). The HTTP PATCH method implies partial update.

**Claude's diagnosis:** `NoteIn` (used for POST) correctly requires both fields. `NoteUpdate` copy-pasted that schema without relaxing the constraints for partial updates.

**Fix:** Made both fields `Optional[str] = Field(default=None, min_length=1)`. `update_note` now calls `model_dump(exclude_none=True)` and builds the SET clause dynamically, skipping fields not supplied by the caller.

---

## Bug 4 — Search uses AND instead of OR

**Symptom:** `GET /notes?q=meeting` silently omits notes where "meeting" appears in the title but not the body (and vice versa).

**Cause:** `WHERE title LIKE ? AND body LIKE ?` requires both fields to match. A user searching for a keyword expects to find it anywhere in the note.

**Claude's diagnosis:** Logical error in the query. The AND contract is invisible to callers and produces unexpectedly sparse results.

**Fix:** Changed `AND` to `OR` in the LIKE clause.

---

## Bug 5 — TOCTOU race in `update_note`

**Symptom:** Under concurrent writes, the response body for a PATCH may reflect a different writer's state rather than the update just applied.

**Cause:** The original code issued `UPDATE` then a separate `SELECT` in two statements. A concurrent writer could modify the row between them.

**Claude's diagnosis:** SQLite's `with conn:` context manager wraps both in a transaction on the Python side, but only for the statements inside the same `execute` call chain; a second concurrent connection in WAL mode could slip in.

**Fix:** Replaced the UPDATE + SELECT pair with `UPDATE ... RETURNING *` (SQLite ≥ 3.35), making the read atomic with the write in a single statement.

---

## Bug 6 — `cur.lastrowid` not guarded in `create_note`

**Symptom:** In an edge case (schema trigger, driver quirk), INSERT succeeds but `lastrowid` is `None`, the follow-up SELECT returns `None`, and `row_to_note(None)` crashes with `TypeError`.

**Cause:** No assertion or null check on `cur.lastrowid` before using it in the SELECT.

**Claude's diagnosis:** Unlikely in normal operation but a latent crash path if the schema ever gains an INSTEAD OF trigger or a future driver change.

**Fix:** Added `assert cur.lastrowid is not None` between the INSERT and the re-SELECT.

---

## Bug 7 — Relative `DB_PATH` depends on working directory

**Symptom:** Starting the server from a different directory silently creates a second, empty `notes.db` file, so data appears to vanish.

**Cause:** `DB_PATH = "notes.db"` resolves against `os.getcwd()`, not the module's location.

**Claude's diagnosis:** Common portability bug; always reproducible when the server is launched via a path like `uvicorn module_05.app:app` from a parent directory.

**Fix:** Changed to `DB_PATH = Path(__file__).parent / "notes.db"`.

---

## Bug 8 — `q=""` silently returns all notes

**Symptom:** `GET /notes?q=` (empty string) returns every note instead of an empty result set or a validation error.

**Cause:** `if q:` is falsy for `""`, so the empty-string case falls through to the unfiltered query.

**Claude's diagnosis:** Invisible to callers; could be mistaken for "no search parameter" behavior. Better to reject it explicitly at the schema layer.

**Fix:** Added `min_length=1` to the `Query` annotation so FastAPI returns 422 for blank `q` values before the handler runs.
