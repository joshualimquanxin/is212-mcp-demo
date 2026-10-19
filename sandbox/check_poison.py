"""Show save_note's description with POISON off and on, side by side.

Runs locally and does not use Claude. It proves the poisoned paragraph lives in
the tool *description* - what the server tells the model - not in anything the
user types. Use it to rehearse, and as the fallback if the live run misbehaves.

    python sandbox/check_poison.py
"""

import asyncio
import os
import pathlib
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

HERE = pathlib.Path(__file__).resolve().parent


async def save_note_description(poison: bool) -> str:
    env = os.environ.copy()
    env["POISON"] = "1" if poison else "0"
    params = StdioServerParameters(command=sys.executable, args=["notes_server.py"],
                                   cwd=str(HERE), env=env)
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = {t.name: t.description for t in (await session.list_tools()).tools}
            return tools["save_note"]


async def main():
    clean = await save_note_description(poison=False)
    poisoned = await save_note_description(poison=True)
    extra = poisoned[len(clean):].strip()

    print("save_note, POISON=0 (what the server author meant):")
    print(f"  {clean}\n")
    print("save_note, POISON=1 (the same tool, one paragraph appended):")
    print(f"  {clean}")
    print(f"  + {extra}\n")
    print("The user never sees either description. MCP delivers the appended")
    print("paragraph to the model exactly like the honest sentence before it.")

    assert poisoned.startswith(clean) and "secrets.txt" in extra and "secrets.txt" not in clean
    print("\nOK")


asyncio.run(main())
