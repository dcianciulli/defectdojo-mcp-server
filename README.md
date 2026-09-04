# DefectDojo MCP Server

A [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) server that provides comprehensive access to
[DefectDojo](https://www.defectdojo.com/) vulnerability management platform, plus a portable
**Agent Skill** that teaches any coding agent how to use it correctly.

> **Repos**: canonical `mcp/defectdojo-mcp-server` on repository — mirror
> [`dcianciulli/defectdojo-mcp-server`](https://github.com/dcianciulli/defectdojo-mcp-server) on GitHub.
> The server can be run straight from either remote (no clone needed).

## What's in this repository

| Path | Purpose |
|---|---|
| `src/defectdojo_mcp/` | The MCP server (78 tools, Python/FastMCP, stdio transport) |
| `skills/defectdojo/SKILL.md` | Portable Agent Skill (standard `SKILL.md` format) — works with Claude Code, OpenCode, Codex CLI, Cursor, Gemini CLI and any other skill-compatible harness |
| `skills/README.md` | **Install & distribution guide**: per-harness install paths and MCP config snippets |
| `.claude-plugin/` | Claude Code plugin + marketplace manifests (bundles skill + MCP server in one install) |
| `tests/` | Live integration tests against the real instance |

**Skill = knowledge** (procedures, workflows, tool map — plain markdown, portable everywhere).
**MCP server = execution** (the actual tools). They are independent: install either or both.
Note: a skill alone does *not* provision MCP servers — that stays explicit host configuration
(except via the Claude Code plugin below, which bundles both with user approval).

## Quick start

Prerequisites: [`uv`](https://docs.astral.sh/uv/) installed; environment variables
`DEFECTDOJO_URL` (e.g. `https://your-defectdojo.example.com`) and `DEFECTDOJO_API_KEY` (token from
DefectDojo → your profile → API v2 Key).

**Install the skill** (Node.js; auto-detects installed agents — Claude Code, OpenCode, Codex, Cursor…):

```bash
npx skills add https://github.com/dcianciulli/defectdojo-mcp-server -g
# or from the repository:
npx skills add https://github.com/dcianciulli/defectdojo-mcp-server.git -g
```

**Run the MCP server** (most harnesses — Kiro, Claude Desktop, Cursor, Gemini CLI share this JSON shape):

```json
{
  "mcpServers": {
    "defectdojo": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/dcianciulli/defectdojo-mcp-server", "defectdojo-mcp-server"],
      "env": { "DEFECTDOJO_URL": "https://your-defectdojo.example.com", "DEFECTDOJO_API_KEY": "your-token" }
    }
  }
}
```

Other harnesses (OpenCode, Codex CLI, Gemini CLI, Kiro) use different config files and field names:
**exact snippets for each are in [`skills/README.md`](skills/README.md)**.

**Claude Code one-step install** (skill + MCP server together, via plugin):

```bash
claude plugin marketplace add dcianciulli/defectdojo-mcp-server
claude plugin install defectdojo@defectdojo-mcp
```

The plugin's MCP entry points at the repository; it resolves `uvx` and requires the two
env variables above to be set in your environment.

## Features

- **Findings**: search with extensive filters (severity, status, SLA, CVE, reporter…), create, update, verify, duplicates
- **Finding lifecycle**: close as *false positive*, *mitigated*, or *duplicate* — with closure note; reopen/reactivate
- **Risk acceptance**: create with **mandatory expiration date** (findings auto-reactivate on expiry), update, expire early, reinstate
- **Products/Assets**: CRUD with filtering by organization, lifecycle, tags (v3 API: assets)
- **Engagements & Tests**: full lifecycle, notes
- **Scan Import/Reimport**: results from 180+ scanners
- **Notes & metadata**: add/remove finding notes, note types, metadata
- **Organizations, Users, Endpoints/Locations, JIRA integration, System administration** (settings, Celery, SLA, notifications)

### Finding lifecycle & risk acceptance (the important part)

Closing a finding requires a *reason* — use the dedicated tool, never raw status flips:

| Reason | Tool |
|---|---|
| Not a real vulnerability | `close_finding_false_positive(finding_id, note)` (+ `out_of_scope=true` if applicable) |
| Vulnerability remediated | `close_finding_mitigated(finding_id, note)` |
| Duplicate of another finding | `close_finding_duplicate(finding_id, duplicate_of)` |

Undo any closure with `reopen_finding`.

Risk acceptance is deliberately **discouraged in favor of fixing**: `accept_risk` requires a
future `expiration_date` (rejected otherwise), an `accepted_by` and a `justification`; findings
are reactivated automatically when the acceptance expires (`reactivate_expired=true` by default).
Manage acceptances with `update_risk_acceptance`, `expire_risk_acceptance`, `reinstate_risk_acceptance`.

When asked to work on a *project*, resolve it by **asset name first** (`list_products(name=…)`);
ask the user when ambiguous; use the organization only as a secondary hint. The bundled skill
enforces all of this — installing it is recommended.

## Available tools (78)

### Findings (8)
`list_findings` · `get_finding` · `create_finding` · `update_finding` · `verify_finding` · `delete_finding` · `get_finding_duplicates` · `reset_finding_duplicate_status`

### Finding lifecycle (5)
`close_finding` (generic, `closure_type`: false_positive / mitigated / duplicate) · `close_finding_false_positive` · `close_finding_mitigated` · `close_finding_duplicate` · `reopen_finding`

### Risk acceptance (9)
`accept_risk` (expiration mandatory) · `accept_risks_vulnerability` (bulk by CVE) · `list_risk_acceptances` · `get_risk_acceptance` · `create_risk_acceptance` · `update_risk_acceptance` · `delete_risk_acceptance` · `expire_risk_acceptance` · `reinstate_risk_acceptance`

### Notes & metadata (6)
`list_finding_notes` · `add_finding_note` · `remove_finding_note` · `list_note_types` · `list_finding_metadata` · `add_finding_metadata`

### Products/Assets (5)
`list_products` / `get_product` / `create_product` / `update_product` / `delete_product`

### Organizations (5)
`list_organizations` / `get_organization` / `create_organization` / `update_organization` / `delete_organization`

### Engagements (8)
`list_engagements` / `get_engagement` / `create_engagement` / `update_engagement` · `close_engagement` / `delete_engagement` · `list_engagement_notes` / `add_engagement_note`

### Tests (8)
`list_tests` / `get_test` / `create_test` / `update_test` / `delete_test` · `list_test_types` · `list_test_notes` / `add_test_note`

### Scan import (2)
`import_scan` · `reimport_scan`

### Endpoints (3)
`list_endpoints` · `get_endpoint` · `list_endpoint_status`

### JIRA (5)
`list_jira_instances` / `get_jira_instance` / `create_jira_instance` · `list_jira_projects` / `list_jira_finding_mappings`

### Users (6)
`list_users` / `get_user` / `get_current_user` / `create_user` / `update_user` / `delete_user`

### System (8)
`get_system_settings` / `update_system_settings` · `get_celery_status` / `get_celery_queue_details` / `purge_celery_queue` / `purge_celery_task` · `list_notifications` / `list_sla_configurations`

## Configuration

### Environment variables

| Variable | Required | Description |
|----------|----------|-------------|
| `DEFECTDOJO_URL` | Yes | Base URL of the DefectDojo instance (e.g. `https://your-defectdojo.example.com`) |
| `DEFECTDOJO_API_KEY` | Yes | API token (DefectDojo → user profile → API v2 Key) |

### Getting your API key

1. Log into DefectDojo
2. Open your profile (top-right menu → API v2 Key)
3. Copy the token value

### Authentication model

The token inherits the permissions of the user who generated it; every action (closures, notes,
risk acceptances) is attributed to that user in DefectDojo. Each person should use **their own
token** — do not share tokens between team members.

## Supported scan types

DefectDojo supports 180+ scan types (ZAP, Burp, Nessus, Qualys, SARIF, Trivy, Grype, SonarQube,
Semgrep, Dependency Check, Snyk, AWS Security Hub/Prowler, GitLab SAST/DAST, Checkmarx, Veracode…).
Run `list_test_types` to get the full list from your instance.

## Development

```bash
git clone <repo-url> && cd defectdojo-mcp-server
uv sync                 # creates .venv from pyproject.toml + uv.lock
uv run defectdojo-mcp-server          # start server locally (stdio)
```

- The `mcp` dependency is pinned to `1.x` (FastMCP API); `uv.lock` is committed to keep it that way.
- `tests/test_lifecycle_live.py` exercises the full lifecycle (close FP/mitigated, reopen, risk
  acceptance with expiration, expire) against the real instance using the *test asset* — run it
  only with a test finding ID you own.
- After changing the code, restart the MCP connection in your harness to pick up the new tools.

## License

MIT
