from __future__ import annotations

from dotenv import load_dotenv
from pydantic import BaseModel
from pydantic_ai import Agent, RunContext

import agent_registry
from agent_searcher import agent_searcher
from agents.shared import get_model

# from agent_runner import agent_runner

load_dotenv()

# system_prompt = """
#         You are a primary orchestration agent that can call upon specialized subagents 
#         to perform various tasks. Each subagent is an expert in interacting with a specific third-party service. 
#         Analyze the user request and delegate the work to the appropriate subagent.
#         """

system_prompt = """
    Find the correct sub agent to use and return its URL.
    """

orchestrator = Agent(
    get_model(),
    system_prompt=system_prompt,
    deps_type=str
)

class SubAgentResponse(BaseModel):
    result: str

@orchestrator.tool
async def search_through_agents(ctx: RunContext[str]) -> SubAgentResponse:
    result = await agent_searcher.run(ctx.deps)
    return SubAgentResponse(result=str(result))
#
# @orchestrator.tool
# async def run_agent_runner(ctx: RunContext[Deps]) -> SubAgentResponse:
#     result = agent_runner.run_sync()
#     return SubAgentResponse(result=str(result))
