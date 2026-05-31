# CLAUDE.md Trim Notes — Conventions Section Removal

## What was removed

```
# Conventions
- Prettier: single quotes, semicolons, trailing commas, printWidth 100, tabWidth 2
- Imports: builtin → external → internal → parent → sibling → index; newlines between; alphabetized — enforced by eslint-plugin-import
- Unused args prefixed with `_`; `no-explicit-any` is a warn — avoid and never suppress silently
- Unit tests: `*.spec.ts`; integration/handler tests: `*.test.ts`; property tests: `*.property.spec.ts`
- Cross-package imports use aliases: `@blast-radius/core`, `@blast-radius/lambdas`, `@blast-radius/cli`
- DynamoDB table names follow `BlastRadius-*` convention (e.g. `BlastRadius-AdapterRegistry`)
- Lambda function names follow `BlastRadius-*` convention (e.g. `BlastRadius-RiskAssessor`)
```

## Task used to test the trim

Added `--graph-file` flag to the CLI and a matching `prebuiltGraph` option in the resolver Lambda that skips AWS discovery entirely when a pre-built `DependencyGraph` JSON is provided.

## What the missing section actually affected

### Import order — real violation introduced
The rule is: external → internal aliases → parent → sibling, with blank lines between groups.

In `handler.spec.ts`, the new `import type { DependencyGraph } from '@blast-radius/core'` was placed *after* the sibling `./handler` imports instead of before them (with a separating blank line). ESLint caught this:

```
8:1  error  There should be at least one empty line between import groups  import/order
```

Without the conventions section, the correct ordering wasn't known at generation time. This is a real defect that would have caused `npm run lint` to fail in CI.

### Prettier — self-correcting, no impact
Our code was close enough (single quotes, semicolons, trailing commas) that only minor whitespace/line-length differences were flagged. `npm run format` auto-fixed them. No human intervention needed.

### Test file naming — no violation, pre-existing issue noted
Convention: `*.spec.ts` for unit tests, `*.property.spec.ts` for property tests. The existing `handler.spec.ts` already mixed both types, so adding unit tests there didn't make things worse. With the conventions visible, a separate file might have been more appropriate.

### Unused args (`_` prefix) and `no-explicit-any` — not triggered
No unused parameters or `any` casts were introduced, so these rules had no opportunity to affect the output.

## Verdict

Removing the Conventions section caused **one real lint error** (import order) that would have blocked CI. The Prettier rule self-corrected via tooling. The test naming rule had no effect due to a pre-existing violation. The conventions most worth keeping for code-generation accuracy are the **import order rule** — it's non-obvious, not derivable from reading the source files, and not auto-fixed by Prettier.

## One line that could be cut (Definition of Done)

**Candidate for deletion:**
```
- Unused args prefixed with `_`; `no-explicit-any` is a warn — avoid and never suppress silently
```

**Why:** This is the only line fully redundant with other guardrails already in CLAUDE.md.

- The `no-explicit-any` half is already covered — more forcefully — in the Do-not section: *"Never use `any` without justification; never silence the lint warning with inline disable comments."*
- The `_` prefix for unused args is enforced by ESLint/TypeScript at `npm run lint`, so a violation gets caught by tooling before it ships regardless.

Every other line in the Conventions section carries something the tools don't auto-enforce and that isn't stated anywhere else — the import ordering rule being the clearest proof from the experiment above.