from __future__ import annotations
from contextlib import AsyncExitStack
import os
from dotenv import load_dotenv

from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.mcp import MCPServerStdio
from typing import Dict, Any, Optional
from pydantic_ai import Agent
from database_agent.response_models import DatabaseAgentResponse

load_dotenv()

# ========== Helper function to get model configuration ==========
def get_model():
    model_name = 'gemini-2.5-flash-preview-04-17'
    base_url = os.getenv('BASE_URL', 'https://generativelanguage.googleapis.com/v1beta/openai')
    api_key = os.getenv('GEMINI_API_KEY', 'no-api-key-provided')
    model = OpenAIModel(model_name, provider=OpenAIProvider(base_url=base_url, api_key=api_key))
    return model

# ========== Set up MCP servers for each service ==========

# Only create MCP servers if the required environment variables are present
brave_server = None
if os.getenv("BRAVE_API_KEY"):
    brave_server = MCPServerStdio(
        'npx', ['-y', '@modelcontextprotocol/server-brave-search'],
        env={"BRAVE_API_KEY": os.getenv("BRAVE_API_KEY")}
    )

filesystem_server = MCPServerStdio(
    'npx', ['-y', '@modelcontextprotocol/server-filesystem', os.getenv("LOCAL_FILE_DIR", ".")]
)

github_server = None
if os.getenv("GITHUB_TOKEN"):
    github_server = MCPServerStdio(
        'npx', ['-y', '@modelcontextprotocol/server-github'],
        env={"GITHUB_PERSONAL_ACCESS_TOKEN": os.getenv("GITHUB_TOKEN")}
    )

# Create agents with or without MCP servers based on availability
brave_agent = Agent(
    get_model(),
    system_prompt="You are a web search specialist using Brave Search. Find relevant information on the web.",
    mcp_servers=[brave_server] if brave_server else []
)

filesystem_agent = Agent(
    get_model(),
    system_prompt="You are a filesystem specialist. Help users manage their files and directories.",
    mcp_servers=[filesystem_server]
)

github_agent = Agent(
    get_model(),
    system_prompt="You are a GitHub specialist. Help users interact with GitHub repositories and features.",
    mcp_servers=[github_server] if github_server else []
)

# ========== MCP Server Management ==========
# Store the stack globally to manage it across lifespan events
_mcp_stack = AsyncExitStack()

async def start_mcp_servers():
    """Starts all MCP servers required by the agents."""
    print("Starting MCP servers...")
    
    # Start servers only for agents that have MCP servers configured
    try:
        if brave_server:
            print("Starting Brave search server...")
            await _mcp_stack.enter_async_context(brave_agent.run_mcp_servers())
        else:
            print("Skipping Brave search server (no API key)")
            
        print("Starting filesystem server...")
        await _mcp_stack.enter_async_context(filesystem_agent.run_mcp_servers())
        
        if github_server:
            print("Starting GitHub server...")
            await _mcp_stack.enter_async_context(github_agent.run_mcp_servers())
        else:
            print("Skipping GitHub server (no token)")
            
        print("All available MCP servers started successfully!")
    except Exception as e:
        print(f"Error starting MCP servers: {e}")
        print("Continuing without MCP servers...")

async def stop_mcp_servers():
    """Stops all MCP servers."""
    print("Stopping MCP servers...")
    await _mcp_stack.aclose()
    print("All MCP servers stopped.")
