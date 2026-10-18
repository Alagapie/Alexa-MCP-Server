"""Manual end-to-end test: connect to the running MCP server over Streamable HTTP."""
import asyncio
import json
import sys

from mcp.client.session import ClientSession
from mcp.client.streamable_http import streamable_http_client

URL = "http://127.0.0.1:8000/mcp"


async def main() -> None:
    async with streamable_http_client(URL) as streams:
        read, write = streams[0], streams[1]
        async with ClientSession(read, write) as session:
            init = await session.initialize()
            print("SERVER:", session._client_info if hasattr(session, "_client_info") else "")
            tools = await session.list_tools()
            names = [t.name for t in tools.tools]
            print("TOOLS:", json.dumps(names))

            res = await session.call_tool("get_home_snapshot", {})
            print("SNAPSHOT:", json.dumps(json.loads(res.content[0].text), indent=None)[:400])

            plan = await session.call_tool("run_routine", {"routine_name": "bedtime", "confirm": False})
            print("PLAN:", plan.content[0].text[:300])

            run = await session.call_tool("run_routine", {"routine_name": "bedtime", "confirm": True})
            print("RUN:", run.content[0].text[:300])

            scene = await session.call_tool("describe_scene", {"camera_id": "kitchen"})
            print("SCENE:", scene.content[0].text[:300])

            res2 = await session.list_resources()
            print("RESOURCES:", [str(r.uri) for r in res2.resources])


if __name__ == "__main__":
    asyncio.run(main())
