import pytest
from unittest.mock import MagicMock, patch


@pytest.fixture
def mock_db():
    mock = MagicMock()
    with patch('app.utils.supabase_client._data_client', new=mock):
        yield mock


def test_get_usuario_returns_dict(mock_db):
    mock_db.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value.data = {
        'id': 'uid-1', 'nombre_completo': 'Ana Torres', 'rol': 'administrador', 'activo': True
    }
    from app.models.usuarios import get_usuario
    result = get_usuario('uid-1')
    assert result['rol'] == 'administrador'
    assert result['nombre_completo'] == 'Ana Torres'


def test_get_usuario_not_found_returns_none(mock_db):
    mock_db.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value.data = None
    from app.models.usuarios import get_usuario
    result = get_usuario('no-existe')
    assert result is None


def test_get_modulos_visibles_returns_list(mock_db):
    mock_db.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value.data = [
        {'modulo': 'general'},
        {'modulo': 'hitos'},
        {'modulo': 'encuestas'},
    ]
    from app.models.usuarios import get_modulos_visibles
    result = get_modulos_visibles('supervision')
    assert result == ['general', 'hitos', 'encuestas']


def test_get_contratos_by_user_admin_returns_all(mock_db):
    mock_db.table.return_value.select.return_value.execute.return_value.data = [
        {'id': 'c1', 'nombre': 'Contrato A'},
        {'id': 'c2', 'nombre': 'Contrato B'},
    ]
    from app.models.usuarios import get_contratos_by_user
    result = get_contratos_by_user('uid-1', 'administrador')
    assert len(result) == 2


def test_get_contratos_by_user_non_admin_filters_by_assignment(mock_db):
    mock_db.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [
        {'contrato_id': 'c1', 'contratos': {'id': 'c1', 'nombre': 'Contrato A'}},
    ]
    from app.models.usuarios import get_contratos_by_user
    result = get_contratos_by_user('uid-2', 'supervision')
    assert len(result) == 1
    assert result[0]['id'] == 'c1'
