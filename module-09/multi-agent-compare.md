# Multi-Agent Fan-Out — Notes API Comparison

**Date**: 2026-05-31  
**Lead**: Claude Code (this session)  
**Workers**: 2 sub-agents, spawned in parallel via `Agent()` tool  
**Task**: smoke-test two candidate Notes API implementations and pick the winner

---

## Topology

```
Lead (orchestrator)
├── Worker 1 → module-09/notes_api.py     port 8099   Candidate A
└── Worker 2 → module-09/app_v2.py  port 8100   Candidate B
```

Workers received identical smoke-test scripts (same 6 checks, same logic) with only `APP_PATH` and `PORT` differing. They ran **concurrently** — neither waited on the other.

---

## Candidate descriptions

| | Candidate A (`notes_api.py`) | Candidate B (`app_v2.py`) |
|---|---|---|
| Storage | SQLite (`notes.db`) | In-memory dict |
| Persistence | Yes (survives restart) | No (resets on restart) |
| Known deviation | None | `POST /notes` omits `status_code=201`; FastAPI defaults to 200 |

---

## Raw worker output (unedited)

### Worker 1 — Candidate A (`notes_api.py`, port 8099)

```
PASS  POST   /notes      → 201
PASS  GET    /notes      → 200
PASS  GET    /notes/5    → 200
PASS  PATCH  /notes/5    → 200
PASS  DELETE /notes/5    → 204
PASS  GET    /notes/999  → 404

6/6 checks passed
EXIT_CODE:0
```

### Worker 2 — Candidate B (`app_v2.py`, port 8100)

```
FAIL  POST   /notes      → 201 (expected 201, got 200)
PASS  GET    /notes      → 200
PASS  GET    /notes/1    → 200
PASS  PATCH  /notes/1    → 200
PASS  DELETE /notes/1    → 204
PASS  GET    /notes/999  → 404

5/6 checks passed
EXIT_CODE:1
```

---

## Lead verdict

**Winner: Candidate A (`notes_api.py`)** — 6/6, exit 0.

Candidate B fails check 1: `POST /notes` returned 200 instead of the RFC 7231 / REST convention-required 201. The root cause is a single omitted keyword argument (`status_code=201`) in the FastAPI decorator. The smoke test caught it in 14 seconds of wall time.

---

## When fan-out is worse than a single agent

This exercise also demonstrates the failure modes of fan-out.

### 1. Startup cost dominates for fast tasks

Each worker starts cold — no shared context, no cached dependencies. Spawning two agents added ~2 seconds of overhead. For a smoke test that takes 6 seconds end-to-end, the coordination tax is ~33 %. A single sequential run of both tests would have been cheaper in wall time for two candidates; fan-out only wins at **three or more** candidates where parallelism amortises the startup cost.

### 2. Workers can't share a port — resource planning is on the lead

Fan-out requires the lead to pre-allocate non-conflicting ports (8099, 8100) before dispatch. A single-agent run needs no such bookkeeping. We also discovered earlier that a stale server on port 8099 silently fed the wrong binary to a previous smoke run — fan-out magnifies this risk because you now have multiple servers to evict.

### 3. Debugging opacity

When a worker fails, the lead gets only its final stdout. There is no way to inspect the worker's intermediate state, re-run a single curl, or attach a debugger. A single-agent run keeps everything in one context window where you can pivot immediately.

### 4. Workers start cold — full prompt required

Each worker was given a 60-line self-contained script. In a single-agent run, the context of the previous invocation (`invocation.md`) was already loaded. Fan-out forces the lead to externalise that context into the prompt, which is brittle: any change to the smoke logic must be replicated to every worker prompt.

### 5. When fan-out is actually worth it

Fan-out earns its overhead when:
- You have **≥ 3 candidates** that each take **≥ 30 seconds** to evaluate (parallel wall-time savings are real).
- Workers are **truly isolated** — different repos, different Docker containers, different databases — so there is no shared-resource contention.
- The **decision rule is objective and automatable** (e.g., "pick the candidate with the highest passing checks; break ties by exit code then alphabetical order"). If the lead needs to read prose output and exercise judgment, a single agent with full context is usually better.
- You need **independent verification** — two workers that can't see each other's results guard against one worker poisoning the other's judgement (important in adversarial or evaluation settings).

**Rule of thumb**: reach for fan-out when the bottleneck is compute/IO time, not when it is reasoning time. For smoke tests on a laptop, the bottleneck is server startup (~4 s), which parallelism can halve — but only if you have enough candidates to make the coordination overhead worthwhile.
