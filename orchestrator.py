from __future__ import annotations
import agent_registry
from dotenv import load_dotenv
from pydantic_ai import Agent, RunContext
from pydantic import BaseModel

from agents.shared import get_model
from agent_searcher import agent_searcher

load_dotenv()

async def search_and_find_agents():
    pass

async def use_agent():
    pass

class Deps(BaseModel):
    query: str

orchestrator = Agent(
    get_model(),
    system_prompt=(
        """
        You are a primary orchestration agent that can call upon specialized subagents 
        to perform various tasks. Each subagent is an expert in interacting with a specific third-party service. 
        Analyze the user request and delegate the work to the appropriate subagent.
        """
        ),
    deps_type=Deps,
    tools=[search_and_find_agents, use_agent]
)

class SubAgentResponse(BaseModel):
    result: str

@orchestrator.tool
async def run_agent_searcher(ctx: RunContext[Deps]) -> SubAgentResponse:
    return agent_searcher.run_sync(ctx.deps.query)

