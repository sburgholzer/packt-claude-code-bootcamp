I removed the output section of the prompt to become: 


```text
GOAL
Build a single-binary CLI Task Manager so a developer can manage TODOs from the terminal.

CONSTRAINTS
- Language: Python 3.11 (stdlib only)
- Persistence: a single JSON file `tasks.json` in CWD.
- No background processes. No network calls.
- Exit code 0 on success, 1 on user error, 2 on internal error.
- All user-facing strings in English.

EXAMPLES
- `task add "Write the spec"` → "Added task #1: Write the spec"
- `task list` → tabular: id, status, created_at, text
- `task done 1` → "Marked #1 as done"
- `task delete 99` → exit 1, "No task with id 99"
```

## Generated output from this prompt → `task_v2.py`

Running the shorter prompt produced `task_v2.py`. Key differences from the full-prompt version (`task.py`):

- Used `argparse` with subparsers instead of a manual `sys.argv` dispatch dict
- No `README.md` generated (not specified)
- Fixed-width table columns instead of dynamic-width
- Raw ISO timestamp (with `T` and microseconds) instead of a human-readable format
- Broad `except Exception` instead of narrow `(json.JSONDecodeError, OSError)`
- ID validation delegated to argparse `type=int` instead of a controlled `_resolve_id()` helper

## Diff (`task_v2.py` → `task.py`)

```diff
--- task_v2.py
+++ task.py
@@ imports @@
-import argparse
 import json

@@ load/save @@
-def load():
+def load_tasks():
-    except Exception as e:
-        print(f"error: {e}", ...)
+    except (json.JSONDecodeError, OSError) as e:
+        print(f"Error reading {TASKS_FILE}: {e}", ...)

@@ add @@
-def add(args):          # argparse Namespace
+def cmd_add(args):      # raw list of strings
+    if not args: sys.exit(1)          # manual arity check
+    text = " ".join(args)
-    "created_at": datetime.now(...).isoformat()
+    "created_at": datetime.now(...).strftime("%Y-%m-%dT%H:%M:%SZ")

@@ list @@
-    print(f"{'ID':<4} {'STATUS':<8} {'CREATED':<25} TEXT")   # fixed widths
+    id_w = max(2, max(len(str(t["id"])) for t in tasks))      # dynamic widths
+    created = t["created_at"][:19].replace("T", " ")          # readable timestamp

@@ done/delete @@
-def done(args): args.id   # argparse parsed int
+def cmd_done(args):
+    task_id = _resolve_id(args[0])    # controlled error message on bad input

@@ dispatch @@
-    parser = argparse.ArgumentParser(...)
-    sub = parser.add_subparsers(...)
+COMMANDS = {"add": cmd_add, "list": cmd_list, ...}
+    cmd, rest = argv[0], argv[1:]
```

## What the missing section changed

The **OUTPUT FORMAT** block did three things the model couldn't infer from GOAL + CONSTRAINTS alone:

1. **Scoped deliverables**: "One source file + a short README" meant no argparse boilerplate and a required README.
2. **Set a quality bar**: the concrete `tabular: id, status, created_at, text` example prompted dynamic column sizing and a human-readable timestamp.
3. **Controlled error UX**: the `exit 1, "No task with id 99"` example signalled that error messages are spec-level concerns, not argparse's job.

**Lesson:** GOAL + CONSTRAINTS answers *what to build*. OUTPUT FORMAT answers *what to hand back* — and that changes the code, not just the files.


---

## Stretch Challenge

The prompt I used for the stretch challenge became:

```text

GOAL
Build a single-binary CLI Task Manager so a developer can manage TODOs from the terminal.

CONSTRAINTS
- Language: Python 3.11 (stdlib only)
- Persistence: a single JSON file `tasks.json` in CWD.
- No background processes. No network calls.
- Exit code 0 on success, 1 on user error, 2 on internal error.
- All user-facing strings in English.

OUTPUT FORMAT
- One source file (Python) or `src/index.ts` + `package.json` (Node).
- A short README explaining install + the four commands.

EXAMPLES
- `task add "Write the spec"` → "Added task #1: Write the spec"
- `task list` → tabular: id, status, created_at, text
- `task done 1` → "Marked #1 as done"
- `task delete 99` → exit 1, "No task with id 99"
- `task list --status open` → lists all open (todo) tasks
- `task list --status done` → lists all completed tasks

```

### The prompt change

Two new EXAMPLES lines were added:

```
- `task list --status open` → lists all open (todo) tasks
- `task list --status done` → lists all completed tasks
```

No other section changed.

### What the model inferred from the examples

- A `--status` flag on `list` is the new behaviour (not a new command).
- `open` maps to the internal `"todo"` status — the example uses a friendlier alias.
- `done` is both the flag value and the internal status value.
- Invalid values should exit 1 (consistent with the existing `task delete 99` pattern).

### Diff (`task.py` before → after)

```diff
+_STATUS_ALIASES = {"open": "todo", "done": "done"}
+
-def cmd_list(_args):
+def cmd_list(args):
+    status_filter = None
+    if "--status" in args:
+        idx = args.index("--status")
+        if idx + 1 >= len(args):
+            print("Usage: task list [--status open|done]", file=sys.stderr)
+            sys.exit(1)
+        flag = args[idx + 1]
+        if flag not in _STATUS_ALIASES:
+            print(f"Invalid status: {flag!r} — use 'open' or 'done'", file=sys.stderr)
+            sys.exit(1)
+        status_filter = _STATUS_ALIASES[flag]
+
     tasks = load_tasks()
+    if status_filter:
+        tasks = [t for t in tasks if t["status"] == status_filter]
+
     if not tasks:
```

### Verified behaviour

| Command | Output | Exit |
|---|---|---|
| `task list` | all tasks | 0 |
| `task list --status open` | todo tasks only | 0 |
| `task list --status done` | done tasks only | 0 |
| `task list --status invalid` | `Invalid status: 'invalid' — use 'open' or 'done'` | 1 |
| `task list --status open` (no matches) | `No tasks.` | 0 |

### What the examples did

Adding concrete input/output pairs to EXAMPLES was enough to fully specify a new feature — no change to GOAL, CONSTRAINTS, or OUTPUT FORMAT was needed. The alias (`open` → `todo`) was implicit in the example and carried through correctly.
