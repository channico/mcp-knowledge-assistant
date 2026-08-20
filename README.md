# MCP Knowledge Assistant

A small, read-only Model Context Protocol (MCP) server built with Python and
FastMCP. It follows OpenAI's MCP compatibility pattern by exposing two tools:

- `search(query)` finds matching documents.
- `fetch(id)` retrieves one complete document.

The first version uses local JSON data, so it needs no API key and makes no
paid API calls. A later version will replace the local search implementation
with OpenAI vector store search.

## Open in PyCharm

1. Choose **Open** on the PyCharm welcome screen.
2. Select this `mcp-knowledge-assistant` folder.
3. Let PyCharm create a virtual environment using Python 3.11 or newer.
4. Open PyCharm's terminal and install the project:

   ```bash
   python -m pip install -e ".[dev]"
   ```

## Run the server

```bash
python -m mcp_knowledge_assistant.server
```

The default transport is `stdio`: an MCP client launches the process and
exchanges protocol messages through standard input and output. The process
appearing to wait silently is normal.

## Run the tests

```bash
pytest
```

## Why the response models matter

The typed `SearchOutput` and `FetchOutput` models give MCP clients a declared
output schema. Search results include a stable ID, readable title, and
canonical URL. Fetch results add the full document text and optional metadata.

