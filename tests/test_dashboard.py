import pytest
from unittest.mock import patch

CONTRATO_FIXTURE = {
    'id': 'test-contrato-id',
    'nombre': 'Contrato Fibra',
    'objeto': 'Tendido de fibra óptica',
    'entidad_contratante': 'MinTIC',
    'localizacion': 'Putumayo',
    'fecha_inicio': '2024-01-01',
    'fecha_fin': '2025-12-31',
    'plazo_meses': 24,
    'valor_contrato': 40700000,
    'nombre_contratista': 'Empresa A SAS',
    'nombre_interventoria': 'Interventores SA',
    'porcentaje_ejecutado': 65.0,
}


def test_general_redirects_to_login_when_not_authenticated(client):
    resp = client.get('/dashboard/general')
    assert resp.status_code == 302
    assert '/login' in resp.headers['Location']


def test_general_returns_200_when_authenticated(auth_session):
    with patch('app.dashboard.routes.get_contrato', return_value=CONTRATO_FIXTURE):
        resp = auth_session.get('/dashboard/general')
        assert resp.status_code == 200
        assert 'Contrato Fibra'.encode() in resp.data or b'MinTIC' in resp.data


def test_general_returns_403_if_module_not_visible(client):
    with client.session_transaction() as sess:
        sess['user_id'] = 'uid-1'
        sess['rol'] = 'operativo'
        sess['modulos_visibles'] = []
        sess['contrato_activo_id'] = 'c1'
    resp = client.get('/dashboard/general')
    assert resp.status_code == 403


def test_hitos_returns_200_when_authenticated(auth_session):
    with patch('app.dashboard.routes.get_hitos', return_value=[]):
        resp = auth_session.get('/dashboard/hitos')
        assert resp.status_code == 200


def test_encuestas_returns_200_when_authenticated(auth_session):
    resp = auth_session.get('/dashboard/encuestas')
    assert resp.status_code == 200


def test_instalaciones_returns_200_when_authenticated(auth_session):
    resp = auth_session.get('/dashboard/instalaciones')
    assert resp.status_code == 200


def test_currency_col_filter_millions(app):
    with app.app_context():
        result = app.jinja_env.filters['currency_col'](40700000)
        assert 'M' in result


def test_date_col_filter_formats_correctly(app):
    with app.app_context():
        result = app.jinja_env.filters['date_col']('2024-01-15')
        assert result == '15/01/2024'


def test_progress_color_success(app):
    with app.app_context():
        assert app.jinja_env.filters['progress_color'](75) == 'success'
        assert app.jinja_env.filters['progress_color'](30) == 'warning'
        assert app.jinja_env.filters['progress_color'](10) == 'danger'
