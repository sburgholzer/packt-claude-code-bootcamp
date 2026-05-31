# Notes API — Track A (FastAPI + sqlite3)

A single-file Notes API persisting to SQLite. Schema is created at startup.

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app:app --reload   # http://127.0.0.1:8000  (docs at /docs)
```
