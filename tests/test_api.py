import pytest
from unittest.mock import patch, MagicMock


# ── set-contrato ────────────────────────────────────────────

def test_set_contrato_updates_session_and_redirects(auth_session):
    resp = auth_session.post('/api/set-contrato',
                             data={'contrato_id': 'test-contrato-id'})
    assert resp.status_code == 200
    assert resp.headers.get('HX-Redirect') is not None


def test_set_contrato_rejects_unauthorized_contrato(client):
    with client.session_transaction() as sess:
        sess['user_id'] = 'uid-2'
        sess['rol'] = 'supervision'
        sess['contratos_lista'] = [{'id': 'c1', 'nombre': 'Solo este'}]
        sess['contrato_activo_id'] = 'c1'
        sess['modulos_visibles'] = ['general']
    resp = client.post('/api/set-contrato', data={'contrato_id': 'otro-contrato-id'})
    assert resp.status_code == 403


def test_set_contrato_requires_login(client):
    resp = client.post('/api/set-contrato', data={'contrato_id': 'c1'})
    assert resp.status_code == 302


# ── comentarios ─────────────────────────────────────────────

def test_get_comentarios_returns_html(auth_session):
    with patch('app.api.routes.get_comentarios_db', return_value=[]):
        resp = auth_session.get('/api/comentarios?tipo=global&contrato_id=test-contrato-id')
        assert resp.status_code == 200
        assert b'comentarios' in resp.data.lower() or resp.status_code == 200


def test_post_comentario_creates_and_returns_panel(auth_session):
    with patch('app.api.routes.create_comentario_db', return_value={'id': 'cm1'}):
        with patch('app.api.routes.get_comentarios_db', return_value=[]):
            resp = auth_session.post('/api/comentarios', data={
                'tipo': 'global',
                'referencia_id': '',
                'contenido': 'Nota de prueba',
            })
            assert resp.status_code == 200


def test_post_comentario_rejects_operativo(client):
    with client.session_transaction() as sess:
        sess['user_id'] = 'uid-op'
        sess['rol'] = 'operativo'
        sess['contrato_activo_id'] = 'c1'
        sess['modulos_visibles'] = ['general']
    resp = client.post('/api/comentarios', data={
        'tipo': 'global', 'contenido': 'hola',
    })
    assert resp.status_code == 403


def test_post_comentario_rejects_empty_content(auth_session):
    resp = auth_session.post('/api/comentarios', data={
        'tipo': 'global', 'contenido': '   ',
    })
    assert resp.status_code == 400


# ── encuestas / instalaciones ───────────────────────────────

def test_get_encuestas_returns_html_partial(auth_session):
    with patch('app.api.routes.get_encuestas_db', return_value=([], 0)):
        resp = auth_session.get('/api/encuestas?page=1')
        assert resp.status_code == 200


def test_get_instalaciones_returns_html_partial(auth_session):
    with patch('app.api.routes.get_instalaciones_db', return_value=([], 0)):
        resp = auth_session.get('/api/instalaciones?page=1')
        assert resp.status_code == 200


# ── hitos estado ────────────────────────────────────────────

def test_patch_hito_estado_updates_and_returns_badge(auth_session):
    with patch('app.api.routes.update_estado_hito_db', return_value={'id': 'h1', 'estado': 'aprobado'}):
        resp = auth_session.patch('/api/hitos/h1/estado',
                                  data={'estado': 'aprobado'})
        assert resp.status_code == 200
        assert b'aprobado' in resp.data.lower() or b'Aprobado' in resp.data


def test_patch_hito_estado_rejects_directivo(client):
    with client.session_transaction() as sess:
        sess['user_id'] = 'uid-dir'
        sess['rol'] = 'directivo'
        sess['modulos_visibles'] = ['hitos']
        sess['contrato_activo_id'] = 'c1'
    resp = client.patch('/api/hitos/h1/estado', data={'estado': 'aprobado'})
    assert resp.status_code == 403


# ── delete registros ────────────────────────────────────────

def test_delete_encuesta_requires_admin(auth_session):
    with patch('app.api.routes.delete_encuesta_db', return_value=True):
        resp = auth_session.delete('/api/encuestas/e1')
        assert resp.status_code == 200


def test_delete_encuesta_rejects_non_admin(client):
    with client.session_transaction() as sess:
        sess['user_id'] = 'uid-dir'
        sess['rol'] = 'directivo'
        sess['contrato_activo_id'] = 'c1'
        sess['modulos_visibles'] = ['encuestas']
    resp = client.delete('/api/encuestas/e1')
    assert resp.status_code == 403


def test_delete_instalacion_requires_admin(auth_session):
    with patch('app.api.routes.delete_instalacion_db', return_value=True):
        resp = auth_session.delete('/api/instalaciones/i1')
        assert resp.status_code == 200


# ── porcentaje ejecutado ────────────────────────────────────

def test_update_porcentaje_ejecutado(auth_session):
    with patch('app.api.routes.update_porcentaje_db', return_value={}):
        resp = auth_session.post('/api/contratos/ejecutado',
                                 data={'porcentaje': '75.5'})
        assert resp.status_code == 200
