# DefectDojo MCP Server

A [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) server that provides comprehensive access to [DefectDojo](https://www.defectdojo.com/) vulnerability management platform.

## Features

- **Findings**: List, create, update, close, verify, manage duplicates, notes, metadata
- **Products/Assets**: CRUD operations with filtering by org, lifecycle, tags
- **Engagements**: Create, update, close engagements with full lifecycle support
- **Tests**: Manage tests, test types, and associated notes
- **Scan Import/Reimport**: Import scan results from 180+ scanners with auto-create context
- **Organizations**: Manage product types (organizations)
- **Users**: User management and current user profile
- **Endpoints**: List and inspect endpoints and their statuses
- **JIRA Integration**: Manage JIRA instances, projects, and finding mappings
- **System Administration**: System settings, Celery status/queue management, risk acceptance, SLA, notifications

## Installation

### From GitHub (recommended for Kiro/Claude)

```bash
uvx --from git+https://github.com/dcianciulli/defectdojo-mcp-server defectdojo-mcp-server
```

### From source

```bash
git clone https://github.com/dcianciulli/defectdojo-mcp-server.git
cd defectdojo-mcp-server
pip install -e .
```

## Configuration

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `DEFECTDOJO_URL` | Yes | Base URL of your DefectDojo instance (e.g., `https://dojo.example.com`) |
| `DEFECTDOJO_API_KEY` | Yes | API token for authentication (from user profile in DefectDojo) |

### MCP Configuration (Kiro / Claude Desktop)

Add to your `mcp.json` (or `~/.kiro/settings/mcp.json`):

```json
{
  "mcpServers": {
    "defectdojo": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/dcianciulli/defectdojo-mcp-server", "defectdojo-mcp-server"],
      "env": {
        "DEFECTDOJO_URL": "https://dojo.example.com",
        "DEFECTDOJO_API_KEY": "your-api-key-here"
      },
      "autoApprove": [
        "list_findings",
        "get_finding",
        "list_products",
        "get_product",
        "list_engagements",
        "get_engagement",
        "list_tests",
        "get_test",
        "list_test_types",
        "list_organizations",
        "get_organization",
        "list_users",
        "get_user",
        "get_current_user",
        "list_endpoints",
        "get_endpoint",
        "list_endpoint_status",
        "list_jira_instances",
        "list_jira_projects",
        "list_jira_finding_mappings",
        "get_celery_status",
        "get_system_settings",
        "list_risk_acceptances",
        "list_notifications",
        "list_sla_configurations"
      ]
    }
  }
}
```

### Getting Your API Key

1. Log into DefectDojo
2. Go to your user profile (top-right menu → API v2 Key)
3. Copy the token value

## Available Tools

### Findings (14 tools)
- `list_findings` - List/search findings with extensive filters
- `get_finding` - Get finding details
- `create_finding` - Create new finding
- `update_finding` - Partial update
- `close_finding` - Close (mitigate) a finding
- `verify_finding` - Mark as verified
- `delete_finding` - Delete a finding
- `get_finding_duplicates` - Get duplicates
- `reset_finding_duplicate_status` - Reset duplicate status
- `list_finding_notes` / `add_finding_note` - Manage notes
- `list_finding_metadata` / `add_finding_metadata` - Manage metadata
- `accept_risks` - Accept risk for findings

### Products/Assets (5 tools)
- `list_products` / `get_product` / `create_product` / `update_product` / `delete_product`

### Engagements (8 tools)
- `list_engagements` / `get_engagement` / `create_engagement` / `update_engagement`
- `close_engagement` / `delete_engagement`
- `list_engagement_notes` / `add_engagement_note`

### Tests (8 tools)
- `list_tests` / `get_test` / `create_test` / `update_test` / `delete_test`
- `list_test_types`
- `list_test_notes` / `add_test_note`

### Scan Import (2 tools)
- `import_scan` - Import new scan results
- `reimport_scan` - Reimport (update existing test)

### Organizations (5 tools)
- `list_organizations` / `get_organization` / `create_organization` / `update_organization` / `delete_organization`

### Users (6 tools)
- `list_users` / `get_user` / `get_current_user` / `create_user` / `update_user` / `delete_user`

### Endpoints (3 tools)
- `list_endpoints` / `get_endpoint` / `list_endpoint_status`

### JIRA (4 tools)
- `list_jira_instances` / `get_jira_instance` / `create_jira_instance`
- `list_jira_projects` / `list_jira_finding_mappings`

### System (10 tools)
- `get_system_settings` / `update_system_settings`
- `get_celery_status` / `get_celery_queue_details` / `purge_celery_queue` / `purge_celery_task`
- `list_risk_acceptances` / `get_risk_acceptance` / `create_risk_acceptance` / `delete_risk_acceptance`
- `list_notifications` / `list_sla_configurations`

## Authentication

The server authenticates using the DefectDojo API token mechanism. All API calls include the header:

```
Authorization: Token <DEFECTDOJO_API_KEY>
```

The token inherits the permissions of the user who generated it. Actions are performed on behalf of that user.

## Supported Scan Types

DefectDojo supports 180+ scan types. Common ones include:

- `ZAP Scan`, `Burp XML`, `Burp API`
- `Nessus Scan`, `Qualys Scan`
- `SARIF` (generic static analysis)
- `Trivy Scan`, `Grype`
- `SonarQube Scan`, `Semgrep JSON Report`
- `Dependency Check Scan`, `Snyk Code Scan`
- `AWS Security Hub`, `AWS Prowler`
- `GitLab SAST Report`, `GitLab DAST Report`
- `Checkmarx Scan`, `Veracode Scan`

Use `list_test_types` to get the full list from your instance.

## Development

```bash
git clone https://github.com/dcianciulli/defectdojo-mcp-server.git
cd defectdojo-mcp-server
pip install -e ".[dev]"
```

## License

MIT
