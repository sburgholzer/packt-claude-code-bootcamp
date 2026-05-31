#!/usr/bin/env python3
import json
import os
import sys
from datetime import datetime, timezone

TASKS_FILE = "tasks.json"


def load_tasks():
    if not os.path.exists(TASKS_FILE):
        return []
    try:
        with open(TASKS_FILE) as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        print(f"Error reading {TASKS_FILE}: {e}", file=sys.stderr)
        sys.exit(2)


def save_tasks(tasks):
    try:
        with open(TASKS_FILE, "w") as f:
            json.dump(tasks, f, indent=2)
    except OSError as e:
        print(f"Error writing {TASKS_FILE}: {e}", file=sys.stderr)
        sys.exit(2)


def next_id(tasks):
    return max((t["id"] for t in tasks), default=0) + 1


def cmd_add(args):
    if not args:
        print("Usage: task add <text>", file=sys.stderr)
        sys.exit(1)
    text = " ".join(args)
    tasks = load_tasks()
    task = {
        "id": next_id(tasks),
        "status": "todo",
        "created_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "text": text,
    }
    tasks.append(task)
    save_tasks(tasks)
    print(f"Added task #{task['id']}: {task['text']}")


_STATUS_ALIASES = {"open": "todo", "done": "done"}


def cmd_list(args):
    status_filter = None
    if "--status" in args:
        idx = args.index("--status")
        if idx + 1 >= len(args):
            print("Usage: task list [--status open|done]", file=sys.stderr)
            sys.exit(1)
        flag = args[idx + 1]
        if flag not in _STATUS_ALIASES:
            print(f"Invalid status: {flag!r} — use 'open' or 'done'", file=sys.stderr)
            sys.exit(1)
        status_filter = _STATUS_ALIASES[flag]

    tasks = load_tasks()
    if status_filter:
        tasks = [t for t in tasks if t["status"] == status_filter]

    if not tasks:
        print("No tasks.")
        return

    id_w      = max(2, max(len(str(t["id"]))    for t in tasks))
    status_w  = max(6, max(len(t["status"])      for t in tasks))
    created_w = 19
    text_w    = max(4, max(len(t["text"])        for t in tasks))

    row = f"{{:<{id_w}}}  {{:<{status_w}}}  {{:<{created_w}}}  {{:<{text_w}}}"
    print(row.format("ID", "STATUS", "CREATED", "TEXT"))
    print(row.format("-" * id_w, "-" * status_w, "-" * created_w, "-" * text_w))
    for t in tasks:
        created = t["created_at"][:19].replace("T", " ")
        print(row.format(t["id"], t["status"], created, t["text"]))


def _resolve_id(raw):
    try:
        return int(raw)
    except ValueError:
        print(f"Invalid id: {raw!r} — must be an integer", file=sys.stderr)
        sys.exit(1)


def cmd_done(args):
    if not args:
        print("Usage: task done <id>", file=sys.stderr)
        sys.exit(1)
    task_id = _resolve_id(args[0])
    tasks = load_tasks()
    for task in tasks:
        if task["id"] == task_id:
            task["status"] = "done"
            save_tasks(tasks)
            print(f"Marked #{task_id} as done")
            return
    print(f"No task with id {task_id}", file=sys.stderr)
    sys.exit(1)


def cmd_delete(args):
    if not args:
        print("Usage: task delete <id>", file=sys.stderr)
        sys.exit(1)
    task_id = _resolve_id(args[0])
    tasks = load_tasks()
    filtered = [t for t in tasks if t["id"] != task_id]
    if len(filtered) == len(tasks):
        print(f"No task with id {task_id}", file=sys.stderr)
        sys.exit(1)
    save_tasks(filtered)
    print(f"Deleted task #{task_id}")


COMMANDS = {
    "add":    cmd_add,
    "list":   cmd_list,
    "done":   cmd_done,
    "delete": cmd_delete,
}


def main():
    argv = sys.argv[1:]
    if not argv:
        print("Usage: task <add|list|done|delete> [args...]", file=sys.stderr)
        sys.exit(1)

    cmd, rest = argv[0], argv[1:]
    if cmd not in COMMANDS:
        print(f"Unknown command: {cmd!r}", file=sys.stderr)
        print(f"Available: {', '.join(COMMANDS)}", file=sys.stderr)
        sys.exit(1)

    try:
        COMMANDS[cmd](rest)
    except SystemExit:
        raise
    except Exception as e:
        print(f"Internal error: {e}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
