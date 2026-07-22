"""Test management tools for DefectDojo MCP Server."""

from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP

from defectdojo_mcp.client import DefectDojoClient


def register(mcp: FastMCP, client: DefectDojoClient) -> None:
    """Register test-related tools."""

    @mcp.tool()
    async def list_tests(
        engagement_id: int | None = None,
        product_id: int | None = None,
        test_type: int | None = None,
        tag: str | None = None,
        title: str | None = None,
        limit: int = 25,
        offset: int = 0,
    ) -> dict[str, Any]:
        """List tests with optional filters.

        Args:
            engagement_id: Filter by engagement ID
            product_id: Filter by product ID (via engagement__product)
            test_type: Filter by test type ID
            tag: Filter by tag name (contains)
            title: Filter by title (contains)
            limit: Results per page (default 25)
            offset: Pagination offset
        """
        params: dict[str, Any] = {
            "engagement": engagement_id,
            "engagement__product": product_id,
            "test_type": test_type,
            "tag": tag,
            "title": title,
        }
        return await client.get_list("/tests/", params, limit=limit, offset=offset)

    @mcp.tool()
    async def get_test(test_id: int) -> dict[str, Any]:
        """Get a single test by ID.

        Args:
            test_id: The test ID
        """
        return await client.get(f"/tests/{test_id}/")

    @mcp.tool()
    async def create_test(
        engagement_id: int,
        test_type_id: int,
        target_start: str,
        target_end: str,
        title: str | None = None,
        description: str | None = None,
        lead_id: int | None = None,
        environment_id: int | None = None,
        version: str | None = None,
        branch_tag: str | None = None,
        build_id: str | None = None,
        commit_hash: str | None = None,
        tags: list[str] | None = None,
    ) -> dict[str, Any]:
        """Create a new test.

        Args:
            engagement_id: Engagement ID this test belongs to
            test_type_id: Test type ID
            target_start: Target start datetime (YYYY-MM-DD or ISO format)
            target_end: Target end datetime
            title: Test title
            description: Test description
            lead_id: Lead user ID
            environment_id: Environment ID
            version: Version string
            branch_tag: Branch or tag
            build_id: Build identifier
            commit_hash: Commit hash
            tags: List of tags
        """
        data: dict[str, Any] = {
            "engagement": engagement_id,
            "test_type": test_type_id,
            "target_start": target_start,
            "target_end": target_end,
            "title": title,
            "description": description,
            "lead": lead_id,
            "environment": environment_id,
            "version": version,
            "branch_tag": branch_tag,
            "build_id": build_id,
            "commit_hash": commit_hash,
            "tags": tags,
        }
        data = {k: v for k, v in data.items() if v is not None}
        return await client.post("/tests/", data)

    @mcp.tool()
    async def update_test(
        test_id: int,
        title: str | None = None,
        description: str | None = None,
        version: str | None = None,
        tags: list[str] | None = None,
    ) -> dict[str, Any]:
        """Update an existing test (partial update).

        Args:
            test_id: The test ID
            title: New title
            description: New description
            version: New version
            tags: Replace tags
        """
        data: dict[str, Any] = {
            "title": title,
            "description": description,
            "version": version,
            "tags": tags,
        }
        data = {k: v for k, v in data.items() if v is not None}
        return await client.patch(f"/tests/{test_id}/", data)

    @mcp.tool()
    async def delete_test(test_id: int) -> dict[str, Any]:
        """Delete a test.

        Args:
            test_id: The test ID to delete
        """
        return await client.delete(f"/tests/{test_id}/")

    @mcp.tool()
    async def list_test_types(
        name: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> dict[str, Any]:
        """List available test types (scan types).

        Args:
            name: Filter by name (contains)
            limit: Results per page
            offset: Pagination offset
        """
        params: dict[str, Any] = {"name": name}
        return await client.get_list(
            "/test_types/", params, limit=limit, offset=offset
        )

    @mcp.tool()
    async def list_test_notes(test_id: int) -> dict[str, Any]:
        """List notes for a test.

        Args:
            test_id: The test ID
        """
        return await client.get(f"/tests/{test_id}/notes/")

    @mcp.tool()
    async def add_test_note(
        test_id: int,
        entry: str,
        private: bool = False,
    ) -> dict[str, Any]:
        """Add a note to a test.

        Args:
            test_id: The test ID
            entry: Note text content
            private: Whether the note is private
        """
        return await client.post(
            f"/tests/{test_id}/notes/", {"entry": entry, "private": private}
        )
