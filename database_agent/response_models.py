"""
Response models for DatabaseAgent tool outputs.
"""
from typing import Any, Optional
from pydantic import BaseModel, ConfigDict

class DatabaseAgentResponse(BaseModel):
    """
    Standard response schema for DatabaseAgent tool outputs.
    """
    success: bool
    message: str
    data: Optional[dict] = None # Changed from Any
    error: Optional[dict] = None # Changed from Any
