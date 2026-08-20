"""MCP search and fetch tools backed by an OpenAI vector store."""

import logging
import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from fastmcp import FastMCP
from openai import OpenAI

from .models import FetchOutput, SearchOutput, SearchResult

ENV_FILE = Path(__file__).resolve().parents[2] / ".env.local"
DEFAULT_PORT = 8000
MCP_PATH = "/mcp"

load_dotenv(ENV_FILE)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

mcp = FastMCP(
    name="MCP Knowledge Assistant",
    instructions=(
        "Search the vector store for relevant documents, then use the returned "
        "file ID with fetch to retrieve complete content for answers and citations."
    ),
)


def require_environment_variable(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Set {name} in {ENV_FILE.name} before running this server.")
    return value


@lru_cache(maxsize=1)
def get_openai_client() -> OpenAI:
    return OpenAI()


def search_vector_store(
    query: str, client: OpenAI, vector_store_id: str
) -> SearchOutput:
    """Map relevant vector-store chunks to unique document search results."""
    if not query.strip():
        return SearchOutput(results=[])

    logger.info("Searching vector store %s", vector_store_id)
    response = client.vector_stores.search(
        vector_store_id=vector_store_id,
        query=query,
    )

    results_by_id: dict[str, SearchResult] = {}
    for item in response.data:
        if item.file_id and item.file_id not in results_by_id:
            results_by_id[item.file_id] = SearchResult(
                id=item.file_id,
                title=item.filename,
                url=f"https://platform.openai.com/storage/files/{item.file_id}",
            )

    results = [*results_by_id.values()]
    logger.info("Vector store search returned %d unique documents", len(results))
    return SearchOutput(results=results)


def fetch_vector_store_document(
    document_id: str, client: OpenAI, vector_store_id: str
) -> FetchOutput:
    """Retrieve a document's parsed text and metadata from a vector store."""
    if not document_id:
        raise ValueError("Document ID is required")

    logger.info("Fetching vector-store file %s", document_id)
    content_response = client.vector_stores.files.content(
        vector_store_id=vector_store_id,
        file_id=document_id,
    )
    vector_store_file = client.vector_stores.files.retrieve(
        vector_store_id=vector_store_id,
        file_id=document_id,
    )
    file_object = client.files.retrieve(document_id)

    content_parts = [item.text for item in content_response.data if item.text]
    file_content = "\n".join(content_parts) or "No content available"
    attributes = getattr(vector_store_file, "attributes", None)

    return FetchOutput(
        id=document_id,
        title=file_object.filename,
        text=file_content,
        url=f"https://platform.openai.com/storage/files/{document_id}",
        metadata=dict(attributes) if attributes else None,
    )


@mcp.tool(output_schema=SearchOutput.model_json_schema())
def search(query: str) -> SearchOutput:
    """Find documents relevant to a natural-language query."""
    return search_vector_store(
        query,
        get_openai_client(),
        require_environment_variable("VECTOR_STORE_ID"),
    )


@mcp.tool(output_schema=FetchOutput.model_json_schema())
def fetch(id: str) -> FetchOutput:
    """Retrieve one complete document using an ID returned by search."""
    # The MCP compatibility schema requires the public argument to be named `id`.
    return fetch_vector_store_document(
        id,
        get_openai_client(),
        require_environment_variable("VECTOR_STORE_ID"),
    )


def main() -> None:
    vector_store_id = require_environment_variable("VECTOR_STORE_ID")
    port = int(os.getenv("MCP_SERVER_PORT", str(DEFAULT_PORT)))

    logger.info("Using vector store: %s", vector_store_id)
    logger.info("Starting MCP server at http://0.0.0.0:%d%s", port, MCP_PATH)

    try:
        mcp.run(
            transport="http",
            host="0.0.0.0",
            port=port,
            path=MCP_PATH,
            uvicorn_config={"loop": "asyncio"},
        )
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception:
        logger.exception("Server error")
        raise


if __name__ == "__main__":
    main()
