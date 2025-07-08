import os
from dotenv import load_dotenv
from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerStdio
from .shared import get_model

load_dotenv()

filesystem_server = MCPServerStdio(
    'npx', ['-y', '@modelcontextprotocol/server-filesystem', os.getenv("LOCAL_FILE_DIR", ".")]
)

filesystem_agent = Agent(
    get_model(),
    system_prompt="You are a filesystem specialist. Help users manage their files and directories.",
    mcp_servers=[filesystem_server]
)

# temp to save desc
# async def use_filesystem_agent(query: str) -> SubAgentResponse: # Use the new model
#     """
#     Interact with the file system through the filesystem subagent.
#     Use this tool when the user needs to read, write, list, or modify files.
#
#     Args:
#         query: The instruction for the filesystem agent.
#
#     Returns:
#         The response from the filesystem agent.
#     """
#     print(f"Calling Filesystem agent with query: {query}")
#     result = await filesystem_agent.run(query)
#     return SubAgentResponse(result=str(result.data) if result.data else "No result from Filesystem agent.") # Instantiate the model
