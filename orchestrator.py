from __future__ import annotations
from contextlib import AsyncExitStack
from typing import Any, Dict, List
from dataclasses import dataclass
from dotenv import load_dotenv
from rich.markdown import Markdown # Keep for potential future debugging/logging
from rich.console import Console # Keep for potential future debugging/logging
import os

from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.mcp import MCPServerStdio
from pydantic_ai import Agent, RunContext

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

# ========== Create the primary orchestration agent ==========
primary_agent = Agent(
    get_model(),
    system_prompt="""You are a primary orchestration agent that can call upon specialized subagents 
    to perform various tasks. Each subagent is an expert in interacting with a specific third-party service.
    Analyze the user request and delegate the work to the appropriate subagent."""
)

# ========== Define tools for the primary agent to call subagents ==========

@primary_agent.tool_plain
async def use_brave_search_agent(query: str) -> dict[str, str]:
    """
    Search the web using Brave Search through the Brave subagent.
    Use this tool when the user needs to find information on the internet or research a topic.

    Args:
        query: The search query or instruction for the Brave search agent.

    Returns:
        The search results or response from the Brave agent.
    """
    print(f"Calling Brave agent with query: {query}")
    result = await brave_agent.run(query)
    # Ensure result.data is serializable (string or dict usually)
    return {"result": str(result.data) if result.data else "No result from Brave agent."}

@primary_agent.tool_plain
async def use_filesystem_agent(query: str) -> dict[str, str]:
    """
    Interact with the file system through the filesystem subagent.
    Use this tool when the user needs to read, write, list, or modify files.

    Args:
        query: The instruction for the filesystem agent.

    Returns:
        The response from the filesystem agent.
    """
    print(f"Calling Filesystem agent with query: {query}")
    result = await filesystem_agent.run(query)
    return {"result": str(result.data) if result.data else "No result from Filesystem agent."}

@primary_agent.tool_plain
async def use_github_agent(query: str) -> dict[str, str]:
    """
    Interact with GitHub through the GitHub subagent.
    Use this tool when the user needs to access repositories, issues, PRs, or other GitHub resources.

    Args:
        query: The instruction for the GitHub agent.

    Returns:
        The response from the GitHub agent.
    """
    print(f"Calling GitHub agent with query: {query}")
    result = await github_agent.run(query)
    return {"result": str(result.data) if result.data else "No result from GitHub agent."}

@primary_agent.tool_plain
async def use_firecrawl_agent(query: str) -> dict[str, str]:
    """
    Crawl and analyze websites using the Firecrawl subagent.
    Use this tool when the user needs to extract data from websites or perform web scraping.

    Args:
        query: The instruction for the Firecrawl agent.

    Returns:
        The response from the Firecrawl agent.
    """
    print(f"Calling Firecrawl agent with query: {query}")
    result = await firecrawl_agent.run(query)
    return {"result": str(result.data) if result.data else "No result from Firecrawl agent."}

# ========== MCP Server Management ==========
# Store the stack globally to manage it across lifespan events
_mcp_stack = AsyncExitStack()

async def start_mcp_servers():
    """Starts all MCP servers required by the agents."""
    print("Starting MCP servers...")
    # Enter the context for each agent's servers
    # Note: If multiple agents share the same server instance,
    # entering the context multiple times might be redundant or cause issues
    # depending on the implementation of run_mcp_servers.
    # Assuming here each agent manages its own server list correctly.
    # We only need to call run_mcp_servers for each *unique* set of servers.
    # In this case, each agent has its own list, so we call it for each agent.
    await _mcp_stack.enter_async_context(brave_agent.run_mcp_servers())
    await _mcp_stack.enter_async_context(filesystem_agent.run_mcp_servers())
    await _mcp_stack.enter_async_context(github_agent.run_mcp_servers())
    await _mcp_stack.enter_async_context(firecrawl_agent.run_mcp_servers())
    # We don't need to run servers for the primary_agent as it doesn't directly use MCP servers itself
    print("All MCP servers started successfully!")

async def stop_mcp_servers():
    """Stops all MCP servers."""
    print("Stopping MCP servers...")
    await _mcp_stack.aclose()
    print("All MCP servers stopped.")
