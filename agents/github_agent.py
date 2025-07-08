import os
from dotenv import load_dotenv
from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerStdio
from .shared import get_model

load_dotenv()

github_server = None
if os.getenv("GITHUB_TOKEN"):
    github_server = MCPServerStdio(
        'npx', ['-y', '@modelcontextprotocol/server-github'],
        env={"GITHUB_PERSONAL_ACCESS_TOKEN": os.getenv("GITHUB_TOKEN")}
    )

github_agent = Agent(
    get_model(),
    system_prompt="You are a GitHub specialist. Help users interact with GitHub repositories and features.",
    mcp_servers=[github_server] if github_server else []
)

# # temp to save desc
# async def use_github_agent(query: str) -> SubAgentResponse: # Use the new model
#     """
#     Interact with GitHub through the GitHub subagent.
#     Use this tool when the user needs to access repositories, issues, PRs, or other GitHub resources.
#
#     Args:
#         query: The instruction for the GitHub agent.
#
#     Returns:
#         The response from the GitHub agent.
#     """
#     print(f"Calling GitHub agent with query: {query}")
#     result = await github_agent.run(query)
#     return SubAgentResponse(result=str(result.data) if result.data else "No result from GitHub agent.") # Instantiate the model
