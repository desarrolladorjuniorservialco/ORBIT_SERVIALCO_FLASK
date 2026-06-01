import pytest
from unittest.mock import MagicMock, patch


@pytest.fixture
def mock_db():
    mock = MagicMock()
    with patch('app.utils.supabase_client._data_client', new=mock):
        yield mock


def test_get_instalaciones_returns_data_and_count(mock_db):
    mock_chain = mock_db.table.return_value
    mock_chain.select.return_value.eq.return_value.range.return_value.execute.return_value.data = [
        {'id': 'i1', 'contrato_id': 'c1'},
    ]
    mock_chain.select.return_value.eq.return_value.range.return_value.execute.return_value.count = 1

    from app.models.instalaciones import get_instalaciones
    data, count = get_instalaciones('c1', page=1, per_page=25)
    assert len(data) == 1
    assert count == 1


def test_delete_instalacion_calls_delete(mock_db):
    mock_db.table.return_value.delete.return_value.eq.return_value.execute.return_value.data = [{'id': 'i1'}]
    from app.models.instalaciones import delete_instalacion
    result = delete_instalacion('i1')
    assert result is True
