import pytest
from datetime import date
from unittest.mock import MagicMock, patch


@pytest.fixture
def mock_db():
    mock = MagicMock()
    with patch('app.utils.supabase_client._data_client', new=mock):
        yield mock


def test_get_contrato_returns_dict(mock_db):
    mock_db.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value.data = {
        'id': 'c1',
        'nombre': 'Contrato Fibra',
        'contratista': 'Empresa A SAS',
        'intrventoria': 'Interventores SA',
        'supervisor': 'Juan Perez',
        'valor_contrato': 40700000,
        'fecha_inicio': '2024-01-01',
        'fecha_fin': '2025-12-31',
        'activo': True,
        'plazo_actual': None,
        'prorrogas': 0,
        'adiciones': 0,
        'valor_actual': None,
    }
    from app.models.contratos import get_contrato
    result = get_contrato('c1')
    assert result['nombre'] == 'Contrato Fibra'
    assert result['contratista'] == 'Empresa A SAS'


def test_calcular_progreso_tiempo_mitad():
    from app.models.contratos import calcular_progreso_tiempo
    inicio = date(2024, 1, 1)
    fin = date(2025, 1, 1)
    mitad = date(2024, 7, 2)
    resultado = calcular_progreso_tiempo(inicio, fin, hoy=mitad)
    assert 49.0 <= resultado <= 51.0


def test_calcular_progreso_tiempo_antes_de_inicio():
    from app.models.contratos import calcular_progreso_tiempo
    inicio = date(2025, 6, 1)
    fin = date(2026, 6, 1)
    antes = date(2025, 1, 1)
    assert calcular_progreso_tiempo(inicio, fin, hoy=antes) == 0.0


def test_calcular_progreso_tiempo_despues_de_fin():
    from app.models.contratos import calcular_progreso_tiempo
    inicio = date(2020, 1, 1)
    fin = date(2021, 1, 1)
    despues = date(2025, 1, 1)
    assert calcular_progreso_tiempo(inicio, fin, hoy=despues) == 100.0


def test_get_prorrogas_resumen_con_datos(mock_db):
    mock_db.table.return_value.select.return_value.eq.return_value.order.return_value.execute.return_value.data = [
        {'numero': 1, 'fecha_fin': '2025-06-30'},
        {'numero': 2, 'fecha_fin': '2026-03-31'},
    ]
    from app.models.contratos import get_prorrogas_resumen
    result = get_prorrogas_resumen('c1')
    assert result['count'] == 2
    assert result['plazo_actual'] == '2026-03-31'


def test_get_prorrogas_resumen_sin_datos(mock_db):
    mock_db.table.return_value.select.return_value.eq.return_value.order.return_value.execute.return_value.data = []
    from app.models.contratos import get_prorrogas_resumen
    result = get_prorrogas_resumen('c1')
    assert result['count'] == 0
    assert result['plazo_actual'] is None


def test_get_adiciones_resumen_con_datos(mock_db):
    mock_db.table.return_value.select.return_value.eq.return_value.order.return_value.execute.return_value.data = [
        {'numero': 1, 'valor_actual': 45000000},
        {'numero': 2, 'valor_actual': 52000000},
    ]
    from app.models.contratos import get_adiciones_resumen
    result = get_adiciones_resumen('c1')
    assert result['count'] == 2
    assert result['valor_actual'] == 52000000


def test_get_adiciones_resumen_sin_datos(mock_db):
    mock_db.table.return_value.select.return_value.eq.return_value.order.return_value.execute.return_value.data = []
    from app.models.contratos import get_adiciones_resumen
    result = get_adiciones_resumen('c1')
    assert result['count'] == 0
    assert result['valor_actual'] is None
