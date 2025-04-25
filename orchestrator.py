from __future__ import annotations
from typing import Dict
from dotenv import load_dotenv
from rich.markdown import Markdown # Keep for potential future debugging/logging
from rich.console import Console # Keep for potential future debugging/logging
from pydantic_ai import Agent

# Import subagents and model helper from the new module
from agents.subagents import (
    brave_agent,
    filesystem_agent,
    github_agent,
    # firecrawl_agent, # Commented out
    get_model
)

load_dotenv()

# ========== Create the primary orchestration agent ==========
primary_agent = Agent(
    get_model(),
    system_prompt="""You are a primary orchestration agent that can call upon specialized subagents 
    to perform various tasks. Each subagent is an expert in interacting with a specific third-party service.
    Analyze the user request and delegate the work to the appropriate subagent."""
)

# Register DatabaseAgent tools so the orchestrator can call them
from agents.subagents import register_database_agent_tools
register_database_agent_tools(primary_agent)

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

# @primary_agent.tool_plain # Commented out
# async def use_firecrawl_agent(query: str) -> dict[str, str]:
#     """
#     Crawl and analyze websites using the Firecrawl subagent.
#     Use this tool when the user needs to extract data from websites or perform web scraping.
#
#     Args:
#         query: The instruction for the Firecrawl agent.
#
#     Returns:
#         The response from the Firecrawl agent.
#     """
#     print(f"Calling Firecrawl agent with query: {query}")
#     result = await firecrawl_agent.run(query)
#     return {"result": str(result.data) if result.data else "No result from Firecrawl agent."}

# Note: MCP Server Management (start_mcp_servers, stop_mcp_servers, _mcp_stack)
# has been moved to agents/subagents.py
