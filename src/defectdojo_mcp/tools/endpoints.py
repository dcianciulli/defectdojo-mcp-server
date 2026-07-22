"""Endpoint management tools for DefectDojo MCP Server."""

from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP

from defectdojo_mcp.client import DefectDojoClient


def register(mcp: FastMCP, client: DefectDojoClient) -> None:
    """Register endpoint-related tools."""

    @mcp.tool()
    async def list_endpoints(
        product_id: int | None = None,
        host: str | None = None,
        protocol: str | None = None,
        path: str | None = None,
        tag: str | None = None,
        limit: int = 25,
        offset: int = 0,
    ) -> dict[str, Any]:
        """List endpoints with optional filters.

        Args:
            product_id: Filter by product ID
            host: Filter by host (contains)
            protocol: Filter by protocol
            path: Filter by path (contains)
            tag: Filter by tag
            limit: Results per page
            offset: Pagination offset
        """
        params: dict[str, Any] = {
            "product": product_id,
            "host": host,
            "protocol": protocol,
            "path": path,
            "tag": tag,
        }
        return await client.get_list(
            "/endpoints/", params, limit=limit, offset=offset
        )

    @mcp.tool()
    async def get_endpoint(endpoint_id: int) -> dict[str, Any]:
        """Get a single endpoint by ID.

        Args:
            endpoint_id: The endpoint ID
        """
        return await client.get(f"/endpoints/{endpoint_id}/")

    @mcp.tool()
    async def list_endpoint_status(
        endpoint_id: int | None = None,
        finding_id: int | None = None,
        mitigated: bool | None = None,
        limit: int = 25,
        offset: int = 0,
    ) -> dict[str, Any]:
        """List endpoint statuses (relationship between endpoints and findings).

        Args:
            endpoint_id: Filter by endpoint ID
            finding_id: Filter by finding ID
            mitigated: Filter by mitigated status
            limit: Results per page
            offset: Pagination offset
        """
        params: dict[str, Any] = {
            "endpoint": endpoint_id,
            "finding": finding_id,
            "mitigated": mitigated,
        }
        return await client.get_list(
            "/endpoint_status/", params, limit=limit, offset=offset
        )
