from __future__ import annotations
from dotenv import load_dotenv
from pydantic_ai import Agent
from pydantic import BaseModel, ConfigDict # Added import

from agents.shared import get_model

load_dotenv()

## wrap searcher and executor agents in funcs for tool use

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

