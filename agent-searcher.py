from pydantic import BaseModel
from pydantic_ai import Agent, RunContext
from agent_registry import registry

from agents.shared import get_model

class AgentOutput(BaseModel):
    agent_url: str

agent = Agent(
    get_model(),
    system_prompt="""Your job is to search through a list of agent cards, 
    which will have descriptions and URLs of agents, and determine which agent to use for a given query.""",
    output_type=AgentOutput
)


@agent.tool
async def search(ctx: RunContext, query: str) -> str:
    """
    Searches through an agent registry of A2A agent cards and determines which agent to use for the query.
    """
    agent_cards = []
    for agent_card in registry:
        card_url = f'http://localhost:{agent_card["PORT"]}/.well-known/agent.json'
        agent_cards.append(card_url)
