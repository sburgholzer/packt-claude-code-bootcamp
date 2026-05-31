#!/usr/bin/env bash
# notes-api-smoke — called by .git/hooks/pre-commit
# Runs from the repo root. Exits 1 if any check fails.
set -uo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
APP_PATH="${APP_PATH:-module-09/app.py}"
PORT="${PORT:-8099}"
DIR="$REPO_ROOT/$(dirname "$APP_PATH")"
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

printf '\n[notes-api-smoke] starting server on port %s...\n' "$PORT"

# Evict any stale occupant so we always start the current code
lsof -ti:"$PORT" | xargs kill -9 2>/dev/null || true
sleep 0.2

( cd "$DIR" && uv run --with fastapi --with uvicorn \
    uvicorn "$MODULE:app" --port "$PORT" --log-level error 2>/dev/null ) &
SERVER_PID=$!

for i in $(seq 1 20); do
  curl -sf "$BASE/docs" > /dev/null 2>&1 && break
  sleep 0.5
done

RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$BASE/notes" \
  -H "Content-Type: application/json" \
  -d '{"title":"smoke","body":"test"}')
STATUS=$(printf '%s' "$RESPONSE" | tail -1)
ID=$(printf '%s' "$RESPONSE" | head -1 \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")
check "POST   /notes      → 201" 201 "$STATUS"

STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$BASE/notes")
check "GET    /notes      → 200" 200 "$STATUS"

STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$BASE/notes/$ID")
check "GET    /notes/$ID  → 200" 200 "$STATUS"

STATUS=$(curl -s -o /dev/null -w "%{http_code}" -X PATCH "$BASE/notes/$ID" \
  -H "Content-Type: application/json" -d '{"title":"updated"}')
check "PATCH  /notes/$ID  → 200" 200 "$STATUS"

STATUS=$(curl -s -o /dev/null -w "%{http_code}" -X DELETE "$BASE/notes/$ID")
check "DELETE /notes/$ID  → 204" 204 "$STATUS"

STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$BASE/notes/999")
check "GET    /notes/999  → 404" 404 "$STATUS"

kill "$SERVER_PID" 2>/dev/null || true
wait "$SERVER_PID" 2>/dev/null || true

printf '\n[notes-api-smoke] %s/6 checks passed\n\n' "$PASS"

[ "$FAIL" -eq 0 ]
