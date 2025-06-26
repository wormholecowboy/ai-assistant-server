import os
from dotenv import load_dotenv
from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerStdio
from .shared import get_model

load_dotenv()

brave_server = None
if os.getenv("BRAVE_API_KEY"):
    brave_server = MCPServerStdio(
        'npx', ['-y', '@modelcontextprotocol/server-brave-search'],
        env={"BRAVE_API_KEY": os.getenv("BRAVE_API_KEY")}
    )

brave_agent = Agent(
    get_model(),
    system_prompt="You are a web search specialist using Brave Search. Find relevant information on the web.",
    mcp_servers=[brave_server] if brave_server else []
)