"""Start circulation_server.py over stdio and exercise it, the way Claude Code does.

    python demo/check_server.py
"""

import asyncio
import json
import pathlib
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

ROOT = pathlib.Path(__file__).resolve().parent.parent


async def main():
    params = StdioServerParameters(command=sys.executable,
                                   args=["circulation_server.py"], cwd=str(ROOT))
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = [t.name for t in (await session.list_tools()).tools]
            resources = [str(r.uri) for r in (await session.list_resources()).resources]
            prompts = [p.name for p in (await session.list_prompts()).prompts]
            print(f"tools     : {tools}")
            print(f"resources : {resources}")
            print(f"prompts   : {prompts}")

            result = await session.call_tool("overdue_loans", {})
            data = result.structured_content
            if isinstance(data, dict) and "result" in data:
                loans = data["result"]            # SDK v2 wraps a list return as {"result": [...]}
            else:
                loans = [json.loads(b.text) for b in result.content if getattr(b, "text", None)]
            over_cap = [l for l in loans if l["fee_today"] > 20]
            print(f"overdue_loans: {len(loans)} loans, {len(over_cap)} above $20 "
                  f"(largest reduction ${max(l['fee_today'] for l in over_cap) - 20:.2f})")

            summary = await session.read_resource("circulation://summary")
            print(f"summary   : {summary.contents[0].text}")
            assert tools == ["overdue_loans"] and len(loans) == 12 and len(over_cap) == 3
            print("OK")


asyncio.run(main())
