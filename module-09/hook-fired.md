# Hook Fired — Blocked Commit

**Hook:** `module-09/.claude/hooks.json` → `.git/hooks/pre-commit` → `module-09/.claude/smoke.sh`
**Trigger:** `git commit -m "test: intentional bug to trigger hook"`
**Bug introduced:** `raise HTTPException(status_code=500, detail="intentional bug")` at the top of `list_notes()` in `module-09/notes_api.py`
**Date:** 2026-05-31

## Actual terminal output

```
[notes-api-smoke] starting server on port 8099...
PASS  POST   /notes      → 201
FAIL  GET    /notes      → 200 (expected 200, got 500)
PASS  GET    /notes/3  → 200
PASS  PATCH  /notes/3  → 200
PASS  DELETE /notes/3  → 204
PASS  GET    /notes/999  → 404

[notes-api-smoke] 5/6 checks passed

EXIT CODE: 1
```

The commit was not created. Git printed no `[branch hash]` line because the pre-commit hook exited 1.

## What happened

1. The pre-commit hook started a fresh server on port 8099 (evicting any stale occupant first).
2. `GET /notes` returned 500 instead of 200 — the injected `raise HTTPException(status_code=500)` fired.
3. `smoke.sh` exited 1; git aborted the commit.
