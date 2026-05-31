# AI-Generated Code Review Rubric

One page. Each check is a yes/no question answerable in ≤ 30 seconds.

---

## 1. Boundary Conditions
**Does every loop, slice, or index access handle the empty and single-element case?**
Look for: `list[0]` without a length check, `range(len(x) - 1)` near length-zero input, off-by-one in `<` vs `<=`.

---

## 2. Error Paths
**Does every call that can fail have explicit handling — not just the happy path?**
Look for: bare `try/except Exception`, functions that return `None` on failure used without a None check, file/network calls with no timeout or error branch.

---

## 3. Type Assumptions
**Does the code silently assume a specific type, shape, or encoding it never validates?**
Look for: treating a `str` as always non-empty, assuming a dict key always exists, mixing `int`/`float` in arithmetic, assuming bytes are UTF-8 without decoding.

---

## 4. Mutation Side Effects
**Are there any in-place mutations on arguments the caller might not expect to be modified?**
Look for: `list.sort()` or `dict.update()` on a parameter, default mutable arguments (`def f(x=[])`), aliasing where two variables point to the same object.

---

## 5. Resource Cleanup
**Is every opened resource (file, connection, lock, subprocess) guaranteed to close even on exception?**
Look for: `open()` without `with`, database connections not closed in the error branch, `threading.Lock()` acquired but never released on a raised exception.

---

## 6. Security Boundaries
**Is any user-supplied or external input used in a shell call, SQL query, file path, or HTML output without sanitization?**
Look for: `subprocess.run(user_input, shell=True)`, f-string SQL, `os.path.join` with unvalidated user path segments, direct `innerHTML` assignment.

---

## 7. Silent Failures
**Does the code swallow errors or return a sentinel value (None, -1, "") where the caller will likely ignore it?**
Look for: `except: pass`, functions that log but return `None`, boolean return values that callers never check.

---

## 8. Concurrency Assumptions
**If this code runs in threads or async contexts, are shared state and ordering assumptions safe?**
Look for: module-level mutable state, `async` functions that call blocking I/O, check-then-act patterns (`if key in dict: dict[key]`) without a lock.

---

## 9. Sibling Handler Parity
**Do all handlers that touch the same resource apply the same defensive checks?**
Look for: GET returns 404 but PATCH/DELETE don't; one endpoint validates input a sibling skips; error handling added to one handler but never propagated to its equivalents.

---

## 10. HTTP Method Contract
**Does each handler's behavior match what its HTTP verb actually promises?**
Look for: PATCH requiring all fields (should be partial); DELETE returning a body (should be 204/empty); POST that is idempotent; GET with side effects.

---

## 11. Parameterized ≠ Sanitized
**Does the code treat SQL parameterization as full sanitization when it isn't?**
Look for: LIKE patterns built from user input without escaping `%` and `_`; regex patterns from user input without escaping metacharacters; paths parameterized but not traversal-checked.

---

## 12. Hallucinated APIs
**Does every method, parameter, and class actually exist in the installed version of the library?**
Look for: any call you didn't write yourself; method names that sound plausible but aren't in the docs; keyword arguments that don't appear in the function signature.

---

## 13. Logical Inversion
**Are all boolean conditions, comparisons, and guards doing what the surrounding logic requires?**
Look for: `>` vs `>=`, `and` vs `or`, a stray `not` on an error branch, loop termination that exits one iteration too early or late.

---

## 14. Scope Creep
**Does the diff contain any changes outside the lines that were actually requested?**
Look for: extra imports, refactored neighbors, new helpers added "for free" — each is unreviewed surface area regardless of how clean it looks.

---

## 15. Formula / Algorithm Correctness
**Is any non-trivial math, sort comparator, or algorithm verifiable against a reference — not just intuition?**
Look for: statistical formulas, bit manipulation, custom sort keys, index arithmetic — cross-check at least one case by hand or against the spec.

---

## Scoring

| Fails | Action |
|-------|--------|
| 0 | Ship it |
| 1–4 | Fix before merge |
| 5+ | Return to author |
