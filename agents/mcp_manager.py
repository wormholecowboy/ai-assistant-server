from contextlib import AsyncExitStack
from .brave_agent import brave_agent, brave_server
from .filesystem_agent import filesystem_agent, filesystem_server
from .github_agent import github_agent, github_server

_mcp_stack = AsyncExitStack()

async def start_mcp_servers():
    """Starts all MCP servers required by the agents."""
    print("Starting MCP servers...")
    
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