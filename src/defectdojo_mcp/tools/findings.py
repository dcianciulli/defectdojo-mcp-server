"""Finding management tools for DefectDojo MCP Server."""

from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP

from defectdojo_mcp.client import DefectDojoClient


def register(mcp: FastMCP, client: DefectDojoClient) -> None:
    """Register finding-related tools."""

    @mcp.tool()
    async def list_findings(
        severity: str | None = None,
        active: bool | None = None,
        verified: bool | None = None,
        is_mitigated: bool | None = None,
        duplicate: bool | None = None,
        false_positive: bool | None = None,
        out_of_scope: bool | None = None,
        risk_accepted: bool | None = None,
        test_id: int | None = None,
        engagement_id: int | None = None,
        product_id: int | None = None,
        product_name: str | None = None,
        title: str | None = None,
        title_exact: str | None = None,
        cwe: int | None = None,
        vulnerability_id: str | None = None,
        reporter_id: int | None = None,
        mitigated_by_id: int | None = None,
        outside_of_sla: bool | None = None,
        tag: str | None = None,
        ordering: str | None = None,
        limit: int = 25,
        offset: int = 0,
    ) -> dict[str, Any]:
        """List findings with optional filters.

        Args:
            severity: Filter by severity (Critical, High, Medium, Low, Info)
            active: Filter active findings only
            verified: Filter verified findings only
            is_mitigated: Filter mitigated findings
            duplicate: Filter duplicates
            false_positive: Filter false positives (false_p)
            out_of_scope: Filter out-of-scope findings
            risk_accepted: Filter findings under an active risk acceptance
            test_id: Filter by test ID
            engagement_id: Filter by engagement ID (via test__engagement)
            product_id: Filter by product (asset) ID (via test__engagement__product)
            product_name: Filter by product (asset) name (server-side contains)
            title: Filter by title (server-side contains)
            title_exact: Filter by exact title
            cwe: Filter by CWE number
            vulnerability_id: Filter by CVE/vulnerability ID (e.g. CVE-2024-1234)
            reporter_id: Filter by reporter user ID
            mitigated_by_id: Filter by the user who mitigated
            outside_of_sla: Filter findings outside SLA
            tag: Filter by tag name (contains)
            ordering: Ordering fields (e.g. "-severity", "created", "-date")
            limit: Number of results per page (default 25)
            offset: Pagination offset
        """
        params: dict[str, Any] = {
            "severity": severity,
            "active": active,
            "verified": verified,
            "is_mitigated": is_mitigated,
            "duplicate": duplicate,
            "false_p": false_positive,
            "out_of_scope": out_of_scope,
            "risk_accepted": risk_accepted,
            "test": test_id,
            "test__engagement": engagement_id,
            "test__engagement__product": product_id,
            "product_name": product_name,
            "title": title,
            "exact_title": title_exact,
            "cwe": cwe,
            "vulnerability_id": vulnerability_id,
            "reporter": reporter_id,
            "mitigated_by": mitigated_by_id,
            "outside_of_sla": outside_of_sla,
            "tag": tag,
            "o": ordering,
        }
        return await client.get_list("/findings/", params, limit=limit, offset=offset)

    @mcp.tool()
    async def get_finding(finding_id: int) -> dict[str, Any]:
        """Get a single finding by ID.

        Args:
            finding_id: The finding ID
        """
        return await client.get(f"/findings/{finding_id}/")

    @mcp.tool()
    async def create_finding(
        title: str,
        severity: str,
        test_id: int,
        description: str | None = None,
        mitigation: str | None = None,
        impact: str | None = None,
        steps_to_reproduce: str | None = None,
        references: str | None = None,
        cwe: int | None = None,
        active: bool = True,
        verified: bool = False,
        numerical_severity: str | None = None,
        line: int | None = None,
        file_path: str | None = None,
        component_name: str | None = None,
        component_version: str | None = None,
        static_finding: bool | None = None,
        dynamic_finding: bool | None = None,
        tags: list[str] | None = None,
    ) -> dict[str, Any]:
        """Create a new finding.

        Args:
            title: Finding title
            severity: Severity level (Critical, High, Medium, Low, Info)
            test_id: ID of the test this finding belongs to
            description: Detailed description
            mitigation: Recommended mitigation
            impact: Impact description
            steps_to_reproduce: Steps to reproduce
            references: External references
            cwe: CWE identifier number
            active: Whether finding is active (default True)
            verified: Whether finding is verified (default False)
            numerical_severity: Numeric severity (S0-S4)
            line: Source code line number
            file_path: Source file path
            component_name: Affected component
            component_version: Component version
            static_finding: Is static analysis finding
            dynamic_finding: Is dynamic analysis finding
            tags: List of tags
        """
        data: dict[str, Any] = {
            "title": title,
            "severity": severity,
            "test": test_id,
            "description": description or "",
            "mitigation": mitigation,
            "impact": impact,
            "steps_to_reproduce": steps_to_reproduce,
            "references": references,
            "cwe": cwe,
            "active": active,
            "verified": verified,
            "numerical_severity": numerical_severity,
            "line": line,
            "file_path": file_path,
            "component_name": component_name,
            "component_version": component_version,
            "static_finding": static_finding,
            "dynamic_finding": dynamic_finding,
            "tags": tags,
        }
        # Remove None values
        data = {k: v for k, v in data.items() if v is not None}
        return await client.post("/findings/", data)

    @mcp.tool()
    async def update_finding(
        finding_id: int,
        title: str | None = None,
        severity: str | None = None,
        description: str | None = None,
        mitigation: str | None = None,
        impact: str | None = None,
        active: bool | None = None,
        verified: bool | None = None,
        is_mitigated: bool | None = None,
        tags: list[str] | None = None,
    ) -> dict[str, Any]:
        """Update an existing finding (partial update).

        Args:
            finding_id: The finding ID
            title: New title
            severity: New severity
            description: New description
            mitigation: New mitigation text
            impact: New impact text
            active: Set active status
            verified: Set verified status
            is_mitigated: Set mitigated status
            tags: Replace tags
        """
        data: dict[str, Any] = {
            "title": title,
            "severity": severity,
            "description": description,
            "mitigation": mitigation,
            "impact": impact,
            "active": active,
            "verified": verified,
            "is_mitigated": is_mitigated,
            "tags": tags,
        }
        data = {k: v for k, v in data.items() if v is not None}
        return await client.patch(f"/findings/{finding_id}/", data)

    @mcp.tool()
    async def verify_finding(finding_id: int) -> dict[str, Any]:
        """Mark a finding as verified.

        Args:
            finding_id: The finding ID to verify
        """
        return await client.post(f"/findings/{finding_id}/verify/", {})

    @mcp.tool()
    async def get_finding_duplicates(finding_id: int) -> dict[str, Any]:
        """Get duplicate findings for a given finding.

        Args:
            finding_id: The finding ID
        """
        return await client.get(f"/findings/{finding_id}/duplicate/")

    @mcp.tool()
    async def reset_finding_duplicate_status(finding_id: int) -> dict[str, Any]:
        """Reset the duplicate status of a finding.

        Args:
            finding_id: The finding ID
        """
        return await client.post(f"/findings/{finding_id}/duplicate/reset/", {})

    @mcp.tool()
    async def list_finding_notes(finding_id: int) -> dict[str, Any]:
        """List notes for a finding (ordered newest first).

        Args:
            finding_id: The finding ID
        """
        resp = await client.get(f"/findings/{finding_id}/notes/")
        # v3 returns {"finding_id": N, "notes": [...]} (not paginated)
        notes = resp.get("notes", []) if isinstance(resp, dict) else []
        return {"finding_id": finding_id, "count": len(notes), "notes": notes}

    @mcp.tool()
    async def add_finding_note(
        finding_id: int,
        entry: str,
        private: bool = False,
        note_type: int | None = None,
    ) -> dict[str, Any]:
        """Add a note to a finding.

        Args:
            finding_id: The finding ID
            entry: Note text content
            private: Whether the note is private (visible only to you and superusers)
            note_type: Note type ID (see list_note_types)
        """
        data: dict[str, Any] = {"entry": entry, "private": private}
        if note_type is not None:
            data["note_type"] = note_type
        await client.post(f"/findings/{finding_id}/notes/", data)
        return {"finding_id": finding_id, "added": True, "entry": entry, "private": private}

    @mcp.tool()
    async def remove_finding_note(finding_id: int, note_id: int) -> dict[str, Any]:
        """Remove a note from a finding.

        Args:
            finding_id: The finding ID
            note_id: The note ID to remove (see list_finding_notes)
        """
        await client.patch(
            f"/findings/{finding_id}/remove_note/", {"note_id": note_id}
        )
        return {"finding_id": finding_id, "note_id": note_id, "removed": True}

    @mcp.tool()
    async def list_finding_metadata(finding_id: int) -> dict[str, Any]:
        """List metadata key-value pairs for a finding.

        Args:
            finding_id: The finding ID
        """
        return await client.get(f"/findings/{finding_id}/metadata/")

    @mcp.tool()
    async def add_finding_metadata(
        finding_id: int, name: str, value: str
    ) -> dict[str, Any]:
        """Add metadata to a finding.

        Args:
            finding_id: The finding ID
            name: Metadata key name
            value: Metadata value
        """
        return await client.post(
            f"/findings/{finding_id}/metadata/", {"name": name, "value": value}
        )

    @mcp.tool()
    async def delete_finding(finding_id: int) -> dict[str, Any]:
        """Delete a finding.

        Args:
            finding_id: The finding ID to delete
        """
        return await client.delete(f"/findings/{finding_id}/")

    @mcp.tool()
    async def list_note_types(
        name: str | None = None,
        limit: int = 25,
        offset: int = 0,
    ) -> dict[str, Any]:
        """List available note types (usable in add_finding_note / close_finding).

        Args:
            name: Filter by name (contains)
            limit: Results per page (default 25)
            offset: Pagination offset
        """
        params: dict[str, Any] = {"name": name}
        return await client.get_list("/note_type/", params, limit=limit, offset=offset)
