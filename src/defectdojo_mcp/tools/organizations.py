"""Organization (Product Type) management tools for DefectDojo MCP Server."""

from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP

from defectdojo_mcp.client import DefectDojoClient


def register(mcp: FastMCP, client: DefectDojoClient) -> None:
    """Register organization-related tools."""

    @mcp.tool()
    async def list_organizations(
        name: str | None = None,
        limit: int = 25,
        offset: int = 0,
    ) -> dict[str, Any]:
        """List organizations (product types).

        Args:
            name: Filter by name (contains)
            limit: Results per page (default 25)
            offset: Pagination offset
        """
        params: dict[str, Any] = {"name": name}
        return await client.get_list(
            "/organizations/", params, limit=limit, offset=offset
        )

    @mcp.tool()
    async def get_organization(organization_id: int) -> dict[str, Any]:
        """Get a single organization by ID.

        Args:
            organization_id: The organization (product type) ID
        """
        return await client.get(f"/organizations/{organization_id}/")

    @mcp.tool()
    async def create_organization(
        name: str,
        description: str | None = None,
        critical_product: bool = False,
        key_product: bool = False,
    ) -> dict[str, Any]:
        """Create a new organization (product type).

        Args:
            name: Organization name
            description: Description
            critical_product: Is critical product flag
            key_product: Is key product flag
        """
        data: dict[str, Any] = {
            "name": name,
            "description": description or "",
            "critical_product": critical_product,
            "key_product": key_product,
        }
        return await client.post("/organizations/", data)

    @mcp.tool()
    async def update_organization(
        organization_id: int,
        name: str | None = None,
        description: str | None = None,
    ) -> dict[str, Any]:
        """Update an organization (partial update).

        Args:
            organization_id: The organization ID
            name: New name
            description: New description
        """
        data: dict[str, Any] = {"name": name, "description": description}
        data = {k: v for k, v in data.items() if v is not None}
        return await client.patch(f"/organizations/{organization_id}/", data)

    @mcp.tool()
    async def delete_organization(organization_id: int) -> dict[str, Any]:
        """Delete an organization.

        Args:
            organization_id: The organization ID to delete
        """
        return await client.delete(f"/organizations/{organization_id}/")
