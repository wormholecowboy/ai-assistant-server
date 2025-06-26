"""
Category classification using LLM via PydanticAI.
"""
from typing import List, Dict
from pydantic_ai import Agent
from ..shared import get_model

agent = Agent(get_model())

def classify_category(data: Dict, existing_categories: List[str]) -> str:
    prompt = f"""Given the following data: {data}, and these categories: {existing_categories}, suggest the best category or a new concise one."""
    result = agent.run_sync(prompt)
    # result.output contains the LLM's response
    return result.output.strip()
