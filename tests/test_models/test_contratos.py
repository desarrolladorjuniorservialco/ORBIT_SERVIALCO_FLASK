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
        'id': 'c1', 'nombre': 'Contrato Fibra', 'valor_contrato': 40700000,
        'fecha_inicio': '2024-01-01', 'fecha_fin': '2025-12-31',
        'porcentaje_ejecutado': 65.0,
    }
    from app.models.contratos import get_contrato
    result = get_contrato('c1')
    assert result['nombre'] == 'Contrato Fibra'
    assert result['porcentaje_ejecutado'] == 65.0


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


def test_update_porcentaje_ejecutado(mock_db):
    mock_db.table.return_value.update.return_value.eq.return_value.execute.return_value.data = [
        {'id': 'c1', 'porcentaje_ejecutado': 75.0}
    ]
    from app.models.contratos import update_porcentaje_ejecutado
    result = update_porcentaje_ejecutado('c1', 75.0)
    assert result['porcentaje_ejecutado'] == 75.0
