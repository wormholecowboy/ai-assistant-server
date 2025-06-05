"""
DatabaseAgent subagent for orchestrator integration.
"""
from pydantic import BaseModel
from pydantic_ai import Agent
from database_agent.agent import DatabaseAgent
from database_agent.response_models import DatabaseAgentResponse
from typing import Optional, Dict

_db_agent = DatabaseAgent()
db_agent = Agent()

class InsertInput(BaseModel):
    table: str
    data: Dict
    schema_changes: bool = False

class FetchInput(BaseModel):
    table: str
    filters: Optional[Dict] = None

class SchemaCommandInput(BaseModel):
    command: Dict

@db_agent.tool
async def insert(inputs: InsertInput) -> DatabaseAgentResponse:
    """
    Insert or upsert a record in the specified table.

    Args:
        inputs (InsertInput): The input data for the insert operation.

    Returns:
        DatabaseAgentResponse: The result of the insert operation.
    """
    result = _db_agent.handle_insert(inputs.table, inputs.data, inputs.schema_changes)
    return DatabaseAgentResponse(**result)

@db_agent.tool
async def fetch(inputs: FetchInput) -> DatabaseAgentResponse:
    """
    Fetch records from the specified table with optional filters.

    Args:
        inputs (FetchInput): The input data for the fetch operation.

    Returns:
        DatabaseAgentResponse: The result of the fetch operation.
    """
    result = _db_agent.handle_fetch(inputs.table, inputs.filters)
    return DatabaseAgentResponse(**result)

@db_agent.tool
async def schema_command(inputs: SchemaCommandInput) -> DatabaseAgentResponse:
    """
    Handle schema evolution commands (e.g., add column, create table).

    Args:
        inputs (SchemaCommandInput): The schema command details.

    Returns:
        DatabaseAgentResponse: The result of the schema command operation.
    """
    result = _db_agent.handle_schema_command(inputs.command)
    return DatabaseAgentResponse(**result)
