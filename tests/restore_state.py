"""Restore finding 20323 to its pre-test state: closed as false positive."""
import asyncio
import os

os.environ.setdefault("DEFECTDOJO_URL", "https://your-defectdojo.example.com")

from defectdojo_mcp.server import create_server

mcp = create_server()
TOOLS = {t.name: t.fn for t in mcp._tool_manager._tools.values()}
FID = 20323


async def main():
    # remove residual test notes (mine only: danilo's notes from today)
    lst = await TOOLS["list_finding_notes"](FID)
    removed = []
    for n in lst["notes"]:
        if n["author"]["username"] == "danilo.cianciulli@example.com":
            await TOOLS["remove_finding_note"](FID, note_id=n["id"])
            removed.append(n["entry"])
    print("removed notes:", removed)

    # restore: closed as false positive (state before today's tests)
    r = await TOOLS["close_finding_false_positive"](FID)
    print("restore close:", r)
    f = await TOOLS["get_finding"](FID)
    print(f"final state: active={f['active']} is_mitigated={f['is_mitigated']} false_p={f['false_p']} "
          f"risk_accepted={f['risk_accepted']} notes_by_me={sum(1 for n in f['notes'] if n['author']['username']=='danilo.cianciulli@example.com')}")

asyncio.run(main())
