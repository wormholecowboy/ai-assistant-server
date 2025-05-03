"""
Dynamic Pydantic model generation and caching.
"""
from typing import Dict, Any, Type
from pydantic import BaseModel, create_model

_model_cache = {}

def get_or_create_model(table: str, columns: Dict[str, str]) -> Type[BaseModel]:
    if table in _model_cache:
        return _model_cache[table]
    fields = {k: (Any, ...) for k in columns.keys()}  # TODO: map types properly
    from pydantic import ConfigDict
    model = create_model(
        f"{table.title()}Model",
        **fields,
    )
    _model_cache[table] = model
    return model

def clear_model_cache():
    _model_cache.clear()
