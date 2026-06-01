import pytest
from unittest.mock import MagicMock, patch
from app import create_app

TEST_CONFIG = {
    'TESTING': True,
    'SECRET_KEY': 'test-secret',
    'SUPABASE_URL': 'https://test.supabase.co',
    'SUPABASE_ANON_KEY': 'test-anon-key',
    'SUPABASE_SERVICE_KEY': 'test-service-key',
}


@pytest.fixture
def app():
    return create_app(TEST_CONFIG)


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def mock_data_client():
    """Mock del cliente de datos Supabase para todos los tests de modelos."""
    mock = MagicMock()
    with patch('app.utils.supabase_client._data_client', new=mock):
        yield mock


@pytest.fixture
def mock_auth_client():
    """Mock del cliente Auth Supabase."""
    mock = MagicMock()
    with patch('app.utils.supabase_client._auth_client', new=mock):
        yield mock


@pytest.fixture
def auth_session(client):
    """Sesión autenticada como administrador."""
    with client.session_transaction() as sess:
        sess['user_id'] = 'test-user-id'
        sess['rol'] = 'administrador'
        sess['nombre'] = 'Test Admin'
        sess['email'] = 'admin@test.com'
        sess['contrato_activo_id'] = 'test-contrato-id'
        sess['access_token'] = 'test-access-token'
        sess['refresh_token'] = 'test-refresh-token'
        sess['contratos_lista'] = [{'id': 'test-contrato-id', 'nombre': 'Contrato Test'}]
        sess['modulos_visibles'] = ['general', 'hitos', 'encuestas', 'instalaciones']
    return client


@pytest.fixture
def supervisor_session(client):
    """Sesión autenticada como supervisión."""
    with client.session_transaction() as sess:
        sess['user_id'] = 'supervisor-id'
        sess['rol'] = 'supervision'
        sess['nombre'] = 'Test Supervisor'
        sess['email'] = 'super@test.com'
        sess['contrato_activo_id'] = 'test-contrato-id'
        sess['access_token'] = 'test-access-token'
        sess['refresh_token'] = 'test-refresh-token'
        sess['contratos_lista'] = [{'id': 'test-contrato-id', 'nombre': 'Contrato Test'}]
        sess['modulos_visibles'] = ['general', 'hitos', 'encuestas']
    return client
