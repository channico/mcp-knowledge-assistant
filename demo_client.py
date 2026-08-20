import asyncio
import json

from fastmcp import Client
from mcp_knowledge_assistant.server import mcp


async def main() -> None:
    async with Client(mcp) as client:
        tools = await client.list_tools()
        print("Available tools:", [tool.name for tool in tools])

        search_result = await client.call_tool(
            "search",
            {"query": "Why separate search from fetching full documents?"}
        )
        print("\nSearch result:")
        print(json.dumps(search_result.structured_content, indent=2))
        #
        document_id = search_result.structured_content["results"][0]["id"]

        fetch_result = await client.call_tool(
            "fetch",
            {"id": document_id}
        )

        print("\nFetched document:")
        print(json.dumps(fetch_result.structured_content, indent=2))


if __name__ == "__main__":
    asyncio.run(main())