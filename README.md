# MCP Knowledge Assistant

A read-only Model Context Protocol (MCP) server that lets an AI client search a
knowledge base and retrieve complete source documents. The project starts with a
small local prototype, then applies the same tool contract to semantic retrieval
from an OpenAI vector store.

## What this demonstrates

- MCP tool design with narrow `search` and `fetch` responsibilities
- Structured inputs and outputs using FastMCP and Pydantic
- Semantic retrieval over uploaded documents in an OpenAI vector store
- Document-level deduplication when vector search returns several matching chunks
- Streamable HTTP and `stdio` MCP transports
- End-to-end tool use through the OpenAI Responses API and a secure MCP tunnel
- Configuration through environment variables, with no credentials in source code
- Unit and protocol-level tests that do not make paid API calls

## Architecture

```text
OpenAI Responses API
        |
        | MCP tool calls through an outbound secure tunnel
        v
Local FastMCP server (Streamable HTTP)
        |
        | vector-store search and file retrieval
        v
OpenAI vector store -> uploaded documents
```

The repository also includes a fully local learning path:

```text
Local demo client -> FastMCP server (stdio) -> data/documents.json
```

Both servers expose the same public tool contract:

| Tool | Input | Purpose |
| --- | --- | --- |
| `search` | `query: string` | Return compact, relevant document references. |
| `fetch` | `id: string` | Retrieve one complete document selected from search. |

Keeping discovery separate from retrieval avoids sending full documents before
they are needed and gives the model stable document IDs to use in later calls.

## Project structure

```text
.
├── data/documents.json                   # Sample local knowledge base
├── sample_data/cats.pdf                  # Public-domain vector-store sample
├── src/mcp_knowledge_assistant/
│   ├── knowledge_base.py                 # Local keyword retrieval
│   ├── models.py                         # Shared response schemas
│   ├── server.py                         # Local stdio MCP server
│   └── vector_store_server.py            # OpenAI vector-store MCP server
├── tests/                                # Offline unit and MCP tests
├── demo_client.py                        # Local stdio demonstration
├── vector_store_demo_client.py           # Direct HTTP MCP demonstration
└── api_client.py                         # Responses API + secure tunnel demonstration
```

## Requirements

- Python 3.11 or newer
- An OpenAI API project with billing enabled for the vector-store path
- The included sample PDF, or your own document, uploaded to an OpenAI vector store
- The OpenAI tunnel client only for the secure-tunnel demonstration

The local JSON server and the complete test suite require no API key.

### Sample document attribution

The vector-store demonstration uses
[*Cats: Their Points and Characteristics*](https://cdn.openai.com/API/docs/cats.pdf)
by W. Gordon Stables, Project Gutenberg eBook #43429. The sample PDF is hosted
by OpenAI and was produced from the Project Gutenberg edition. See the PDF for
the Project Gutenberg licence and applicable reuse terms.

## Setup

Clone the repository, create a virtual environment, and install the project:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
```

For OpenAI-backed examples, copy the environment template:

```bash
cp .env.example .env.local
```

Then add your own values to `.env.local`:

```dotenv
OPENAI_API_KEY=your_project_api_key
VECTOR_STORE_ID=vs_your_vector_store_id
```

`.env.local`, PyCharm settings, virtual environments, and local tunnel profiles
are excluded from Git.

## 1. Run the local prototype

The first server uses `stdio`, so the MCP client launches it as a child process
and communicates over standard input and output:

```bash
python demo_client.py
```

The demo discovers both tools, searches the sample JSON knowledge base, and
fetches the selected document.

You can also start the server through its installed command:

```bash
mcp-knowledge-assistant
```

A silent, waiting process is normal for a `stdio` server that has no connected
client.

## 2. Run the vector-store server

Upload `sample_data/cats.pdf` to an OpenAI vector store, then set
`OPENAI_API_KEY` and `VECTOR_STORE_ID` in `.env.local`. You may substitute your
own document and query if preferred. Start the Streamable HTTP server:

```bash
mcp-vector-store-assistant
```

By default, its MCP endpoint is:

```text
http://127.0.0.1:8000/mcp
```

In a second terminal, test the endpoint directly:

```bash
python vector_store_demo_client.py
```

Vector search operates on chunks, so a long document may produce several
matches with the same file ID. The MCP `search` tool deliberately collapses
those matches into one document result. The `fetch` tool then retrieves and
combines that document's parsed content for the model.

## 3. Call it through the Responses API

Follow OpenAI's [secure MCP tunnels guide](https://developers.openai.com/api/docs/guides/secure-mcp-tunnels)
to create a tunnel, configure its ignored local profile to target
`http://127.0.0.1:8000/mcp`, and start the tunnel client. Add the resulting ID to
`.env.local`:

```dotenv
MCP_TUNNEL_ID=tunnel_your_tunnel_id
```

The tunnel client reads its own runtime credential from
`CONTROL_PLANE_API_KEY`. Keep that value local as well. With the vector server
and tunnel client both running, execute:

```bash
python api_client.py
```

The Responses API request declares only the read-only `search` and `fetch` MCP
tools. The model can search, fetch a selected source, and compose an answer from
the retrieved content.

## Tests

Run all tests with:

```bash
pytest
```

The tests cover local ranking and fetching, MCP tool discovery, vector-result
deduplication, content assembly, and input validation. OpenAI calls are mocked,
so the suite is repeatable and does not consume API credits.

## Design decisions and scope

- **Read-only first:** neither MCP tool changes files or external state.
- **Stable compatibility contract:** `search(query)` returns document references;
  `fetch(id)` returns complete content and metadata.
- **Document results, not chunk results:** chunks are retrieval evidence inside the
  vector store, while the MCP client receives stable file IDs.
- **MCP is an abstraction layer:** for a single OpenAI-hosted vector store, the
  Responses API's built-in File Search tool is simpler. MCP becomes useful when
  the same retrieval interface must serve multiple clients, hide backend details,
  or later add authorization and domain logic.
- **Verified integration boundary:** the local servers, direct MCP clients, and
  Responses API path through the secure tunnel were exercised during development.
  This repository does not claim a deployed public server or a published ChatGPT
  app.

## Security notes

- Never commit `.env.local`, API keys, tunnel runtime keys, or organization IDs.
- Use project-scoped credentials and grant only the permissions required.
- Keep the local MCP server bound behind the secure outbound tunnel rather than
  opening an inbound firewall port.
- Review tool permissions before adding any write or consequential action.

## References

- [OpenAI MCP guide](https://developers.openai.com/api/docs/mcp)
- [OpenAI File Search guide](https://developers.openai.com/api/docs/guides/tools-file-search)
- [OpenAI secure MCP tunnels guide](https://developers.openai.com/api/docs/guides/secure-mcp-tunnels)
- [FastMCP documentation](https://gofastmcp.com/)
