"""
DatabaseAgent subagent for orchestrator integration.
"""
from pydantic_ai import Agent
from database_agent.agent import DatabaseAgent
from database_agent.response_models import DatabaseAgentResponse

# Instantiate the DatabaseAgent
_db_agent = DatabaseAgent()

def get_database_agent():
    return _db_agent

# Optionally, you could wrap agent methods for orchestration
async def handle_insert(table: str, data: dict, schema_changes: bool = False) -> DatabaseAgentResponse:
    result = _db_agent.handle_insert(table, data, schema_changes)
    return DatabaseAgentResponse(**result)

async def handle_fetch(table: str, filters: dict = None) -> DatabaseAgentResponse:
    result = _db_agent.handle_fetch(table, filters)
    return DatabaseAgentResponse(**result)

async def handle_schema_command(command: dict) -> DatabaseAgentResponse:
    result = _db_agent.handle_schema_command(command)
    return DatabaseAgentResponse(**result)
