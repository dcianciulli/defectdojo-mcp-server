"""JIRA integration tools for DefectDojo MCP Server."""

from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP

from defectdojo_mcp.client import DefectDojoClient


def register(mcp: FastMCP, client: DefectDojoClient) -> None:
    """Register JIRA-related tools."""

    @mcp.tool()
    async def list_jira_instances(
        limit: int = 25,
        offset: int = 0,
    ) -> dict[str, Any]:
        """List configured JIRA instances.

        Args:
            limit: Results per page
            offset: Pagination offset
        """
        return await client.get_list("/jira_instances/", limit=limit, offset=offset)

    @mcp.tool()
    async def get_jira_instance(instance_id: int) -> dict[str, Any]:
        """Get a JIRA instance configuration by ID.

        Args:
            instance_id: The JIRA instance ID
        """
        return await client.get(f"/jira_instances/{instance_id}/")

    @mcp.tool()
    async def list_jira_projects(
        product_id: int | None = None,
        engagement_id: int | None = None,
        limit: int = 25,
        offset: int = 0,
    ) -> dict[str, Any]:
        """List JIRA project configurations.

        Args:
            product_id: Filter by product ID
            engagement_id: Filter by engagement ID
            limit: Results per page
            offset: Pagination offset
        """
        params: dict[str, Any] = {
            "product": product_id,
            "engagement": engagement_id,
        }
        return await client.get_list(
            "/jira_projects/", params, limit=limit, offset=offset
        )

    @mcp.tool()
    async def list_jira_finding_mappings(
        finding_id: int | None = None,
        jira_key: str | None = None,
        limit: int = 25,
        offset: int = 0,
    ) -> dict[str, Any]:
        """List JIRA finding mappings (links between findings and JIRA issues).

        Args:
            finding_id: Filter by finding ID
            jira_key: Filter by JIRA issue key
            limit: Results per page
            offset: Pagination offset
        """
        params: dict[str, Any] = {
            "finding": finding_id,
            "jira_key": jira_key,
        }
        return await client.get_list(
            "/jira_finding_mappings/", params, limit=limit, offset=offset
        )

    @mcp.tool()
    async def create_jira_instance(
        url: str,
        username: str,
        password: str,
        default_issue_type: str = "Bug",
        epic_name_id: int = 0,
        open_status_key: int = 0,
        close_status_key: int = 0,
        info_mapping_severity: str = "Lowest",
        low_mapping_severity: str = "Low",
        medium_mapping_severity: str = "Medium",
        high_mapping_severity: str = "High",
        critical_mapping_severity: str = "Highest",
    ) -> dict[str, Any]:
        """Create a new JIRA instance configuration.

        Args:
            url: JIRA instance URL
            username: JIRA username
            password: JIRA API token or password
            default_issue_type: Default issue type for new issues
            epic_name_id: Custom field ID for epic name
            open_status_key: Transition ID for opening issues
            close_status_key: Transition ID for closing issues
            info_mapping_severity: JIRA priority for Info severity
            low_mapping_severity: JIRA priority for Low severity
            medium_mapping_severity: JIRA priority for Medium severity
            high_mapping_severity: JIRA priority for High severity
            critical_mapping_severity: JIRA priority for Critical severity
        """
        data: dict[str, Any] = {
            "url": url,
            "username": username,
            "password": password,
            "default_issue_type": default_issue_type,
            "epic_name_id": epic_name_id,
            "open_status_key": open_status_key,
            "close_status_key": close_status_key,
            "info_mapping_severity": info_mapping_severity,
            "low_mapping_severity": low_mapping_severity,
            "medium_mapping_severity": medium_mapping_severity,
            "high_mapping_severity": high_mapping_severity,
            "critical_mapping_severity": critical_mapping_severity,
        }
        return await client.post("/jira_instances/", data)
