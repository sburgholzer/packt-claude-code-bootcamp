# notes-api-smoke — Live Invocation

**Skill:** `module-09/skill/SKILL.md`
**Target:** `module-09/notes_api.py`
**Port:** `8099`
**Date:** 2026-05-31

## Command

```bash
APP_PATH="module-09/notes_api.py" PORT=8099 bash module-09/skill/SKILL.md
```

(Script run inline via `bash << 'EOF'` from the bootcamp root.)

## Actual output

```
PASS  POST   /notes      → 201
PASS  GET    /notes      → 200
PASS  GET    /notes/1  → 200
PASS  PATCH  /notes/1  → 200
PASS  DELETE /notes/1  → 204
PASS  GET    /notes/999  → 404

6/6 checks passed
```

## Result

6/6 — all assertions passed. Exit code 0.
