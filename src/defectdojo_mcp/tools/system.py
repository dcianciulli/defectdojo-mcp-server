"""System administration tools for DefectDojo MCP Server."""

from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP

from defectdojo_mcp.client import DefectDojoClient


def register(mcp: FastMCP, client: DefectDojoClient) -> None:
    """Register system administration tools."""

    @mcp.tool()
    async def get_system_settings() -> dict[str, Any]:
        """Get DefectDojo system settings."""
        data = await client.get_list("/system_settings/", limit=1)
        results = data.get("results", [])
        if results:
            return results[0]
        return data

    @mcp.tool()
    async def update_system_settings(
        settings_id: int = 1,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Update system settings (partial update).

        Args:
            settings_id: Settings ID (usually 1)
            **kwargs: Key-value pairs of settings to update
        """
        return await client.patch(f"/system_settings/{settings_id}/", kwargs)

    @mcp.tool()
    async def get_celery_status() -> dict[str, Any]:
        """Get Celery worker and queue status.

        Returns worker liveness, pending queue length, and configuration.
        """
        return await client.get("/celery/status/")

    @mcp.tool()
    async def get_celery_queue_details() -> list[dict[str, Any]]:
        """Get per-task breakdown of the Celery queue.

        Returns task names, counts, and queue positions.
        May be slow for large queues.
        """
        return await client.get("/celery/queue/details/")

    @mcp.tool()
    async def purge_celery_queue() -> dict[str, Any]:
        """Purge all pending Celery tasks from the queue.

        Tasks already being executed are not affected.
        Use with caution - this removes ALL pending tasks.
        """
        return await client.post("/celery/queue/purge/")

    @mcp.tool()
    async def purge_celery_task(task_name: str) -> dict[str, Any]:
        """Purge all queued instances of a specific Celery task.

        Args:
            task_name: The task name to purge (e.g., "dojo.tasks.async_update")
        """
        return await client.post(
            "/celery/queue/task/purge/", {"task_name": task_name}
        )

    @mcp.tool()
    async def list_risk_acceptances(
        finding_id: int | None = None,
        product_id: int | None = None,
        owner_id: int | None = None,
        limit: int = 25,
        offset: int = 0,
    ) -> dict[str, Any]:
        """List risk acceptances.

        Args:
            finding_id: Filter by finding ID
            product_id: Filter by product ID
            owner_id: Filter by owner user ID
            limit: Results per page
            offset: Pagination offset
        """
        params: dict[str, Any] = {
            "accepted_findings": finding_id,
            "product": product_id,
            "owner": owner_id,
        }
        return await client.get_list(
            "/risk_acceptance/", params, limit=limit, offset=offset
        )

    @mcp.tool()
    async def get_risk_acceptance(risk_acceptance_id: int) -> dict[str, Any]:
        """Get a risk acceptance by ID.

        Args:
            risk_acceptance_id: The risk acceptance ID
        """
        return await client.get(f"/risk_acceptance/{risk_acceptance_id}/")

    @mcp.tool()
    async def create_risk_acceptance(
        name: str,
        owner_id: int,
        accepted_findings: list[int],
        recommendation: str | None = None,
        recommendation_details: str | None = None,
        decision: str | None = None,
        decision_details: str | None = None,
        expiration_date: str | None = None,
    ) -> dict[str, Any]:
        """Create a new risk acceptance.

        Args:
            name: Risk acceptance name
            owner_id: Owner user ID
            accepted_findings: List of finding IDs to accept
            recommendation: Recommendation (fix, accept, transfer)
            recommendation_details: Details about the recommendation
            decision: Decision (accept, avoid, mitigate, fix, transfer)
            decision_details: Details about the decision
            expiration_date: Expiration date (YYYY-MM-DD)
        """
        data: dict[str, Any] = {
            "name": name,
            "owner": owner_id,
            "accepted_findings": accepted_findings,
            "recommendation": recommendation,
            "recommendation_details": recommendation_details,
            "decision": decision,
            "decision_details": decision_details,
            "expiration_date": expiration_date,
        }
        data = {k: v for k, v in data.items() if v is not None}
        return await client.post("/risk_acceptance/", data)

    @mcp.tool()
    async def delete_risk_acceptance(risk_acceptance_id: int) -> dict[str, Any]:
        """Delete a risk acceptance.

        Args:
            risk_acceptance_id: The risk acceptance ID
        """
        return await client.delete(f"/risk_acceptance/{risk_acceptance_id}/")

    @mcp.tool()
    async def list_notifications(
        limit: int = 25,
        offset: int = 0,
    ) -> dict[str, Any]:
        """List notification configurations.

        Args:
            limit: Results per page
            offset: Pagination offset
        """
        return await client.get_list("/notifications/", limit=limit, offset=offset)

    @mcp.tool()
    async def list_sla_configurations(
        limit: int = 25,
        offset: int = 0,
    ) -> dict[str, Any]:
        """List SLA configurations.

        Args:
            limit: Results per page
            offset: Pagination offset
        """
        return await client.get_list(
            "/sla_configurations/", limit=limit, offset=offset
        )
