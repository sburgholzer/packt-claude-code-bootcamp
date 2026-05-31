# PR Description — feat/bootcamp-modules

## Summary

Adds completed work for bootcamp modules 00–05, covering environment setup, prompt engineering, CLAUDE.md optimization, best-of-N generation, and a hardened Notes API with a full test suite. Each module is a discrete commit reflecting the plan→implement→test→review→commit loop taught in module 01.

## Why

Establishes a baseline student submission demonstrating the core bootcamp skills: structured prompting, context-file hygiene, multi-candidate generation with scoring, bug-finding under review, and property-based testing.

## What changed

- **Repo**: `.gitignore` for Python/editor artifacts
- **Module 00–01**: prework smoke-test output, environment versions, loop reflection notes
- **Module 02**: CLI task manager (`task.py`), argparse variant (`task_v2.py`), prompt-iteration comparison notes
- **Module 03**: CLAUDE.md for a TypeScript monorepo, trim-experiment notes identifying import-order as the only non-auto-fixable convention
- **Module 04**: Three FastAPI/SQLite Notes API candidates, scoring rubric, and merged winner (`winner/app.py`)
- **Module 05**: 8 documented bugs fixed in the winner, 15-point AI code-review rubric, async pytest suite (22 tests) + Hypothesis property tests (4 properties, 500 examples)

## How to test

```bash
cd module-02 && python3 task.py add "smoke" && python3 task.py list

cd module-04/winner
pip install -r requirements.txt
uvicorn app:app --reload   # spot-check /docs

cd module-05
pip install pytest httpx anyio pytest-anyio hypothesis fastapi uvicorn
pytest tests/ --app-path=../module-04/winner -v
```

## Risk

Low — all changes are additive student work files; no shared infrastructure is modified.

## Rollback

`git revert` any individual module commit by hash; each is fully self-contained.

---

## Reviewer checklist

- [ ] Does `task.py` correctly handle `--status open` and `--status done` with exit code 1 on invalid values?
- [ ] Does `module-04/winner/app.py` use `@app.patch` (not `@app.put`) and `RETURNING *` for the update route?
- [ ] Do all 22 pytest tests pass against the winner app with a fresh DB?
- [ ] Does `escape_like()` appear in the winner and is `ESCAPE '\\'` present in both LIKE clauses?
- [ ] Are the three candidate `.db` files the only binaries committed (no `.venv` or `__pycache__` directories)?
