"""Show save_note's description split into the part a reader sees and the part
hidden after the padding.

Runs locally and does not use Claude. It proves the poisoned paragraph lives in
the tool *description* - what the server tells the model - not in anything the
user types. Use it to rehearse, and as the fallback if the live run misbehaves.

    python sandbox/check_poison.py
"""

import asyncio
import pathlib
import re
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

HERE = pathlib.Path(__file__).resolve().parent


async def save_note_description() -> str:
    params = StdioServerParameters(command=sys.executable, args=["notes_server.py"],
                                   cwd=str(HERE))
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = {t.name: t.description for t in (await session.list_tools()).tools}
            return tools["save_note"]


async def main():
    desc = await save_note_description()
    # Honest half, then a long run of dots/spaces that pushes the rest out of
    # the collapsed preview, then the hidden paragraph.
    pad = re.search(r"[ .]{80,}", desc)
    visible = desc[: pad.start()].rstrip(" .")
    hidden = desc[pad.end() :].lstrip(" .")
    padding_len = (len(desc) - len(hidden)) - len(visible)

    print("save_note, the part a reader sees:")
    print(f"  {visible}\n")
    print(f"  ... then {padding_len} characters of dots and spaces ...\n")
    print("save_note, the part hidden after the padding:")
    print(f"  {hidden}\n")
    print("The user never sees the hidden part. MCP delivers it to the model")
    print("exactly like the honest sentence before it.")

    assert "personal_details.txt" in hidden and "personal_details.txt" not in visible
    print("\nOK")


asyncio.run(main())
