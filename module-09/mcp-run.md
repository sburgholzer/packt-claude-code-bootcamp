# MCP Run — notes-api-smoke issue

## MCP context brief — notes-api-smoke issue — 2026-05-31

**Task**: Open one GitHub issue reporting the notes-api-smoke result for module-09/app.py on 2026-05-31.
**Server**: `github` MCP — scope: `write` — paths: `sburgholzer/packt-claude-code-bootcamp`
**Scope**: ONE repo — `sburgholzer/packt-claude-code-bootcamp`; no other repos or orgs in scope.
**Allowed action**: `create_issue` on `sburgholzer/packt-claude-code-bootcamp` — nothing else.
**Stop condition**: Done when the issue URL is returned; escalate to human if `create_issue` errors.

---

## Dry-run (no GitHub MCP server configured)

No `github` MCP server was found in `~/.claude/settings.json` or the project `.claude/settings.json`.
The call below is what the agent **would** make if the server were present.

### Tool call

```json
{
  "tool": "mcp__github__create_issue",
  "parameters": {
    "owner": "sburgholzer",
    "repo": "packt-claude-code-bootcamp",
    "title": "notes-api-smoke: PASS on 2026-05-31",
    "body": "## notes-api-smoke run — 2026-05-31\n\n**Target**: `module-09/app.py`  \n**Port**: `8099`  \n**Skill**: `module-09/skill/SKILL.md`\n\n### Result\n\n```\nPASS  POST   /notes      → 201\nPASS  GET    /notes      → 200\nPASS  GET    /notes/1    → 200\nPASS  PATCH  /notes/1    → 200\nPASS  DELETE /notes/1    → 204\nPASS  GET    /notes/999  → 404\n\n6/6 checks passed\n```\n\n**Exit code**: 0\n\n### Hook evidence\n\nA pre-commit hook (`module-09/.claude/hooks.json` → `.git/hooks/pre-commit`) enforces this smoke test before every commit. A deliberate 500 bug in `list_notes()` produced:\n\n```\nFAIL  GET    /notes      → 200 (expected 200, got 500)\n[notes-api-smoke] 5/6 checks passed\nEXIT CODE: 1\n```\n\nThe commit was blocked. Bug was reverted; all 6 checks now pass."
  }
}
```

### Expected response (if server were live)

```json
{
  "number": "<assigned by GitHub>",
  "html_url": "https://github.com/sburgholzer/packt-claude-code-bootcamp/issues/<N>",
  "state": "open",
  "title": "notes-api-smoke: PASS on 2026-05-31"
}
```

### Why dry-run

To configure the GitHub MCP server and run this for real, add to `~/.claude/settings.json`:

```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": { "GITHUB_PERSONAL_ACCESS_TOKEN": "<token>" }
    }
  }
}
```

Then re-run this skill — the agent will invoke `mcp__github__create_issue` directly instead of printing the dry-run block.
