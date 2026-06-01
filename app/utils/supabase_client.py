import os
from supabase import create_client, Client

_auth_client: Client | None = None
_data_client: Client | None = None


def _require_env(*names: str) -> list[str]:
    missing = [n for n in names if not os.environ.get(n)]
    if missing:
        raise RuntimeError(
            f"Variables de entorno requeridas no configuradas: {', '.join(missing)}. "
            "Agrégalas a .env.local o a los Environment Variables del proyecto en Vercel."
        )
    return [os.environ[n] for n in names]


def get_auth_client() -> Client:
    global _auth_client
    if _auth_client is None:
        url, anon_key = _require_env('SUPABASE_URL', 'SUPABASE_ANON_KEY')
        _auth_client = create_client(url, anon_key)
    return _auth_client


def get_data_client() -> Client:
    global _data_client
    if _data_client is None:
        url, service_key = _require_env('SUPABASE_URL', 'SUPABASE_SERVICE_KEY')
        _data_client = create_client(url, service_key)
    return _data_client
