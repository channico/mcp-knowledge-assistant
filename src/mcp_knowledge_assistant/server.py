from fastmcp import FastMCP

from .knowledge_base import fetch_document, search_documents
from .models import FetchOutput, SearchOutput


mcp = FastMCP(
    name="MCP Knowledge Assistant",
    instructions=(
        "Search the knowledge base before fetching a complete document. "
        "Use search result IDs with the fetch tool."
    ),
)


@mcp.tool(output_schema=SearchOutput.model_json_schema())
def search(query: str) -> SearchOutput:
    """Find documents relevant to a natural-language query."""
    return search_documents(query)


@mcp.tool(output_schema=FetchOutput.model_json_schema())
def fetch(id: str) -> FetchOutput:
    """Retrieve one complete document using an ID returned by search."""
    return fetch_document(id)


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()

