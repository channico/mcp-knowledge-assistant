import asyncio
import json
import sys
from pathlib import Path

from fastmcp import Client
from fastmcp.client.transports import StdioTransport


async def main() -> None:
    transport = StdioTransport(
        command=sys.executable,
        args=["-m", "mcp_knowledge_assistant.server"],
        cwd=str(Path(__file__).parent),
    )

    async with Client(transport) as client:
        tools = await client.list_tools()
        print("Available tools:", [tool.name for tool in tools])

        search_result = await client.call_tool(
            "search",
            {"query": "Why separate search from fetching full documents?"},
        )
        print("\nSearch result:")
        print(json.dumps(search_result.structured_content, indent=2))
        document_id = search_result.structured_content["results"][0]["id"]

        fetch_result = await client.call_tool("fetch", {"id": document_id})

        print("\nFetched document:")
        print(json.dumps(fetch_result.structured_content, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
