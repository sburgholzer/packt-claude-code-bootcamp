---
name: notes-api-smoke
description: Boot a single-file FastAPI app and smoke-test its CRUD endpoints, asserting correct HTTP status codes.
---

## Purpose

Starts a single-file FastAPI app using `uv`, fires six `curl` requests against its CRUD endpoints, and prints `PASS` or `FAIL` with the expected and actual status code for each check. Exits non-zero if any assertion fails.

## When to use it

- After writing or modifying a FastAPI CRUD file and wanting a quick end-to-end sanity check before running the full test suite.
- When you need to verify that POST, GET, PATCH, and DELETE all return the correct HTTP status codes on a live server.
- When confirming that a missing-resource path returns 404 rather than silently succeeding.
- When a CI gate needs a lightweight smoke test that requires only `uv` and `curl`, with no test framework installed.

## Prompt body

```text
Smoke-test a single-file FastAPI CRUD app.

Inputs:
  APP_PATH  — path to the Python file (e.g. ./api/app.py)
  PORT      — local port to bind (default: 8000)

Steps:
1. Derive MODULE from APP_PATH: strip the directory prefix and the .py suffix.
2. Start the server in the background:
     cd "$(dirname APP_PATH)" && \
     uv run --with fastapi --with uvicorn \
       uvicorn MODULE:app --port PORT --log-level error &
   Capture the PID.
3. Poll http://localhost:PORT/docs with curl until HTTP 200 or 10-second timeout
   (20 attempts, 0.5 s apart).
4. Run each assertion and print "PASS  <label>" or "FAIL  <label> (expected X, got Y)":
     a. POST   /notes  body={"title":"smoke","body":"test"}  → expect 201; capture returned id
     b. GET    /notes                                         → expect 200
     c. GET    /notes/<id from step 4a>                      → expect 200
     d. PATCH  /notes/<id>  body={"title":"updated"}         → expect 200
     e. DELETE /notes/<id>                                   → expect 204
     f. GET    /notes/999                                    → expect 404
5. Kill the server using the captured PID.
6. Print "N/6 checks passed" and exit 1 if any check failed, exit 0 if all passed.
```

## Expected inputs

- `APP_PATH`: relative or absolute path to the single Python file that defines the FastAPI `app` object.
- `PORT`: integer port number on which to bind the development server (default `8000`; choose a free port to avoid conflicts).

## Expected outputs

- One `PASS` or `FAIL` line per endpoint check (6 total).
- A summary line: `N/6 checks passed`.
- Exit code `0` when all 6 pass; exit code `1` when any fail.

## Worked example

Target: `module-09/notes_api.py`, port `8099`.

```bash
#!/usr/bin/env bash
set -uo pipefail

APP_PATH="module-09/notes_api.py"
PORT=8099
DIR="$(dirname "$APP_PATH")"
MODULE="$(basename "$APP_PATH" .py)"
BASE="http://localhost:$PORT"
PASS=0
FAIL=0

check() {
  local label="$1" expected="$2" actual="$3"
  if [ "$actual" = "$expected" ]; then
    printf "PASS  %s\n" "$label"
    (( ++PASS )) || true
  else
    printf "FAIL  %s (expected %s, got %s)\n" "$label" "$expected" "$actual"
    (( ++FAIL )) || true
  fi
}

# Start server
( cd "$DIR" && uv run --with fastapi --with uvicorn \
    uvicorn "$MODULE:app" --port "$PORT" --log-level error 2>/dev/null ) &
SERVER_PID=$!

# Wait up to 10 s for the server to be ready
for i in $(seq 1 20); do
  curl -sf "$BASE/docs" > /dev/null 2>&1 && break
  sleep 0.5
done

# POST /notes → 201; capture the assigned id
RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$BASE/notes" \
  -H "Content-Type: application/json" \
  -d '{"title":"smoke","body":"test"}')
STATUS=$(printf '%s' "$RESPONSE" | tail -1)
ID=$(printf '%s' "$RESPONSE" | head -1 \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")
check "POST   /notes      → 201" 201 "$STATUS"

# GET /notes → 200
STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$BASE/notes")
check "GET    /notes      → 200" 200 "$STATUS"

# GET /notes/:id → 200
STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$BASE/notes/$ID")
check "GET    /notes/$ID  → 200" 200 "$STATUS"

# PATCH /notes/:id → 200
STATUS=$(curl -s -o /dev/null -w "%{http_code}" -X PATCH "$BASE/notes/$ID" \
  -H "Content-Type: application/json" -d '{"title":"updated"}')
check "PATCH  /notes/$ID  → 200" 200 "$STATUS"

# DELETE /notes/:id → 204
STATUS=$(curl -s -o /dev/null -w "%{http_code}" -X DELETE "$BASE/notes/$ID")
check "DELETE /notes/$ID  → 204" 204 "$STATUS"

# GET /notes/999 → 404
STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$BASE/notes/999")
check "GET    /notes/999  → 404" 404 "$STATUS"

kill "$SERVER_PID" 2>/dev/null || true
wait "$SERVER_PID" 2>/dev/null || true

echo ""
echo "$PASS/6 checks passed"
[ "$FAIL" -eq 0 ]
```

Expected output when all checks pass (ID will vary):

```
PASS  POST   /notes      → 201
PASS  GET    /notes      → 200
PASS  GET    /notes/1    → 200
PASS  PATCH  /notes/1    → 200
PASS  DELETE /notes/1    → 204
PASS  GET    /notes/999  → 404

6/6 checks passed
```
