"""
Supabase client singleton initialization.
"""
import os
from supabase import create_client, Client

_supabase_client = None

def get_supabase_client() -> Client:
    global _supabase_client
    if _supabase_client is None:
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_ANON_KEY")
        if not url or not key:
            raise RuntimeError("Supabase credentials not set in environment.")
        _supabase_client = create_client(url, key)
    return _supabase_client
