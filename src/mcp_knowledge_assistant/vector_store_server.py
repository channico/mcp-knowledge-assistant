import logging
import os
from pathlib import Path

from dotenv import load_dotenv
from fastmcp import FastMCP
from openai import OpenAI

from .models import FetchOutput, SearchOutput, SearchResult

load_dotenv(Path(__file__).resolve().parents[2] / ".env.local")

# OpenAI configuration
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
VECTOR_STORE_ID = os.environ["VECTOR_STORE_ID"]

"""
Sample MCP Server for ChatGPT Integration

This server implements the Model Context Protocol (MCP) with search and fetch
capabilities designed to work with ChatGPT's chat and deep research features.
"""

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize OpenAI client
openai_client = OpenAI(api_key=OPENAI_API_KEY)

server_instructions = """
This MCP server provides search and document retrieval capabilities
for ChatGPT Apps and deep research. Use the search tool to find relevant documents
based on keywords, then use the fetch tool to retrieve complete
document content with citations.
"""

mcp = FastMCP(name="MCP Knowledge Assistant",
                 instructions=server_instructions)

@mcp.tool(output_schema=SearchOutput.model_json_schema())
def search(query: str) -> SearchOutput:
    """
    Search for documents using OpenAI Vector Store search.

    This tool searches through the vector store to find semantically relevant matches.
    Returns a list of search results with basic information. Use the fetch tool to get
    complete document content.

    Args:
        query: Search query string. Natural language queries work best for semantic search.

    Returns:
        Dictionary with 'results' key containing list of matching documents.
        Each result includes id, title, and URL.
    """
    if not query or not query.strip():
        return SearchOutput(results=[])

    # Search the vector store using OpenAI API
    logger.info(f"Searching {VECTOR_STORE_ID} for query: '{query}'")

    response = openai_client.vector_stores.search(
        vector_store_id=VECTOR_STORE_ID, query=query
    )


    results_by_id: dict[str, SearchResult] = {}

    # Process the vector store search results
    for item in response.data:
        if item.file_id not in results_by_id:
            results_by_id[item.file_id] = SearchResult(
                id=item.file_id,
                title=item.filename,
                url=f"https://platform.openai.com/storage/files/{item.file_id}",
            )

    results = list(results_by_id.values())

    logger.info(f"Vector store search returned {len(results)} results")
    return SearchOutput(results=results)

@mcp.tool(output_schema=FetchOutput.model_json_schema())
def fetch(id: str) -> FetchOutput:
    """
    Retrieve complete document content by ID for detailed
    analysis and citation. This tool fetches the full document
    content from OpenAI Vector Store. Use this after finding
    relevant documents with the search tool to get complete
    information for analysis and proper citation.

    Args:
        id: File ID from vector store (file-xxx) or local document ID

    Returns:
        Complete document with id, title, full text content,
        optional URL, and metadata

    Raises:
        ValueError: If the specified ID is not found
    """
    if not id:
        raise ValueError("Document ID is required")

    logger.info(f"Fetching content from vector store for file ID: {id}")

    # Fetch file content from vector store
    content_response = openai_client.vector_stores.files.content(
        vector_store_id=VECTOR_STORE_ID, file_id=id
    )

    # Get file metadata
    file_info = openai_client.vector_stores.files.retrieve(
        vector_store_id=VECTOR_STORE_ID, file_id=id
    )

    content_parts: list[str] = []

    for content_item in content_response.data:
        if content_item.text:
            content_parts.append(content_item.text)

    file_content = "\n".join(content_parts) or "No content available"

    # Use filename as title and create proper URL for citations
    filename = getattr(file_info, "filename", f"Document {id}")

    result = FetchOutput(
        id=id,
        title=filename,
        text=file_content,
        url=f"https://platform.openai.com/storage/files/{id}",
    )

    # Add metadata if available from file info
    if hasattr(file_info, "attributes") and file_info.attributes:
        result.metadata = dict(file_info.attributes)

    logger.info(f"Fetched vector store file: {id}")
    return result


def main():
    """Main function to start the MCP server."""
    logger.info(f"Using vector store: {VECTOR_STORE_ID}")

    # Configure and start the server
    logger.info("Starting MCP server on 0.0.0.0:8000")
    logger.info("Server will be accessible via SSE transport")

    try:
        # Use FastMCP's built-in run method with SSE transport
        port = int(os.environ.get("OPENAI_EXAMPLE_PORT", "8000"))
        mcp.run(
            transport="sse",
            host="0.0.0.0",
            port=port,
            uvicorn_config={"loop": "asyncio"},
        )
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception:
        logger.exception("Server error")
        raise


if __name__ == "__main__":
    main()
