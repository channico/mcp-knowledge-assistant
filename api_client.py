import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI
from openai.types.responses.tool_param import Mcp

ENV_FILE = Path(__file__).with_name(".env.local")


def require_environment_variable(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Set {name} in {ENV_FILE.name} before running this client.")
    return value


def main() -> None:
    load_dotenv(ENV_FILE)

    mcp_tool: Mcp = {
        "type": "mcp",
        "server_label": "knowledge",
        "tunnel_id": require_environment_variable("MCP_TUNNEL_ID"),
        "allowed_tools": ["search", "fetch"],
        "require_approval": "never",
    }

    response = OpenAI().responses.create(
        model=os.getenv("OPENAI_MODEL", "gpt-5.6-luna"),
        input=(
            "Use the MCP knowledge source to explain whether cats become "
            "attached to their homes. Cite the source."
        ),
        tools=[mcp_tool],
    )

    print("Response items:")
    for item in response.output:
        print("-", item.type)

    print("\nAnswer:")
    print(response.output_text)


if __name__ == "__main__":
    main()
