import pytest
from unittest.mock import MagicMock, patch


# ── Login ──────────────────────────────────────────────────────────────────

def test_login_get_returns_200(client):
    resp = client.get('/login')
    assert resp.status_code == 200


def test_login_post_success_redirects_to_dashboard(client, mock_auth_client, mock_data_client):
    mock_session = MagicMock()
    mock_session.user.id = 'uid-1'
    mock_session.session.access_token = 'tok-abc'
    mock_session.session.refresh_token = 'ref-abc'
    mock_auth_client.auth.sign_in_with_password.return_value = mock_session

    mock_data_client.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value.data = {
        'id': 'uid-1', 'nombre_completo': 'Ana Torres',
        'rol': 'administrador', 'activo': True,
    }
    mock_data_client.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value.data = [
        {'modulo': 'general'}, {'modulo': 'hitos'},
    ]
    mock_data_client.table.return_value.select.return_value.execute.return_value.data = [
        {'id': 'c1', 'nombre': 'Contrato A'}
    ]

    resp = client.post('/login', data={'email': 'ana@test.com', 'password': 'secret'})
    assert resp.status_code == 302
    assert '/dashboard' in resp.headers['Location']


def test_login_post_invalid_credentials_shows_error(client, mock_auth_client):
    mock_auth_client.auth.sign_in_with_password.side_effect = Exception('Invalid credentials')
    resp = client.post('/login', data={'email': 'bad@test.com', 'password': 'wrong'})
    assert resp.status_code == 200
    assert 'Credenciales incorrectas'.encode() in resp.data


def test_login_post_missing_fields_shows_error(client):
    resp = client.post('/login', data={'email': '', 'password': ''})
    assert resp.status_code == 200
    assert 'requeridos'.encode() in resp.data


# ── Logout ─────────────────────────────────────────────────────────────────

def test_logout_clears_session_and_redirects(auth_session, mock_auth_client):
    mock_auth_client.auth.sign_out.return_value = None
    resp = auth_session.post('/logout')
    assert resp.status_code == 302
    assert '/login' in resp.headers['Location']


def test_logout_requires_login(client):
    resp = client.post('/logout')
    assert resp.status_code == 302
    assert '/login' in resp.headers['Location']


# ── Cambiar contraseña ──────────────────────────────────────────────────────

def test_cambiar_contrasena_passwords_mismatch(auth_session):
    resp = auth_session.post('/cambiar-contrasena', data={
        'current_password': 'old',
        'new_password': 'nueva1234',
        'confirm_password': 'diferente',
    })
    assert resp.status_code == 302


def test_cambiar_contrasena_too_short(auth_session):
    resp = auth_session.post('/cambiar-contrasena', data={
        'current_password': 'old',
        'new_password': 'corta',
        'confirm_password': 'corta',
    })
    assert resp.status_code == 302


def test_cambiar_contrasena_success(auth_session, mock_auth_client):
    mock_session = MagicMock()
    mock_session.user.id = 'test-user-id'
    mock_auth_client.auth.sign_in_with_password.return_value = mock_session
    mock_auth_client.auth.update_user.return_value = MagicMock()

    resp = auth_session.post('/cambiar-contrasena', data={
        'current_password': 'correcta',
        'new_password': 'nueva1234',
        'confirm_password': 'nueva1234',
    })
    assert resp.status_code == 302
