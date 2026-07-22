"""Engagement management tools for DefectDojo MCP Server."""

from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP

from defectdojo_mcp.client import DefectDojoClient


def register(mcp: FastMCP, client: DefectDojoClient) -> None:
    """Register engagement-related tools."""

    @mcp.tool()
    async def list_engagements(
        product_id: int | None = None,
        name: str | None = None,
        status: str | None = None,
        engagement_type: str | None = None,
        tag: str | None = None,
        limit: int = 25,
        offset: int = 0,
    ) -> dict[str, Any]:
        """List engagements with optional filters.

        Args:
            product_id: Filter by product ID
            name: Filter by name (contains)
            status: Filter by status (Not Started, In Progress, Completed)
            engagement_type: Filter by type (Interactive, CI/CD)
            tag: Filter by tag name
            limit: Results per page (default 25)
            offset: Pagination offset
        """
        params: dict[str, Any] = {
            "product": product_id,
            "name": name,
            "status": status,
            "engagement_type": engagement_type,
            "tag": tag,
        }
        return await client.get_list(
            "/engagements/", params, limit=limit, offset=offset
        )

    @mcp.tool()
    async def get_engagement(engagement_id: int) -> dict[str, Any]:
        """Get a single engagement by ID.

        Args:
            engagement_id: The engagement ID
        """
        return await client.get(f"/engagements/{engagement_id}/")

    @mcp.tool()
    async def create_engagement(
        name: str,
        product_id: int,
        target_start: str,
        target_end: str,
        engagement_type: str = "Interactive",
        status: str = "In Progress",
        description: str | None = None,
        lead_id: int | None = None,
        build_id: str | None = None,
        commit_hash: str | None = None,
        branch_tag: str | None = None,
        source_code_management_uri: str | None = None,
        deduplication_on_engagement: bool = False,
        tags: list[str] | None = None,
    ) -> dict[str, Any]:
        """Create a new engagement.

        Args:
            name: Engagement name
            product_id: Product ID this engagement belongs to
            target_start: Target start date (YYYY-MM-DD)
            target_end: Target end date (YYYY-MM-DD)
            engagement_type: Type (Interactive or CI/CD)
            status: Status (Not Started, In Progress, Completed)
            description: Description
            lead_id: Lead user ID
            build_id: Build identifier
            commit_hash: Commit hash
            branch_tag: Branch or tag name
            source_code_management_uri: SCM URI
            deduplication_on_engagement: Dedupe scoped to engagement
            tags: List of tags
        """
        data: dict[str, Any] = {
            "name": name,
            "product": product_id,
            "target_start": target_start,
            "target_end": target_end,
            "engagement_type": engagement_type,
            "status": status,
            "description": description,
            "lead": lead_id,
            "build_id": build_id,
            "commit_hash": commit_hash,
            "branch_tag": branch_tag,
            "source_code_management_uri": source_code_management_uri,
            "deduplication_on_engagement": deduplication_on_engagement,
            "tags": tags,
        }
        data = {k: v for k, v in data.items() if v is not None}
        return await client.post("/engagements/", data)

    @mcp.tool()
    async def update_engagement(
        engagement_id: int,
        name: str | None = None,
        status: str | None = None,
        description: str | None = None,
        target_start: str | None = None,
        target_end: str | None = None,
        tags: list[str] | None = None,
    ) -> dict[str, Any]:
        """Update an existing engagement (partial update).

        Args:
            engagement_id: The engagement ID
            name: New name
            status: New status (Not Started, In Progress, Completed)
            description: New description
            target_start: New target start date
            target_end: New target end date
            tags: Replace tags
        """
        data: dict[str, Any] = {
            "name": name,
            "status": status,
            "description": description,
            "target_start": target_start,
            "target_end": target_end,
            "tags": tags,
        }
        data = {k: v for k, v in data.items() if v is not None}
        return await client.patch(f"/engagements/{engagement_id}/", data)

    @mcp.tool()
    async def close_engagement(engagement_id: int) -> dict[str, Any]:
        """Close an engagement.

        Args:
            engagement_id: The engagement ID to close
        """
        return await client.post(f"/engagements/{engagement_id}/close/", {})

    @mcp.tool()
    async def delete_engagement(engagement_id: int) -> dict[str, Any]:
        """Delete an engagement.

        Args:
            engagement_id: The engagement ID to delete
        """
        return await client.delete(f"/engagements/{engagement_id}/")

    @mcp.tool()
    async def list_engagement_notes(engagement_id: int) -> dict[str, Any]:
        """List notes for an engagement.

        Args:
            engagement_id: The engagement ID
        """
        return await client.get(f"/engagements/{engagement_id}/notes/")

    @mcp.tool()
    async def add_engagement_note(
        engagement_id: int,
        entry: str,
        private: bool = False,
    ) -> dict[str, Any]:
        """Add a note to an engagement.

        Args:
            engagement_id: The engagement ID
            entry: Note text content
            private: Whether the note is private
        """
        return await client.post(
            f"/engagements/{engagement_id}/notes/",
            {"entry": entry, "private": private},
        )
