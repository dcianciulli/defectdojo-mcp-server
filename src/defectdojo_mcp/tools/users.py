"""User management tools for DefectDojo MCP Server."""

from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP

from defectdojo_mcp.client import DefectDojoClient


def register(mcp: FastMCP, client: DefectDojoClient) -> None:
    """Register user-related tools."""

    @mcp.tool()
    async def list_users(
        username: str | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
        is_active: bool | None = None,
        is_superuser: bool | None = None,
        limit: int = 25,
        offset: int = 0,
    ) -> dict[str, Any]:
        """List users with optional filters.

        Args:
            username: Filter by username (contains)
            first_name: Filter by first name
            last_name: Filter by last name
            is_active: Filter by active status
            is_superuser: Filter by superuser status
            limit: Results per page
            offset: Pagination offset
        """
        params: dict[str, Any] = {
            "username": username,
            "first_name": first_name,
            "last_name": last_name,
            "is_active": is_active,
            "is_superuser": is_superuser,
        }
        return await client.get_list("/users/", params, limit=limit, offset=offset)

    @mcp.tool()
    async def get_user(user_id: int) -> dict[str, Any]:
        """Get a single user by ID.

        Args:
            user_id: The user ID
        """
        return await client.get(f"/users/{user_id}/")

    @mcp.tool()
    async def get_current_user() -> dict[str, Any]:
        """Get the currently authenticated user's profile."""
        return await client.get("/user_profile/")

    @mcp.tool()
    async def create_user(
        username: str,
        first_name: str = "",
        last_name: str = "",
        email: str = "",
        is_active: bool = True,
        is_superuser: bool = False,
    ) -> dict[str, Any]:
        """Create a new user.

        Args:
            username: Username
            first_name: First name
            last_name: Last name
            email: Email address
            is_active: Active status
            is_superuser: Superuser status
        """
        data: dict[str, Any] = {
            "username": username,
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "is_active": is_active,
            "is_superuser": is_superuser,
        }
        return await client.post("/users/", data)

    @mcp.tool()
    async def update_user(
        user_id: int,
        first_name: str | None = None,
        last_name: str | None = None,
        email: str | None = None,
        is_active: bool | None = None,
    ) -> dict[str, Any]:
        """Update a user (partial update).

        Args:
            user_id: The user ID
            first_name: New first name
            last_name: New last name
            email: New email
            is_active: Set active status
        """
        data: dict[str, Any] = {
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "is_active": is_active,
        }
        data = {k: v for k, v in data.items() if v is not None}
        return await client.patch(f"/users/{user_id}/", data)

    @mcp.tool()
    async def delete_user(user_id: int) -> dict[str, Any]:
        """Delete a user.

        Args:
            user_id: The user ID to delete
        """
        return await client.delete(f"/users/{user_id}/")
