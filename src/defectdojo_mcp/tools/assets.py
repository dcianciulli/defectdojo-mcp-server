"""Product/Asset management tools for DefectDojo MCP Server."""

from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP

from defectdojo_mcp.client import DefectDojoClient


def register(mcp: FastMCP, client: DefectDojoClient) -> None:
    """Register product/asset-related tools."""

    @mcp.tool()
    async def list_products(
        name: str | None = None,
        name_exact: str | None = None,
        organization_id: int | None = None,
        lifecycle: str | None = None,
        tag: str | None = None,
        external_audience: bool | None = None,
        internet_accessible: bool | None = None,
        limit: int = 25,
        offset: int = 0,
    ) -> dict[str, Any]:
        """List products (assets) with optional filters.

        Args:
            name: Filter by name (contains)
            name_exact: Filter by exact name
            organization_id: Filter by organization (product type) ID
            lifecycle: Filter by lifecycle (construction, production, retirement)
            tag: Filter by tag name (contains)
            external_audience: Filter by external audience flag
            internet_accessible: Filter by internet accessible flag
            limit: Results per page (default 25)
            offset: Pagination offset
        """
        params: dict[str, Any] = {
            "name": name,
            "name_exact": name_exact,
            "organization": organization_id,
            "lifecycle": lifecycle,
            "tag": tag,
            "external_audience": external_audience,
            "internet_accessible": internet_accessible,
        }
        return await client.get_list("/assets/", params, limit=limit, offset=offset)

    @mcp.tool()
    async def get_product(product_id: int) -> dict[str, Any]:
        """Get a single product by ID.

        Args:
            product_id: The product ID
        """
        return await client.get(f"/assets/{product_id}/")

    @mcp.tool()
    async def create_product(
        name: str,
        organization_id: int,
        description: str = "",
        lifecycle: str | None = None,
        platform: str | None = None,
        origin: str | None = None,
        business_criticality: str | None = None,
        external_audience: bool = False,
        internet_accessible: bool = False,
        tags: list[str] | None = None,
    ) -> dict[str, Any]:
        """Create a new product (asset).

        Args:
            name: Product name
            organization_id: Organization (product type) ID
            description: Product description
            lifecycle: Lifecycle stage (construction, production, retirement)
            platform: Platform (web service, desktop, iot, mobile, web)
            origin: Origin (third party library, purchased, contractor, internal, open source, outsourced)
            business_criticality: Business criticality (very high, high, medium, low, very low, none)
            external_audience: Has external audience
            internet_accessible: Is internet accessible
            tags: List of tags
        """
        data: dict[str, Any] = {
            "name": name,
            "prod_type": organization_id,
            "description": description,
            "lifecycle": lifecycle,
            "platform": platform,
            "origin": origin,
            "business_criticality": business_criticality,
            "external_audience": external_audience,
            "internet_accessible": internet_accessible,
            "tags": tags,
        }
        data = {k: v for k, v in data.items() if v is not None}
        return await client.post("/assets/", data)

    @mcp.tool()
    async def update_product(
        product_id: int,
        name: str | None = None,
        description: str | None = None,
        lifecycle: str | None = None,
        business_criticality: str | None = None,
        tags: list[str] | None = None,
    ) -> dict[str, Any]:
        """Update an existing product (partial update).

        Args:
            product_id: The product ID
            name: New name
            description: New description
            lifecycle: New lifecycle stage
            business_criticality: New business criticality
            tags: Replace tags
        """
        data: dict[str, Any] = {
            "name": name,
            "description": description,
            "lifecycle": lifecycle,
            "business_criticality": business_criticality,
            "tags": tags,
        }
        data = {k: v for k, v in data.items() if v is not None}
        return await client.patch(f"/assets/{product_id}/", data)

    @mcp.tool()
    async def delete_product(product_id: int) -> dict[str, Any]:
        """Delete a product.

        Args:
            product_id: The product ID to delete
        """
        return await client.delete(f"/assets/{product_id}/")
