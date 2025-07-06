from typing import Any
from pydantic import BaseModel
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIModel
from agent_registry import registry
import httpx

from agents.shared import get_model

class AgentOutput(BaseModel):
    agent_url: str

agent_searcher = Agent(
    get_model(),
    system_prompt="""Your job is to search through a list of agent cards, 
    which will have descriptions and URLs of agents, and determine which agent to use for a given query.
    Use the get_agent_cards tool to get a list of agent cards. You should ONLY return the URL of the chosen agent.""",
    output_type=AgentOutput
)


@agent_searcher.tool_plain
async def get_agent_cards() -> list(str):
    """
    Searches through an agent registry of A2A agent cards and determines which agent to use for the query.
    """
    agent_card_urls = []
    for agent_card in registry:
        card_url = f'http://localhost:{agent_card["PORT"]}/.well-known/agent.json'
        agent_card_urls.append(card_url)

    agent_cards = []
    async with httpx.AsyncClient() as client:
        for url in agent_card_urls:
            res = await client.get(url)
            if res.status_code == 200:
                agent_card = res.json()
                agent_cards.append(agent_card)
            else:
                print(f"Failed to fetch agent card from {url}")
    
    print(agent_cards)
    return agent_cards


