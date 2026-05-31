# Commit Splitter Session — 2026-05-30

Proposed commits from Claude's commit splitter, with acceptance notes.

---

## Commit 1 — accepted as-is

**Proposed subject**
```
chore: add .gitignore for Python and editor artifacts
```
**Body:** Prevents virtual-environment directories, compiled bytecode, and OS/editor noise from cluttering git status as bootcamp modules accumulate Python projects.

**Paths:** `.gitignore`

**Status:** ✅ Accepted verbatim

---

## Commit 2 — accepted as-is

**Proposed subject**
```
docs(module-00-01): record prework smoke-test and loop reflection
```
**Body:** Captures the pre-work environment verification (Python 3.12, Node 25, Git 2.53) and a written reflection on the plan→implement→test→review→commit loop so the reasoning survives beyond the live session.

**Paths:** `module-00-prework/hello-claude.txt`, `module-01/environment.txt`, `module-01/loop-notes.md`

**Status:** ✅ Accepted verbatim

---

## Commit 3 — accepted as-is

**Proposed subject**
```
feat(module-02): CLI task manager with prompt-iteration comparison
```
**Body:** Demonstrates how adding an OUTPUT FORMAT section to the spec changes the generated code from argparse boilerplate to a manual dispatch table with dynamic column widths and controlled error UX — the comparison makes the lesson concrete rather than theoretical.

**Paths:** `module-02/task.py`, `module-02/task_v2.py`, `module-02/tasks.json`, `module-02/README.md`, `module-02/iteration-notes.md`

**Status:** ✅ Accepted verbatim

---

## Commit 4 — edited

**Proposed subject**
```
feat(module-03): document CLAUDE.md trimming experiment and import-order finding
```
**Committed subject**
```
docs(module-03): CLAUDE.md trim experiment and import-order finding
```
**Paths:** `module-03/CLAUDE.md`, `module-03/Proof.png`, `module-03/trim-notes.md`

**Status:** ✏️ Edited — changed type from `feat` to `docs` (no working code shipped); shortened subject to fit under 72 chars.

---

## Commit 5 — accepted as-is

**Proposed subject**
```
feat(module-04): best-of-N Notes API generation and scoring rubric
```
**Body:** Generates three independent implementations of the same spec and scores them to show that correctness (passing all seven curl checks) outweighs code style — Candidate C wins because it uses @app.patch while A and B both return 405.

**Paths:** `module-04/candidate-a/`, `module-04/candidate-b/`, `module-04/candidate-c/`, `module-04/scoring.md`, `module-04/winner/`

**Status:** ✅ Accepted verbatim

---

## Commit 6 — edited

**Proposed subject**
```
feat(module-05): add bug fixes, review rubric, and test suite
```
**Committed subject**
```
feat(module-05): bug-finding session, review rubric, and test suite
```
**Paths:** `module-05/bug-fix-notes.md`, `module-05/code-review-rubric.md`, `module-05/tests/`

**Status:** ✏️ Edited — "add bug fixes" reworded to "bug-finding session" because the primary artifact is the documented analysis (notes + rubric + tests), not a patch to production code.
