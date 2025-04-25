"""
Response models for DatabaseAgent tool outputs.
"""
from typing import Any, Optional
from pydantic import BaseModel, ConfigDict

class DatabaseAgentResponse(BaseModel):
    """
    Standard response schema for DatabaseAgent tool outputs.
    """
    model_config = ConfigDict(extra='forbid')
    success: bool
    message: str
    data: Optional[Any] = None
    error: Optional[Any] = None
