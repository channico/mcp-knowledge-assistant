import asyncio
import os
from pathlib import Path

from dotenv import load_dotenv
from fastmcp import Client


async def main() -> None:
    load_dotenv(Path(__file__).with_name(".env.local"))
    server_url = os.getenv("MCP_SERVER_URL", "http://127.0.0.1:8000/mcp")

    async with Client(server_url) as client:
        tools = await client.list_tools()
        print("Available tools:", [tool.name for tool in tools])

        search_result = await client.call_tool(
            "search",
            {"query": "What does this book say about caring for cats?"},
        )
        print("\nSearch result:")
        print(search_result.data)

        search_content = search_result.structured_content or {}
        results = search_content.get("results", [])
        if not results:
            print("No documents matched the query.")
            return

        fetch_result = await client.call_tool("fetch", {"id": results[0]["id"]})
        document = fetch_result.structured_content or {}
        preview = str(document.get("text", ""))[:500]
        print(f"\nFetched document: {document.get('title', results[0]['id'])}")
        print(f"{preview}...")


if __name__ == "__main__":
    asyncio.run(main())
