import asyncio

from fastmcp import Client

from mcp_knowledge_assistant.server import mcp


def test_mcp_client_can_discover_and_call_tools() -> None:
    async def exercise_server() -> None:
        async with Client(mcp) as client:
            tools = await client.list_tools()
            assert {tool.name for tool in tools} == {"search", "fetch"}

            result = await client.call_tool("search", {"query": "MCP protocol"})
            assert result.structured_content is not None
            assert result.structured_content["results"][0]["id"] == "mcp-basics"

    asyncio.run(exercise_server())
