from pydantic_ai.agent import AgentRunResult
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.types import (
    FilePart,
    FileWithBytes,
    InvalidParamsError,
    Part,
    Task,
    TextPart,
    UnsupportedOperationError,
)
from a2a.utils import (
    completed_task,
    new_artifact,
)
from a2a.utils.errors import ServerError

from typing import Any, Dict, Optional

from pydantic import BaseModel
from pydantic_ai import Agent

from .shared import get_model
from .supabase.database_operations import handle_fetch as _handle_fetch
from .supabase.database_operations import handle_insert as _handle_insert
from .supabase.database_operations import \
    handle_schema_command as _handle_schema_command
from .supabase.response_models import DatabaseAgentResponse


class InsertInput(BaseModel):
    table: str
    data: Dict
    schema_changes: bool = False

class FetchInput(BaseModel):
    table: str
    filters: Optional[Dict] = None

class SchemaCommandInput(BaseModel):
    command: Dict

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

class SupabaseAgent:
    def __init__(self):
        self.agent = Agent(
            get_model(),
           system_prompt="""You are a database specialist. Help users manage their database. You have access to several tools to 
           complete all of the basic CRUD functions. You can use the insert, fetch, and schema_command tools to perform these actions,
           which means you can create and edit tables. Always respond with whether or not the action was successful.""",
           tools=[insert, fetch, schema_command])

    def invoke(self, query: str) -> AgentRunResult[str]:
        return self.agent.run_sync(query)

