"""
DatabaseAgent: Core agent logic for database CRUD and schema operations.
"""
from typing import Any, Dict, Optional
from pydantic import BaseModel
from pydantic_ai import Agent, RunContext
from typing import Any, Dict, Optional
from .database_operations import handle_insert, handle_fetch, handle_schema_command

class DatabaseAgent:
    """
    Orchestrates database operations by delegating to the core handlers in database_operations.py.
    """
    def __init__(self):
        pass

    def handle_insert(self, table: str, data: Dict[str, Any], schema_changes: bool = False) -> Dict[str, Any]:
        """
        Insert or upsert a record in the specified table.

        Args:
            table (str): The table name.
            data (dict): The data payload.
            schema_changes (bool): Whether schema changes are allowed (default: False).
        Returns:
            dict: Operation result with success, message, data, and error.
        """
        return handle_insert(table, data, schema_changes)

    def handle_fetch(self, table: str, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Fetch records from the specified table, optionally filtered.

        Args:
            table (str): The table name.
            filters (dict, optional): Filters to apply.
        Returns:
            dict: Operation result with success, message, data, and error.
        """
        return handle_fetch(table, filters)

    def handle_schema_command(self, command: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle schema evolution commands (add column, create table).

        Args:
            command (dict): Schema command details.
        Returns:
            dict: Operation result with success, message, data, and error.
        """
        return handle_schema_command(command)
