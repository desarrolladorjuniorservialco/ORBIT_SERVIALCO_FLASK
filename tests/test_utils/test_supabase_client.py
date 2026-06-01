import pytest
from unittest.mock import patch, MagicMock


def test_get_data_client_returns_singleton():
    """get_data_client devuelve siempre la misma instancia."""
    mock = MagicMock()
    with patch('app.utils.supabase_client._data_client', mock):
        from app.utils.supabase_client import get_data_client
        c1 = get_data_client()
        c2 = get_data_client()
        assert c1 is c2


def test_get_auth_client_returns_singleton():
    """get_auth_client devuelve siempre la misma instancia."""
    mock = MagicMock()
    with patch('app.utils.supabase_client._auth_client', mock):
        from app.utils.supabase_client import get_auth_client
        c1 = get_auth_client()
        c2 = get_auth_client()
        assert c1 is c2
