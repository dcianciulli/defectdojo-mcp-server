"""Live integration test of the reworked lifecycle tools against your-defectdojo.example.com.

Runs in-process (same code the MCP server registers), against finding 20323
("Finding2" on Test Asset 105). Cleans up after itself.
"""
import asyncio
import json
import os
import sys

os.environ.setdefault("DEFECTDOJO_URL", "https://your-defectdojo.example.com")
os.environ.setdefault("DEFECTDOJO_API_KEY", os.environ.get("DEFECTDOJO_API_KEY", ""))

from defectdojo_mcp.server import create_server

mcp = create_server()
tm = mcp._tool_manager
TOOLS = {t.name: t.fn for t in tm._tools.values()}

FID = 20323
results = []


def record(step, res):
    s = json.dumps(res, ensure_ascii=False, default=str)
    print(f"[{step}] {s[:400]}")
    results.append((step, res))


async def main():
    # 0. current state
    f = await TOOLS["get_finding"](FID)
    print(f"initial: active={f['active']} is_mitigated={f['is_mitigated']} false_p={f['false_p']} risk_accepted={f['risk_accepted']}")

    # 1. note add + list + remove
    r = await TOOLS["add_finding_note"](FID, entry="int-test: nota temp", private=False)
    record("add_finding_note", r)
    lst = await TOOLS["list_finding_notes"](FID)
    record("list_finding_notes", {"count": lst["count"], "first": lst["notes"][0]["entry"] if lst["notes"] else None})
    my_note = next(n for n in lst["notes"] if n["entry"] == "int-test: nota temp")
    r = await TOOLS["remove_finding_note"](FID, note_id=my_note["id"])
    record("remove_finding_note", r)
    lst2 = await TOOLS["list_finding_notes"](FID)
    assert all(n["entry"] != "int-test: nota temp" for n in lst2["notes"]), "note not removed!"
    record("remove_finding_note verify", {"still_present": any(n['entry'] == 'int-test: nota temp' for n in lst2['notes'])})

    # 2. close as false positive WITH note
    r = await TOOLS["close_finding_false_positive"](FID, note="int-test: chiusura FP con nota")
    record("close_finding_false_positive", r)
    f = await TOOLS["get_finding"](FID)
    record("state after FP close", {"active": f["active"], "is_mitigated": f["is_mitigated"], "false_p": f["false_p"],
                                     "last_note": f["notes"][0]["entry"] if f["notes"] else None})

    # 3. reopen
    r = await TOOLS["reopen_finding"](FID, note="int-test: riapertura")
    record("reopen_finding", r)
    f = await TOOLS["get_finding"](FID)
    record("state after reopen", {"active": f["active"], "is_mitigated": f["is_mitigated"], "false_p": f["false_p"]})

    # 4. close as mitigated with note
    r = await TOOLS["close_finding_mitigated"](FID, note="int-test: mitigato")
    record("close_finding_mitigated", r)
    f = await TOOLS["get_finding"](FID)
    record("state after mitigated close", {"active": f["active"], "false_p": f["false_p"], "is_mitigated": f["is_mitigated"]})

    # 5. reopen again
    r = await TOOLS["reopen_finding"](FID)
    record("reopen_finding #2", r)
    f = await TOOLS["get_finding"](FID)
    record("state after reopen #2", {"active": f["active"], "is_mitigated": f["is_mitigated"]})

    # 6. accept_risk WITHOUT expiration -> must fail (validation)
    r = await TOOLS["accept_risk"](finding_ids=[FID], accepted_by="danilo.cianciulli@example.com",
                                   justification="int-test", expiration_date="2020-01-01")
    record("accept_risk past date (must fail)", r)
    assert "error" in r, "past date was accepted!"

    # 7. accept_risk WITH future expiration -> must succeed
    r = await TOOLS["accept_risk"](finding_ids=[FID], accepted_by="danilo.cianciulli@example.com",
                                   justification="int-test accettazione con scadenza",
                                   expiration_date="2026-12-31", decision="A")
    record("accept_risk valid", r)
    ra_id = r.get("risk_acceptance_id")
    f = await TOOLS["get_finding"](FID)
    record("state after accept", {"active": f["active"], "risk_accepted": f["risk_accepted"]})
    assert f["risk_accepted"] is True, "finding not risk-accepted!"

    # 8. expire the risk acceptance early, verify finding reactivated
    r = await TOOLS["expire_risk_acceptance"](ra_id, reason="int-test expire")
    record("expire_risk_acceptance", r)
    f = await TOOLS["get_finding"](FID)
    record("state after expire", {"active": f["active"], "risk_accepted": f["risk_accepted"]})

    # 9. cleanup: delete risk acceptance + remove my notes
    r = await TOOLS["delete_risk_acceptance"](ra_id)
    record("delete_risk_acceptance", r)
    lst3 = await TOOLS["list_finding_notes"](FID)
    for n in lst3["notes"]:
        if n["entry"].startswith("int-test:"):
            await TOOLS["remove_finding_note"](FID, note_id=n["id"])
    lst4 = await TOOLS["list_finding_notes"](FID)
    record("cleanup notes", {"remaining_int_test": sum(1 for n in lst4["notes"] if n["entry"].startswith("int-test:"))})

    # 10. new list_findings filters
    r = await TOOLS["list_findings"](product_name="Test Asset", limit=5)
    record("list_findings product_name", {"count": r.get("count")})
    r = await TOOLS["list_findings"](product_id=105, active=False, false_positive=False, limit=5)
    record("list_findings product_id+active", {"count": r.get("count")})

    # 11. close_finding validation
    r = await TOOLS["close_finding"](FID, closure_type="bogus")
    record("close_finding bad type (must fail)", r)
    assert "error" in r

    print("\nALL INTEGRATION CHECKS COMPLETED")

asyncio.run(main())
