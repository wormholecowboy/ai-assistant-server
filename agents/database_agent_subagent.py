"""
DatabaseAgent subagent for orchestrator integration.
"""
from pydantic import BaseModel
from pydantic_ai import Agent
from .supabase.database_operations import handle_insert as _handle_insert, handle_fetch as _handle_fetch, handle_schema_command as _handle_schema_command
from .supabase.response_models import DatabaseAgentResponse
from typing import Optional, Dict, Any
from .shared import get_model

db_agent = Agent(get_model())

class InsertInput(BaseModel):
    table: str
    data: Dict
    schema_changes: bool = False

class FetchInput(BaseModel):
    table: str
    filters: Optional[Dict] = None

class SchemaCommandInput(BaseModel):
    command: Dict

@db_agent.tool_plain
async def insert(inputs: InsertInput) -> DatabaseAgentResponse:
    """
    Insert or upsert a record in the specified table.

    Args:
        inputs (InsertInput): The input data for the insert operation.

    Returns:
        DatabaseAgentResponse: The result of the insert operation.
    """
    result = _handle_insert(inputs.table, inputs.data, inputs.schema_changes)
    return DatabaseAgentResponse(**result)

@db_agent.tool_plain
async def fetch(inputs: FetchInput) -> DatabaseAgentResponse:
    """
    Fetch records from the specified table with optional filters.

    Args:
        inputs (FetchInput): The input data for the fetch operation.

    Returns:
        DatabaseAgentResponse: The result of the fetch operation.
    """
    result = _handle_fetch(inputs.table, inputs.filters)
    return DatabaseAgentResponse(**result)

@db_agent.tool_plain
async def schema_command(inputs: SchemaCommandInput) -> DatabaseAgentResponse:
    """
    Handle schema evolution commands (e.g., add column, create table).

    Args:
        inputs (SchemaCommandInput): The schema command details.

    Returns:
        DatabaseAgentResponse: The result of the schema command operation.
    """
    result = _handle_schema_command(inputs.command)
    return DatabaseAgentResponse(**result)
