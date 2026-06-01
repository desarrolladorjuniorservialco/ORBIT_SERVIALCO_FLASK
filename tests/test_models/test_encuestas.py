import pytest
from unittest.mock import MagicMock, patch


@pytest.fixture
def mock_db():
    mock = MagicMock()
    with patch('app.utils.supabase_client._data_client', new=mock):
        yield mock


def test_get_encuestas_returns_data_and_count(mock_db):
    mock_chain = mock_db.table.return_value
    mock_chain.select.return_value.eq.return_value.range.return_value.execute.return_value.data = [
        {'id': 'e1', 'contrato_id': 'c1'},
        {'id': 'e2', 'contrato_id': 'c1'},
    ]
    mock_chain.select.return_value.eq.return_value.range.return_value.execute.return_value.count = 2

    from app.models.encuestas import get_encuestas
    data, count = get_encuestas('c1', page=1, per_page=25)
    assert len(data) == 2
    assert count == 2


def test_delete_encuesta_calls_delete(mock_db):
    mock_db.table.return_value.delete.return_value.eq.return_value.execute.return_value.data = [{'id': 'e1'}]
    from app.models.encuestas import delete_encuesta
    result = delete_encuesta('e1')
    assert result is True
