# Notes API — Track A (FastAPI + sqlite3)

A single-file Notes API persisting to SQLite. Schema is created at startup.

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app:app --reload   # http://127.0.0.1:8000  (docs at /docs)
```

## Pre-deploy backup (rollback)

Before deploying a new version, snapshot the database:

```bash
cp notes.db notes.db.$(date +%Y%m%dT%H%M%S).bak
```

To roll back, stop the server and restore the snapshot:

```bash
cp notes.db.<timestamp>.bak notes.db
```

**Schema changes:** `CREATE TABLE IF NOT EXISTS` is safe for additive changes. Any destructive change (dropping a column, adding `NOT NULL` without a default) requires a manual down-migration before the snapshot can be restored against the old binary.
