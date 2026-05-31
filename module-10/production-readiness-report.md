# Production Readiness Report — module-04/winner (Notes API)

## Security — **RED**
No auth of any kind and no rate limiting means any caller can read, write, or delete all notes; unpinned deps (`fastapi`, `uvicorn`) make supply-chain state non-deterministic.
- **Biggest risk:** Unauthenticated write access — any network-reachable client can flood or wipe the database.
- **Smallest next step:** Pin every dep to an exact version in `requirements.txt` (`fastapi==0.115.x`) and add an `X-API-Key` header check as a FastAPI dependency.

---

## Observability — **RED**
Zero structured logging, no request IDs, no `/health` endpoint, and no error metrics; a silent failure would be invisible until a user complains.
- **Biggest risk:** An unhandled exception (e.g., SQLite lock) raises a 500 with no trace in any log, making MTTR undefined.
- **Smallest next step:** Add `import logging; logging.basicConfig(level=logging.INFO)` and log at `INFO` on every request entry and at `ERROR` on every caught exception.

---

## Deployment — **RED**
No Dockerfile, no `healthcheck`, no pinned Python version, and `uvicorn --reload` in the README implies development mode is the only documented run path.
- **Biggest risk:** `--reload` in production causes workers to restart on any file change, silently dropping in-flight requests.
- **Smallest next step:** Add a four-line `Dockerfile` (python:3.12-slim, copy, pip install, `uvicorn app:app --host 0.0.0.0 --port 8000`) and a `GET /health` route returning `{"status": "ok"}`.

---

## Runbooks — **RED**
No runbook exists; the README covers only the happy-path startup sequence.
- **Biggest risk:** "Database locked" or "disk full" on the SQLite file has no documented first-responder action.
- **Smallest next step:** Add a `RUNBOOK.md` with three entries: DB locked → check file permissions + restart; disk full → rotate/truncate DB; 500 storm → restart process and check logs.

---

## Rollback — **YELLOW**
SQLite is a single portable file, so a pre-deploy `cp notes.db notes.db.bak` is a valid rollback path, but it is not scripted or documented anywhere.
- **Biggest risk:** A schema-altering deploy (adding a NOT NULL column) has no down-migration, so restoring the old binary against the new schema would fail.
- **Smallest next step:** Add a one-liner pre-deploy backup step to the README: `cp notes.db notes.db.$(date +%Y%m%dT%H%M%S).bak` and note that schema changes require a manual rollback plan.

---

## Verdict
**No-Go.** Three red axes — no auth, no observability, no container story — make first-week production exposure indefensible.
