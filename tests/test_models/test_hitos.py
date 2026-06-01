import pytest
from unittest.mock import MagicMock, patch


@pytest.fixture
def mock_db():
    mock = MagicMock()
    with patch('app.utils.supabase_client._data_client', new=mock):
        yield mock


def test_get_hitos_returns_list(mock_db):
    mock_db.table.return_value.select.return_value.eq.return_value.order.return_value.execute.return_value.data = [
        {'id': 'h1', 'nombre': 'Hito 1', 'estado': 'pendiente', 'fecha_limite': '2025-03-01'},
        {'id': 'h2', 'nombre': 'Hito 2', 'estado': 'aprobado', 'fecha_limite': '2025-06-01'},
    ]
    from app.models.hitos import get_hitos
    result = get_hitos('c1')
    assert len(result) == 2
    assert result[0]['estado'] == 'pendiente'


def test_get_hitos_empty_returns_empty_list(mock_db):
    mock_db.table.return_value.select.return_value.eq.return_value.order.return_value.execute.return_value.data = []
    from app.models.hitos import get_hitos
    assert get_hitos('c1') == []


def test_update_estado_hito(mock_db):
    mock_db.table.return_value.update.return_value.eq.return_value.execute.return_value.data = [
        {'id': 'h1', 'estado': 'aprobado'}
    ]
    from app.models.hitos import update_estado_hito
    result = update_estado_hito('h1', 'aprobado')
    assert result['estado'] == 'aprobado'


def test_update_estado_hito_estado_invalido():
    from app.models.hitos import update_estado_hito
    with pytest.raises(ValueError, match='Estado inválido'):
        update_estado_hito('h1', 'invalido')
