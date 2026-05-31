#!/usr/bin/env python3
import argparse
import json
import os
import sys
from datetime import datetime, timezone

TASKS_FILE = "tasks.json"


def load():
    if not os.path.exists(TASKS_FILE):
        return []
    try:
        with open(TASKS_FILE) as f:
            return json.load(f)
    except Exception as e:
        print(f"error: {e}", file=sys.stderr)
        sys.exit(2)


def save(tasks):
    try:
        with open(TASKS_FILE, "w") as f:
            json.dump(tasks, f, indent=2)
    except Exception as e:
        print(f"error: {e}", file=sys.stderr)
        sys.exit(2)


def add(args):
    tasks = load()
    tid = max((t["id"] for t in tasks), default=0) + 1
    tasks.append({
        "id": tid,
        "status": "todo",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "text": args.text,
    })
    save(tasks)
    print(f"Added task #{tid}: {args.text}")


def list_tasks(args):
    tasks = load()
    if not tasks:
        print("No tasks.")
        return
    print(f"{'ID':<4} {'STATUS':<8} {'CREATED':<25} TEXT")
    print("-" * 60)
    for t in tasks:
        print(f"{t['id']:<4} {t['status']:<8} {t['created_at']:<25} {t['text']}")


def done(args):
    tasks = load()
    for t in tasks:
        if t["id"] == args.id:
            t["status"] = "done"
            save(tasks)
            print(f"Marked #{args.id} as done")
            return
    print(f"No task with id {args.id}", file=sys.stderr)
    sys.exit(1)


def delete(args):
    tasks = load()
    filtered = [t for t in tasks if t["id"] != args.id]
    if len(filtered) == len(tasks):
        print(f"No task with id {args.id}", file=sys.stderr)
        sys.exit(1)
    save(filtered)
    print(f"Deleted task #{args.id}")


def main():
    parser = argparse.ArgumentParser(prog="task", description="CLI Task Manager")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_add = sub.add_parser("add", help="Add a task")
    p_add.add_argument("text", help="Task description")
    p_add.set_defaults(func=add)

    p_list = sub.add_parser("list", help="List all tasks")
    p_list.set_defaults(func=list_tasks)

    p_done = sub.add_parser("done", help="Mark a task done")
    p_done.add_argument("id", type=int, help="Task id")
    p_done.set_defaults(func=done)

    p_del = sub.add_parser("delete", help="Delete a task")
    p_del.add_argument("id", type=int, help="Task id")
    p_del.set_defaults(func=delete)

    args = parser.parse_args()
    try:
        args.func(args)
    except SystemExit:
        raise
    except Exception as e:
        print(f"Internal error: {e}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
