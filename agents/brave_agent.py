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

## temp to save desc
async def use_brave_search_agent(query: str) -> SubAgentResponse: # Use the new model
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
    return SubAgentResponse(result=str(result.data) if result.data else "No result from Brave agent.") # Instantiate the model

