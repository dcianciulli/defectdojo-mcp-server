"""Finding lifecycle tools for DefectDojo MCP Server.

Implements closing / reopening / reactivating findings per DefectDojo v3 API:
- close_finding          -> POST /findings/{id}/close/  (FindingCloseRequest)
- reopen_finding         -> PATCH /findings/{id}/       (active=true, is_mitigated=false, ...)
- accept_risk            -> POST /risk_acceptance/      (RiskAcceptanceRequest, expiration enforced)
- accept_risks_vulnerability -> POST /findings/accept_risks/ (AcceptedRiskRequest[] by vulnerability_id)
"""

from __future__ import annotations

import re
from datetime import datetime
from typing import Any

from mcp.server.fastmcp import FastMCP

from defectdojo_mcp.client import DefectDojoClient

# Status update payload returned by close/reopen/accept tools. Kept deliberately
# minimal: DefectDojo echoes back the whole finding object and serializers may
# reject unknown/None fields, so we build our own summary instead.
_DATE_RE = re.compile(r"\d{4}-\d{2}-\d{2}")


def register(mcp: FastMCP, client: DefectDojoClient) -> None:
    """Register finding lifecycle tools."""

    @mcp.tool()
    async def close_finding(
        finding_id: int,
        closure_type: str = "mitigated",
        note: str | None = None,
        note_type: int | None = None,
        mitigated: str | None = None,
        out_of_scope: bool = False,
        duplicate: bool = False,
    ) -> dict[str, Any]:
        """Close a finding. Requires closure_type; use the dedicated tools below when unsure.

        Prefer the semantic aliases:
        - close_finding_false_positive(finding_id, note)
        - close_finding_mitigated(finding_id, note)
        - close_finding_duplicate(finding_id, duplicate_of)

        Args:
            finding_id: The finding ID to close
            closure_type: One of "false_positive", "mitigated", "duplicate"
            note: Optional note recorded on the finding at closure time
            note_type: Optional note type ID (see list_note_types)
            mitigated: Mitigation datetime (ISO 8601, defaults to now)
            out_of_scope: Mark finding as out of scope (only meaningful with closure_type="false_positive")
            duplicate: Mark finding as duplicate (only meaningful with closure_type="duplicate")
        """
        allowed = ("false_positive", "mitigated", "duplicate")
        if closure_type not in allowed:
            return {"error": f"closure_type must be one of {allowed}"}
        body: dict[str, Any] = {"is_mitigated": True}
        if closure_type == "false_positive":
            body["false_p"] = True
            if out_of_scope:
                body["out_of_scope"] = True
        elif closure_type == "duplicate":
            body["duplicate"] = True
        if mitigated:
            body["mitigated"] = mitigated
        if note:
            body["note"] = note
            if note_type is not None:
                body["note_type"] = note_type
        try:
            result = await client.post(f"/findings/{finding_id}/close/", body)
        except Exception as exc:
            detail = getattr(exc, "public_detail", None) or str(exc)
            return {"error": f"close failed for finding {finding_id}: {detail}"}
        if isinstance(result, dict) and result.get("message"):
            return {
                "error": f"close failed for finding {finding_id}",
                "detail": result.get("message"),
            }
        return {
            "finding_id": finding_id,
            "closed": True,
            "closure_type": closure_type,
            "note_added": bool(note),
        }

    @mcp.tool()
    async def close_finding_false_positive(
        finding_id: int,
        note: str | None = None,
        note_type: int | None = None,
        out_of_scope: bool = False,
    ) -> dict[str, Any]:
        """Close a finding as a false positive (and optionally out of scope).

        Args:
            finding_id: The finding ID to close
            note: Why this is a false positive (recommended)
            note_type: Optional note type ID (see list_note_types)
            out_of_scope: Also mark the finding as out of scope
        """
        body: dict[str, Any] = {"is_mitigated": True, "false_p": True}
        if out_of_scope:
            body["out_of_scope"] = True
        if note:
            body["note"] = note
            if note_type is not None:
                body["note_type"] = note_type
        try:
            result = await client.post(f"/findings/{finding_id}/close/", body)
        except Exception as exc:
            detail = getattr(exc, "public_detail", None) or str(exc)
            return {"error": f"close failed for finding {finding_id}: {detail}"}
        if isinstance(result, dict) and result.get("message"):
            return {
                "error": f"close failed for finding {finding_id}",
                "detail": result.get("message"),
            }
        return {
            "finding_id": finding_id,
            "closed": True,
            "closure_type": "false_positive",
            "out_of_scope": out_of_scope,
            "note_added": bool(note),
        }

    @mcp.tool()
    async def close_finding_mitigated(
        finding_id: int,
        note: str | None = None,
        note_type: int | None = None,
        mitigated: str | None = None,
    ) -> dict[str, Any]:
        """Close a finding because the vulnerability was remediated (fix applied).

        Args:
            finding_id: The finding ID to close
            note: How/where it was fixed (recommended)
            note_type: Optional note type ID (see list_note_types)
            mitigated: Mitigation datetime (ISO 8601, defaults to now server-side)
        """
        body: dict[str, Any] = {"is_mitigated": True}
        if mitigated:
            body["mitigated"] = mitigated
        if note:
            body["note"] = note
            if note_type is not None:
                body["note_type"] = note_type
        try:
            result = await client.post(f"/findings/{finding_id}/close/", body)
        except Exception as exc:
            detail = getattr(exc, "public_detail", None) or str(exc)
            return {"error": f"close failed for finding {finding_id}: {detail}"}
        if isinstance(result, dict) and result.get("message"):
            return {
                "error": f"close failed for finding {finding_id}",
                "detail": result.get("message"),
            }
        return {
            "finding_id": finding_id,
            "closed": True,
            "closure_type": "mitigated",
            "note_added": bool(note),
        }

    @mcp.tool()
    async def close_finding_duplicate(
        finding_id: int,
        duplicate_of: int,
        note: str | None = None,
    ) -> dict[str, Any]:
        """Close a finding as duplicate of another finding.

        Args:
            finding_id: The finding ID to close
            duplicate_of: The ID of the original (canonical) finding
            note: Optional note
        """
        # link the duplicate first, then close
        try:
            await client.patch(f"/findings/{finding_id}/", {"duplicate_finding": duplicate_of})
        except Exception as exc:
            detail = getattr(exc, "public_detail", None) or str(exc)
            return {"error": f"linking duplicate failed for finding {finding_id}: {detail}"}
        body: dict[str, Any] = {"is_mitigated": True, "duplicate": True}
        if note:
            body["note"] = note
        try:
            result = await client.post(f"/findings/{finding_id}/close/", body)
        except Exception as exc:
            detail = getattr(exc, "public_detail", None) or str(exc)
            return {"error": f"close failed for finding {finding_id}: {detail}"}
        if isinstance(result, dict) and result.get("message"):
            return {
                "error": f"close failed for finding {finding_id}",
                "detail": result.get("message"),
            }
        return {
            "finding_id": finding_id,
            "closed": True,
            "closure_type": "duplicate",
            "duplicate_of": duplicate_of,
            "note_added": bool(note),
        }

    @mcp.tool()
    async def reopen_finding(
        finding_id: int,
        note: str | None = None,
        restore_false_positive: bool = False,
        restore_out_of_scope: bool = False,
    ) -> dict[str, Any]:
        """Reopen (reactivate) a closed/mitigated finding.

        Clears the mitigated state and any false-positive/duplicate/out-of-scope flags
        unless explicitly restored.

        Args:
            finding_id: The finding ID to reopen
            note: Optional note explaining the reopening
            restore_false_positive: Keep the false_p flag as-is instead of clearing it
            restore_out_of_scope: Keep the out_of_scope flag as-is instead of clearing it
        """
        body: dict[str, Any] = {
            "active": True,
            "is_mitigated": False,
            "mitigated": None,
            "mitigated_by": None,
            "false_p": bool(restore_false_positive),
            "out_of_scope": bool(restore_out_of_scope),
            "duplicate": False,
        }
        try:
            await client.patch(f"/findings/{finding_id}/", body)
        except Exception as exc:
            detail = getattr(exc, "public_detail", None) or str(exc)
            return {"error": f"reopen failed for finding {finding_id}: {detail}"}
        if note:
            try:
                await client.post(
                    f"/findings/{finding_id}/notes/",
                    {"entry": note, "private": False},
                )
            except Exception:
                pass  # reopening succeeded; note failure is non-fatal
        return {"finding_id": finding_id, "closed": False, "reopened": True}

    @mcp.tool()
    async def accept_risk(
        finding_ids: list[int],
        accepted_by: str,
        justification: str,
        expiration_date: str,
        decision: str | None = None,
        decision_details: str | None = None,
        recommendation: str | None = None,
        recommendation_details: str | None = None,
        reactivate_expired: bool = True,
        restart_sla_expired: bool = False,
        owner_id: int | None = None,
        name: str | None = None,
    ) -> dict[str, Any]:
        """Accept the risk of one or more findings (risk acceptance with mandatory expiration date).

        Creates a RiskAcceptance object. The expiration date is MANDATORY: findings
        are reactivated automatically when it passes (unless reactivate_expired=False).
        Risk acceptance is discouraged in favor of fixing; always require an explicit
        business justification and a named approver.

        Args:
            finding_ids: List of finding IDs to accept
            accepted_by: Name/email of the person accepting the risk
            justification: Business justification for accepting
            expiration_date: Mandatory expiration (ISO date "YYYY-MM-DD" or full ISO datetime). Must be in the future.
            decision: Risk treatment by risk owner: A=Accept, V=Avoid, M=Mitigate, F=Fix, T=Transfer
            decision_details: Details of the decision / compensating controls
            recommendation: Security team recommendation: A=Accept, V=Avoid, M=Mitigate, F=Fix, T=Transfer
            recommendation_details: Details of the recommendation
            reactivate_expired: Reactivate findings when the acceptance expires (default True)
            restart_sla_expired: Restart SLA when the acceptance expires (default False)
            owner_id: Owner user ID (defaults to the authenticated user)
            name: Acceptance name (defaults to "Risk acceptance <date> (<n> findings)")
        """
        # Validate expiration
        date_part = _DATE_RE.match(expiration_date.strip())
        if not date_part:
            return {"error": f"expiration_date '{expiration_date}' is not a valid date (expected YYYY-MM-DD or ISO datetime)"}
        exp_date = datetime.strptime(date_part.group(0), "%Y-%m-%d")
        today = datetime.now().combine(datetime.today().date(), datetime.min.time())
        if exp_date.date() <= today.date():
            return {"error": f"expiration_date must be in the future (got {exp_date.date()})"}
        # Require an explicit decision when provided: must be one of A/V/M/F/T
        for label, value in (("decision", decision), ("recommendation", recommendation)):
            if value is not None and value not in ("A", "V", "M", "F", "T"):
                return {"error": f"{label} must be one of A, V, M, F, T"}
        owner = owner_id
        if owner is None:
            try:
                me = await client.get("/user_profile/")
                owner = me["user"]["id"]
            except Exception:
                return {"error": "owner_id is required (could not resolve current user)"}
        final_name = name or f"Risk acceptance {exp_date.date().isoformat()} ({len(finding_ids)} findings)"
        data: dict[str, Any] = {
            "name": final_name,
            "owner": owner,
            "accepted_findings": finding_ids,
            "accepted_by": accepted_by,
            "expiration_date": expiration_date,
            "reactivate_expired": reactivate_expired,
            "restart_sla_expired": restart_sla_expired,
        }
        for key, value in (
            ("decision", decision),
            ("decision_details", decision_details),
            ("recommendation", recommendation),
            ("recommendation_details", recommendation_details),
        ):
            if value is not None:
                data[key] = value
        try:
            result = await client.post("/risk_acceptance/", data)
        except Exception as exc:
            detail = getattr(exc, "public_detail", None) or str(exc)
            return {"error": f"risk acceptance failed: {detail}"}
        if not isinstance(result, dict):
            return {"error": "unexpected response from /risk_acceptance/"}
        return {
            "risk_acceptance_id": result.get("id"),
            "name": result.get("name"),
            "accepted_findings": result.get("accepted_findings"),
            "expiration_date": result.get("expiration_date"),
            "reactivate_expired": result.get("reactivate_expired"),
        }

    @mcp.tool()
    async def accept_risks_vulnerability(
        vulnerability_ids: list[str],
        accepted_by: str,
        justification: str,
    ) -> dict[str, Any]:
        """Bulk accept risk for findings matching vulnerability IDs (CVEs).

        Uses the native /findings/accept_risks/ endpoint: matches findings by
        vulnerability_id (CVE) inside the CURRENT engagement context. Use accept_risk()
        instead when you need explicit finding IDs and an expiration date.

        Args:
            vulnerability_ids: CVE or advisory IDs (e.g. ["CVE-2024-1234"])
            accepted_by: Name/email of the person accepting the risk
            justification: Justification for accepting findings with these vulnerability IDs
        """
        if not vulnerability_ids:
            return {"error": "vulnerability_ids must not be empty"}
        payload = [
            {
                "vulnerability_id": vid,
                "accepted_by": accepted_by,
                "justification": justification,
            }
            for vid in vulnerability_ids
        ]
        try:
            result = await client.post("/findings/accept_risks/", payload)
        except Exception as exc:
            detail = getattr(exc, "public_detail", None) or str(exc)
            return {"error": f"accept_risks failed: {detail}"}
        return {"accepted": payload}

    @mcp.tool()
    async def expire_risk_acceptance(
        risk_acceptance_id: int,
        reason: str | None = None,
    ) -> dict[str, Any]:
        """Expire a risk acceptance early (reactivates its findings).

        Args:
            risk_acceptance_id: The risk acceptance ID
            reason: Optional reason for expiring
        """
        body: dict[str, Any] = {}
        if reason:
            body["reason"] = reason
        try:
            result = await client.post(f"/risk_acceptance/{risk_acceptance_id}/expire/", body)
        except Exception as exc:
            detail = getattr(exc, "public_detail", None) or str(exc)
            return {"error": f"expire failed for risk acceptance {risk_acceptance_id}: {detail}"}
        return {
            "risk_acceptance_id": risk_acceptance_id,
            "expired": True,
            "expiration_date": (result or {}).get("expiration_date") if isinstance(result, dict) else None,
        }

    @mcp.tool()
    async def reinstate_risk_acceptance(
        risk_acceptance_id: int,
        expiration_date: str,
        reason: str | None = None,
    ) -> dict[str, Any]:
        """Reinstate an expired risk acceptance with a new (mandatory) expiration date.

        Args:
            risk_acceptance_id: The risk acceptance ID
            expiration_date: New expiration date (YYYY-MM-DD or ISO datetime), must be in the future
            reason: Optional reason
        """
        date_part = _DATE_RE.match(expiration_date.strip())
        if not date_part:
            return {"error": f"expiration_date '{expiration_date}' is not a valid date (expected YYYY-MM-DD or ISO datetime)"}
        exp_date = datetime.strptime(date_part.group(0), "%Y-%m-%d")
        today = datetime.now().combine(datetime.today().date(), datetime.min.time())
        if exp_date.date() <= today.date():
            return {"error": f"expiration_date must be in the future (got {exp_date.date()})"}
        body: dict[str, Any] = {"expiration_date": expiration_date}
        if reason:
            body["reason"] = reason
        try:
            result = await client.post(f"/risk_acceptance/{risk_acceptance_id}/reinstate/", body)
        except Exception as exc:
            detail = getattr(exc, "public_detail", None) or str(exc)
            return {"error": f"reinstate failed for risk acceptance {risk_acceptance_id}: {detail}"}
        return {
            "risk_acceptance_id": risk_acceptance_id,
            "reinstated": True,
            "expiration_date": (result or {}).get("expiration_date") if isinstance(result, dict) else None,
        }
