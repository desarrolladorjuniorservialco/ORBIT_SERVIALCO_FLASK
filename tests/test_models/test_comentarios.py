import pytest
from unittest.mock import MagicMock, patch


@pytest.fixture
def mock_db():
    mock = MagicMock()
    with patch('app.utils.supabase_client._data_client', new=mock):
        yield mock


def test_get_comentarios_globales(mock_db):
    mock_db.table.return_value.select.return_value.eq.return_value.eq.return_value.is_.return_value.order.return_value.execute.return_value.data = [
        {'id': 'cm1', 'tipo': 'global', 'contenido': 'Nota global', 'referencia_id': None},
    ]
    from app.models.comentarios import get_comentarios
    result = get_comentarios('c1', tipo='global')
    assert len(result) == 1
    assert result[0]['tipo'] == 'global'


def test_get_comentarios_por_registro(mock_db):
    mock_db.table.return_value.select.return_value.eq.return_value.eq.return_value.eq.return_value.order.return_value.execute.return_value.data = [
        {'id': 'cm2', 'tipo': 'encuesta', 'contenido': 'Obs registro', 'referencia_id': 'e1'},
    ]
    from app.models.comentarios import get_comentarios
    result = get_comentarios('c1', tipo='encuesta', referencia_id='e1')
    assert result[0]['referencia_id'] == 'e1'


def test_create_comentario(mock_db):
    mock_db.table.return_value.insert.return_value.execute.return_value.data = [
        {'id': 'cm3', 'contenido': 'Nuevo comentario', 'tipo': 'global', 'contrato_id': 'c1'}
    ]
    from app.models.comentarios import create_comentario
    result = create_comentario(
        contrato_id='c1',
        autor_id='uid-1',
        tipo='global',
        contenido='Nuevo comentario',
    )
    assert result['contenido'] == 'Nuevo comentario'


def test_create_comentario_tipo_invalido():
    from app.models.comentarios import create_comentario
    with pytest.raises(ValueError, match='Tipo inválido'):
        create_comentario('c1', 'uid-1', 'invalido', 'texto')
