import asyncio

from fastmcp import Client

async def main() -> None:
    async with Client("http://127.0.0.1:8000/sse") as client:
        tools = await client.list_tools()
        print("Available tools:", [tool.name for tool in tools])

        result = await client.call_tool(
            "search",
            {"query": "What does this book say about caring for cats?"}
        )
        print("\nSearch result:")
        print(result.data)

if __name__ == "__main__":
    asyncio.run(main())