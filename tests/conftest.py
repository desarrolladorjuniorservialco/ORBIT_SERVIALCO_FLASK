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
    _app = create_app(TEST_CONFIG)

    # Stub dashboard blueprint — evita BuildError cuando el blueprint real
    # aún no está registrado (Fases 1-4)
    if 'dashboard' not in _app.blueprints:
        from flask import Blueprint
        dash_bp = Blueprint('dashboard', __name__)

        @dash_bp.route('/dashboard/general')
        def general():
            return 'general'

        _app.register_blueprint(dash_bp)

    # Stub api blueprint — evita BuildError en url_for('api.set_contrato')
    # cuando el blueprint real aún no está registrado (Fases 1-5)
    if 'api' not in _app.blueprints:
        from flask import Blueprint
        api_bp = Blueprint('api', __name__, url_prefix='/api')

        @api_bp.route('/set-contrato', methods=['POST'])
        def set_contrato():
            return '', 200

        _app.register_blueprint(api_bp)

    return _app


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
