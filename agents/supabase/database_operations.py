"""
Database operations for DatabaseAgent: category persistence, insert/upsert, fetch, and schema commands.
"""
from typing import Dict, Any, Optional
from .supabase_client import get_supabase_client
from .category_classifier import classify_category
from .schema_inspector import fetch_table_schema
from models.model_generator import get_or_create_model, clear_model_cache

# --- Category Persistence ---
def category_exists(category: str) -> bool:
    supabase = get_supabase_client()
    res = supabase.table("categories").select("name").eq("name", category).execute()
    return bool(res.data)

def insert_category(category: str) -> None:
    supabase = get_supabase_client()
    supabase.table("categories").insert({"name": category}).execute()

# --- Insert/Upsert Handler ---
def handle_insert(table_name: str, data: dict, schema_changes: bool = False) -> dict:
    schema = fetch_table_schema(table_name)
    model = get_or_create_model(table_name, schema)
    try:
        validated = model(**data)
    except Exception as e:
        return {"success": False, "message": "Validation error", "data": None, "error": {"code": "validation_error", "detail": str(e)}}
    # Category classification
    if "category" in data:
        category = data["category"]
    else:
        # Fetch existing categories
        supabase = get_supabase_client()
        cat_res = supabase.table("categories").select("name").execute()
        existing = [row["name"] for row in cat_res.data] if cat_res.data else []
        category = classify_category(data, existing)
        if not category_exists(category):
            insert_category(category)
        data["category"] = category
    # Upsert
    supabase = get_supabase_client()
    upsert_res = supabase.table(table_name).upsert(data).execute()
    return {"success": True, "message": "Inserted", "data": upsert_res.data, "error": None}

# --- Fetch/List Handler ---
def handle_fetch(table_name: str, filters: Optional[dict] = None) -> dict:
    supabase = get_supabase_client()
    query = supabase.table(table_name).select("*")
    if filters:
        for k, v in filters.items():
            query = query.eq(k, v)
    res = query.execute()
    return {"success": True, "message": "Fetched", "data": res.data or [], "error": None}

# --- Schema Command Handler ---
def handle_schema_command(command: dict) -> dict:
    supabase = get_supabase_client()
    try:
        if command.get("type") == "add_column":
            table = command["table"]
            column = command["column"]
            data_type = command["data_type"]
            sql = f"ALTER TABLE {table} ADD COLUMN {column} {data_type};"
            supabase.rpc("execute_sql", {"sql": sql}).execute()
            clear_model_cache()
            return {"success": True, "message": f"Added column {column} to {table}.", "data": None, "error": None}
        elif command.get("type") == "create_table":
            table = command["table"]
            columns = command["columns"] # list of dicts: [{"name":..., "type":...}]
            cols_sql = ", ".join([f'{c["name"]} {c["type"]}' for c in columns])
            sql = f"CREATE TABLE {table} ({cols_sql});"
            supabase.rpc("execute_sql", {"sql": sql}).execute()
            clear_model_cache()
            return {"success": True, "message": f"Created table {table}.", "data": None, "error": None}
        else:
            return {"success": False, "message": "Unknown command type", "data": None, "error": {"code": "unknown_command", "detail": str(command)}}
    except Exception as e:
        return {"success": False, "message": "Schema command failed", "data": None, "error": {"code": "schema_error", "detail": str(e)}}
