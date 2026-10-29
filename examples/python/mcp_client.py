"""Connect to Cedric with the official MCP Python SDK (2.x), list his tools, and call one.

    pip install -r requirements.txt
    CEDRIC_KEY=cedric_sk_... python mcp_client.py
"""

import asyncio
import os

from mcp import ClientSession
from mcp.client.streamable_http import create_mcp_http_client, streamable_http_client

URL = "https://app.meet-cedric.com/api/v1/mcp"


async def main():
    http = create_mcp_http_client(headers={"Authorization": f"Bearer {os.environ['CEDRIC_KEY']}"})
    async with http, streamable_http_client(URL, http_client=http) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools = (await session.list_tools()).tools
            print(f"{len(tools)} tools, for example:", [t.name for t in tools[:5]])

            # Search the team's memory.
            result = await session.call_tool("recall_memories", {"query": "pricing decisions"})
            print("\n".join(c.text for c in result.content if c.type == "text"))


asyncio.run(main())
