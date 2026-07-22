"""Scan import/reimport tools for DefectDojo MCP Server."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from mcp.server.fastmcp import FastMCP

from defectdojo_mcp.client import DefectDojoClient


def register(mcp: FastMCP, client: DefectDojoClient) -> None:
    """Register import-related tools."""

    @mcp.tool()
    async def import_scan(
        scan_type: str,
        file_path: str | None = None,
        scan_data: str | None = None,
        engagement_id: int | None = None,
        product_name: str | None = None,
        product_type_name: str | None = None,
        engagement_name: str | None = None,
        test_title: str | None = None,
        auto_create_context: bool = False,
        active: bool = True,
        verified: bool = False,
        close_old_findings: bool = False,
        close_old_findings_product_scope: bool = False,
        push_to_jira: bool = False,
        minimum_severity: str = "Info",
        deduplication_on_engagement: bool = False,
        environment: str | None = None,
        version: str | None = None,
        build_id: str | None = None,
        branch_tag: str | None = None,
        commit_hash: str | None = None,
        service: str | None = None,
        group_by: str | None = None,
        tags: list[str] | None = None,
    ) -> dict[str, Any]:
        """Import a scan report into DefectDojo.

        Either engagement_id OR (product_name + auto_create_context=True) must be provided.
        Either file_path (local file) or scan_data (raw content) must be provided.

        Args:
            scan_type: Scanner type (e.g., "ZAP Scan", "Nessus Scan", "SARIF", "Trivy Scan", etc.)
            file_path: Path to the scan results file on the local filesystem
            scan_data: Raw scan data as string (alternative to file_path)
            engagement_id: Target engagement ID
            product_name: Product name (for auto-create context)
            product_type_name: Product type name (for auto-create context)
            engagement_name: Engagement name (for auto-create context)
            test_title: Custom test title
            auto_create_context: Auto-create product/engagement if they don't exist
            active: Mark findings as active
            verified: Mark findings as verified
            close_old_findings: Close findings not present in new scan
            close_old_findings_product_scope: Close at product scope
            push_to_jira: Push findings to JIRA
            minimum_severity: Minimum severity to import (Info, Low, Medium, High, Critical)
            deduplication_on_engagement: Deduplicate within engagement
            environment: Environment name
            version: Version being scanned
            build_id: Build ID
            branch_tag: Branch or tag
            commit_hash: Commit hash
            service: Service name
            group_by: Group findings by (component_name, component_name+component_version, file_path)
            tags: Tags to apply
        """
        form_data: dict[str, Any] = {
            "scan_type": scan_type,
            "active": str(active).lower(),
            "verified": str(verified).lower(),
            "close_old_findings": str(close_old_findings).lower(),
            "close_old_findings_product_scope": str(close_old_findings_product_scope).lower(),
            "push_to_jira": str(push_to_jira).lower(),
            "minimum_severity": minimum_severity,
            "auto_create_context": str(auto_create_context).lower(),
            "deduplication_on_engagement": str(deduplication_on_engagement).lower(),
        }

        if engagement_id is not None:
            form_data["engagement"] = str(engagement_id)
        if product_name:
            form_data["product_name"] = product_name
        if product_type_name:
            form_data["product_type_name"] = product_type_name
        if engagement_name:
            form_data["engagement_name"] = engagement_name
        if test_title:
            form_data["test_title"] = test_title
        if environment:
            form_data["environment"] = environment
        if version:
            form_data["version"] = version
        if build_id:
            form_data["build_id"] = build_id
        if branch_tag:
            form_data["branch_tag"] = branch_tag
        if commit_hash:
            form_data["commit_hash"] = commit_hash
        if service:
            form_data["service"] = service
        if group_by:
            form_data["group_by"] = group_by
        if tags:
            form_data["tags"] = tags

        files = None
        if file_path:
            p = Path(file_path)
            if not p.exists():
                return {"error": f"File not found: {file_path}"}
            files = {"file": (p.name, p.read_bytes())}
        elif scan_data:
            files = {"file": ("scan_data.json", scan_data.encode())}
        else:
            return {"error": "Either file_path or scan_data must be provided"}

        return await client.post_multipart("/import-scan/", form_data, files)

    @mcp.tool()
    async def reimport_scan(
        scan_type: str,
        test_id: int | None = None,
        file_path: str | None = None,
        scan_data: str | None = None,
        product_name: str | None = None,
        product_type_name: str | None = None,
        engagement_name: str | None = None,
        test_title: str | None = None,
        auto_create_context: bool = False,
        active: bool = True,
        verified: bool = False,
        close_old_findings: bool = True,
        close_old_findings_product_scope: bool = False,
        push_to_jira: bool = False,
        minimum_severity: str = "Info",
        do_not_reactivate: bool = False,
        environment: str | None = None,
        version: str | None = None,
        build_id: str | None = None,
        branch_tag: str | None = None,
        commit_hash: str | None = None,
        service: str | None = None,
        group_by: str | None = None,
        tags: list[str] | None = None,
    ) -> dict[str, Any]:
        """Reimport a scan report (update existing test with new results).

        Either test_id OR (product_name + test_title + auto_create_context) must be provided.
        Either file_path or scan_data must be provided.

        Args:
            scan_type: Scanner type (e.g., "ZAP Scan", "Nessus Scan", "SARIF", etc.)
            test_id: Existing test ID to reimport into
            file_path: Path to the scan results file
            scan_data: Raw scan data as string
            product_name: Product name (for auto-create context)
            product_type_name: Product type name (for auto-create context)
            engagement_name: Engagement name (for auto-create context)
            test_title: Test title (for matching existing test)
            auto_create_context: Auto-create context if it doesn't exist
            active: Mark findings as active
            verified: Mark findings as verified
            close_old_findings: Close findings not in new scan (default True)
            close_old_findings_product_scope: Close at product scope
            push_to_jira: Push to JIRA
            minimum_severity: Minimum severity
            do_not_reactivate: Don't reactivate closed findings
            environment: Environment name
            version: Version being scanned
            build_id: Build ID
            branch_tag: Branch or tag
            commit_hash: Commit hash
            service: Service name
            group_by: Group findings by field
            tags: Tags to apply
        """
        form_data: dict[str, Any] = {
            "scan_type": scan_type,
            "active": str(active).lower(),
            "verified": str(verified).lower(),
            "close_old_findings": str(close_old_findings).lower(),
            "close_old_findings_product_scope": str(close_old_findings_product_scope).lower(),
            "push_to_jira": str(push_to_jira).lower(),
            "minimum_severity": minimum_severity,
            "auto_create_context": str(auto_create_context).lower(),
            "do_not_reactivate": str(do_not_reactivate).lower(),
        }

        if test_id is not None:
            form_data["test"] = str(test_id)
        if product_name:
            form_data["product_name"] = product_name
        if product_type_name:
            form_data["product_type_name"] = product_type_name
        if engagement_name:
            form_data["engagement_name"] = engagement_name
        if test_title:
            form_data["test_title"] = test_title
        if environment:
            form_data["environment"] = environment
        if version:
            form_data["version"] = version
        if build_id:
            form_data["build_id"] = build_id
        if branch_tag:
            form_data["branch_tag"] = branch_tag
        if commit_hash:
            form_data["commit_hash"] = commit_hash
        if service:
            form_data["service"] = service
        if group_by:
            form_data["group_by"] = group_by
        if tags:
            form_data["tags"] = tags

        files = None
        if file_path:
            p = Path(file_path)
            if not p.exists():
                return {"error": f"File not found: {file_path}"}
            files = {"file": (p.name, p.read_bytes())}
        elif scan_data:
            files = {"file": ("scan_data.json", scan_data.encode())}
        else:
            return {"error": "Either file_path or scan_data must be provided"}

        return await client.post_multipart("/reimport-scan/", form_data, files)
