# Follow-up: Rollback Axis — module-04/winner

## What was done

The production-readiness review scored **Rollback** as **yellow**: the SQLite
file is trivially portable, but no backup or restore procedure was documented,
and there was no callout that destructive schema changes break a naive restore.

The smallest next step from the report was applied directly to
`module-04/winner/README.md`:

- Added a **Pre-deploy backup** section with the timestamped `cp` one-liner.
- Added the corresponding restore command.
- Added a plain-English note that `CREATE TABLE IF NOT EXISTS` is safe for
  additive changes, but any destructive schema change requires a manual
  down-migration before the snapshot can be used.

## Commit

`dd9f1c8` — `docs(module-04): add pre-deploy backup and rollback instructions to README`

## Why only this axis

The four **red** axes (Security, Observability, Deployment, Runbooks) each
require new code, infrastructure, or files that touch the running application.
The **yellow** Rollback axis was the only one where the next step was purely
documentation — zero risk of introducing a regression, and the change is
immediately useful to anyone following the README today.
