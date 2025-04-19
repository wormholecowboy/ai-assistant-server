from __future__ import annotations
from contextlib import AsyncExitStack
import os
from dotenv import load_dotenv

from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.mcp import MCPServerStdio
from pydantic_ai import Agent

load_dotenv()

# ========== Helper function to get model configuration ==========
def get_model():
    llm = os.getenv('MODEL_CHOICE', 'gpt-4o-mini')
    base_url = os.getenv('BASE_URL', 'https://api.openai.com/v1')
    api_key = os.getenv('LLM_API_KEY', 'no-api-key-provided')

    return OpenAIModel(llm, provider=OpenAIProvider(base_url=base_url, api_key=api_key))

# ========== Set up MCP servers for each service ==========

# Brave Search MCP server
brave_server = MCPServerStdio(
    'npx', ['-y', '@modelcontextprotocol/server-brave-search'],
    env={"BRAVE_API_KEY": os.getenv("BRAVE_API_KEY")}
)

# Filesystem MCP server
filesystem_server = MCPServerStdio(
    'npx', ['-y', '@modelcontextprotocol/server-filesystem', os.getenv("LOCAL_FILE_DIR", ".")] # Added default dir
)

# GitHub MCP server
github_server = MCPServerStdio(
    'npx', ['-y', '@modelcontextprotocol/server-github'],
    env={"GITHUB_PERSONAL_ACCESS_TOKEN": os.getenv("GITHUB_TOKEN")}
)

# Firecrawl MCP server
firecrawl_server = MCPServerStdio(
    'npx', ['-y', 'firecrawl-mcp'],
    env={"FIRECRAWL_API_KEY": os.getenv("FIRECRAWL_API_KEY")}
)

# ========== Create subagents with their MCP servers ==========

# Brave search agent
brave_agent = Agent(
    get_model(),
    system_prompt="You are a web search specialist using Brave Search. Find relevant information on the web.",
    mcp_servers=[brave_server]
)

# Filesystem agent
filesystem_agent = Agent(
    get_model(),
    system_prompt="You are a filesystem specialist. Help users manage their files and directories.",
    mcp_servers=[filesystem_server]
)

# GitHub agent
github_agent = Agent(
    get_model(),
    system_prompt="You are a GitHub specialist. Help users interact with GitHub repositories and features.",
    mcp_servers=[github_server]
)

# Firecrawl agent
firecrawl_agent = Agent(
    get_model(),
    system_prompt="You are a web crawling specialist. Help users extract data from websites.",
    mcp_servers=[firecrawl_server]
)

# ========== MCP Server Management ==========
# Store the stack globally to manage it across lifespan events
_mcp_stack = AsyncExitStack()

async def start_mcp_servers():
    """Starts all MCP servers required by the agents."""
    print("Starting MCP servers...")
    # Enter the context for each agent's servers
    await _mcp_stack.enter_async_context(brave_agent.run_mcp_servers())
    await _mcp_stack.enter_async_context(filesystem_agent.run_mcp_servers())
    await _mcp_stack.enter_async_context(github_agent.run_mcp_servers())
    await _mcp_stack.enter_async_context(firecrawl_agent.run_mcp_servers())
    print("All MCP servers started successfully!")

async def stop_mcp_servers():
    """Stops all MCP servers."""
    print("Stopping MCP servers...")
    await _mcp_stack.aclose()
    print("All MCP servers stopped.")
