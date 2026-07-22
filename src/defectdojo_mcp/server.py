"""DefectDojo MCP Server - main entry point.

Provides comprehensive access to DefectDojo vulnerability management
via Model Context Protocol (MCP) over stdio transport.

Required environment variables:
    DEFECTDOJO_URL: Base URL of DefectDojo instance (e.g., https://dojo.example.com)
    DEFECTDOJO_API_KEY: API token for authentication
"""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from defectdojo_mcp.client import DefectDojoClient
from defectdojo_mcp.tools import (
    assets,
    endpoints,
    engagements,
    findings,
    imports,
    jira,
    organizations,
    system,
    tests,
    users,
)


def create_server() -> FastMCP:
    """Create and configure the MCP server with all tools."""
    client = DefectDojoClient()

    mcp = FastMCP(
        "DefectDojo",
        instructions="MCP server for DefectDojo vulnerability management platform. "
        "Provides tools for managing findings, products, engagements, tests, "
        "scan imports, JIRA integration, and system administration.",
    )

    # Register all tool modules
    findings.register(mcp, client)
    assets.register(mcp, client)
    engagements.register(mcp, client)
    tests.register(mcp, client)
    imports.register(mcp, client)
    organizations.register(mcp, client)
    users.register(mcp, client)
    endpoints.register(mcp, client)
    jira.register(mcp, client)
    system.register(mcp, client)

    return mcp


def main() -> None:
    """Run the MCP server with stdio transport."""
    server = create_server()
    server.run(transport="stdio")


if __name__ == "__main__":
    main()
