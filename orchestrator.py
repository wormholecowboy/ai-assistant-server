from __future__ import annotations
import agent_registry
from dotenv import load_dotenv
from pydantic_ai import Agent
from pydantic import BaseModel

from agents.shared import get_model
from agent_searcher import agent_searcher

load_dotenv()

async def search_and_find_agents():
    pass

async def use_agent():
    pass

# Orchestrator is now a PydanticAI Agent
orchestrator = Agent(
    get_model(),
    system_prompt="""You are a primary orchestration agent that can call upon specialized subagents 
    to perform various tasks. Each subagent is an expert in interacting with a specific third-party service.
    Analyze the user request and delegate the work to the appropriate subagent."""
)

# Define strict response models for non-database tools
class SubAgentResponse(BaseModel):
    result: str

@orchestrator.tool
     async def run_agent_searcher(ctx: RunContext, query: str) -> SubAgentResponse:
         return await agent_searcher.run_sync(query)


