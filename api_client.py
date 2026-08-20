from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(Path(__file__).with_name(".env.local"))

client = OpenAI()

response = client.responses.create(
    model="gpt-5.6-luna",
    input="Explain what an MCP server does in two concise sentences.",
)

print(response.output_text)