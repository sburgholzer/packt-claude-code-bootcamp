# Module 04 — Best-of-N Scoring

## Candidate A

**Source:** `candidate-a/app.py`

```
Candidate: a
Correctness (0–3): 2
Simplicity   (0–3): 3
Fit          (0–3): 3
Total: 8 / 9
Notes:
  - 6/7 curls pass. PATCH /notes/1 → 405 because the route is decorated
    with @app.put, not @app.patch. All other 6 tests (201, 200×4, 204) pass.
  - Single file, context-manager connection handling (`with get_conn() as conn:`),
    `row_to_note` helper keeps every route handler to ~5 lines.
  - 404 body is {"error":"not found"} — matches the spec's example shape exactly.
    Uses modern FastAPI `lifespan` context manager (not the deprecated
    @app.on_event("startup")). Field(min_length=1) validates inputs at the boundary.
```

## Candidate B

**Source:** `candidate-b/main.py`

```
Candidate: b
Correctness (0–3): 2
Simplicity   (0–3): 2
Fit          (0–3): 2
Total: 6 / 9
Notes:
  - 6/7 curls pass. Same PATCH → 405 failure as A (decorator is @app.put).
    Notably, NoteUpdate fields are Optional, so partial updates would work
    semantically — but the wrong HTTP verb makes it unreachable via PATCH.
  - Single file, but connection lifecycle is manual: every route does
    conn = get_db() / conn.commit() / conn.close() by hand, and routes
    that 404 early must close before raising. No row-to-model helper;
    create/update return hand-built dicts instead of re-fetching.
  - 404 body is {"detail":"not found"} — FastAPI's default shape, not the
    spec's {"error":"..."}. Uses @app.on_event("startup"), which is
    deprecated in FastAPI ≥ 0.93. No input length validation.
```

---

## Side-by-Side Comparison

| Criterion (0–3) | Candidate A | Candidate B |
|---|---|---|
| Correctness | 2 — 6/7 pass; PATCH → 405 (wrong decorator) | 2 — 6/7 pass; same PATCH → 405 failure |
| Simplicity | 3 — context-manager conns, `row_to_note` helper, routes ≤ 5 lines | 2 — manual open/commit/close in every route, hand-built return dicts |
| Fit | 3 — `{"error":"…"}` 404 shape, modern lifespan, validated fields | 2 — `{"detail":"…"}` 404 (wrong shape), deprecated startup hook, no validation |
| **Total** | **8 / 9** | **6 / 9** |

## Winner: Candidate A

Both candidates share the same correctness bug (PUT decorator instead of PATCH), so the tiebreaker is quality across the other two dimensions. Candidate A wins on both: its connection handling is cleaner (`with get_conn()` context manager vs. manual open/commit/close scattered through every route), and it follows the spec more closely — the custom exception handler converts all HTTP errors to `{"error": "..."}` rather than FastAPI's default `{"detail": "..."}`, which matches the 404 shape shown in the exercise. The modern `lifespan` hook and `Field(min_length=1)` validation are bonuses that show the author read the FastAPI docs rather than copying older patterns.

---

## Round 2 — Adding Candidate C

## Candidate C

**Source:** `candidate-c/main.py`

```
Candidate: c
Correctness (0–3): 3
Simplicity   (0–3): 3
Fit          (0–3): 2
Total: 8 / 9
Notes:
  - 7/7 curls pass. Only candidate with @app.patch — PATCH /notes/1
    correctly returns 200 with the updated body. Also guards against empty
    payloads (raises 422 if both title and body are None).
  - Single file, get_db() is a proper @contextmanager (auto-commit + close),
    row_to_dict helper keeps routes clean. Reads as clearly as A.
  - 404 body is {"detail":"not found"} — FastAPI default, not the spec's
    {"error":"..."}. init_db() called at module level rather than via a
    lifecycle hook. No Field(min_length=1) input validation.
```

## A vs B vs C Comparison

| Criterion (0–3) | Candidate A | Candidate B | Candidate C |
|---|---|---|---|
| Correctness | 2 — 6/7; PATCH → 405 | 2 — 6/7; PATCH → 405 | **3 — 7/7 pass** |
| Simplicity | 3 — CM conns, `row_to_note`, short routes | 2 — manual open/commit/close, no helper | **3** — CM conns, `row_to_dict`, short routes |
| Fit | **3** — `{"error":"…"}` 404, modern lifespan, validated fields | 2 — wrong 404 shape, deprecated hook, no validation | 2 — `{"detail":"…"}` 404, module-level init, no validation |
| **Total** | **8 / 9** | **6 / 9** | **8 / 9** |

## Winner: Candidate C

A and C tie at 8/9, so the tiebreaker is the simpler source. C is leaner at ~119 lines vs A's 156 — no module docstring, no `__future__` import, no section-banner comments, and no Pydantic `response_model` declarations on the routes. Both use a context-manager `get_db()` and a row-to-dict helper, but C strips away everything that isn't load-bearing. A's extra polish (modern `lifespan`, `Field(min_length=1)`, spec-correct 404 shape) is real, but it doesn't close the gap opened by PATCH returning 405.
