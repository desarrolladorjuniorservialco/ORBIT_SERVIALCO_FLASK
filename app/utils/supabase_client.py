import os
from supabase import create_client, Client

_auth_client: Client | None = None
_data_client: Client | None = None


def get_auth_client() -> Client:
    """Cliente con anon key — solo para operaciones de Supabase Auth."""
    global _auth_client
    if _auth_client is None:
        _auth_client = create_client(
            os.environ['SUPABASE_URL'],
            os.environ['SUPABASE_ANON_KEY'],
        )
    return _auth_client


def get_data_client() -> Client:
    """Cliente con service key — operaciones de base de datos (bypasses RLS)."""
    global _data_client
    if _data_client is None:
        _data_client = create_client(
            os.environ['SUPABASE_URL'],
            os.environ['SUPABASE_SERVICE_KEY'],
        )
    return _data_client
