# task — CLI Task Manager

Manage TODOs from the terminal. Single Python file, no dependencies, persists to `tasks.json` in the current directory.

## Install

```bash
# Make executable and put on PATH (pick any directory already on your PATH)
chmod +x task.py
cp task.py /usr/local/bin/task
```

Or run without installing:

```bash
python3 task.py <command> [args...]
```

## Commands

### `task add <text>`

Add a new task.

```
$ task add "Write the spec"
Added task #1: Write the spec
```

### `task list [--status open|done]`

Print all tasks in a table. Pass `--status open` for pending tasks or `--status done` for completed tasks.

```
$ task list
ID  STATUS  CREATED              TEXT
--  ------  -------------------  --------------
1   todo    2026-05-30 14:00:00  Write the spec
2   done    2026-05-30 14:01:00  Review PR

$ task list --status open
ID  STATUS  CREATED              TEXT
--  ------  -------------------  -------------
1   todo    2026-05-30 14:00:00  Write the spec

$ task list --status done
ID  STATUS  CREATED              TEXT
--  ------  -------------------  ---------
2   done    2026-05-30 14:01:00  Review PR
```

### `task done <id>`

Mark a task as done.

```
$ task done 1
Marked #1 as done
```

### `task delete <id>`

Delete a task permanently.

```
$ task delete 99
No task with id 99        ← exits with code 1
```

## Exit codes

| Code | Meaning       |
|------|---------------|
| 0    | Success       |
| 1    | User error    |
| 2    | Internal error|

## Storage

Tasks are written to `tasks.json` in the **current working directory** when any command runs. The file is plain JSON and human-readable.
