from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI
from openai.types.responses.tool_param import Mcp

load_dotenv(Path(__file__).with_name(".env.local"))

client = OpenAI()
mcp_tool: Mcp = {
    "type": "mcp",
    "server_label": "knowledge",
    "tunnel_id": "tunnel_6a866de7e2ec81919d2914ff8243f960",
    "allowed_tools": ["search", "fetch"],
    "require_approval": "never",
}

response = client.responses.create(
    model="gpt-5.6-luna",
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
