# Gestión de Contratos — Plan Fase 3: Auth Routes + Login UI

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Prerequisito:** Fase 2 completada. `22 passed` en la suite de tests.

**Goal:** Rutas de autenticación funcionales (login, logout, cambio de contraseña), blueprint registrado en la app factory, y template de login con el diseño split-panel del sector infraestructura.

**Fases del proyecto:**
- ✅ Fase 1 — Scaffolding + Config + Auth Utils
- ✅ Fase 2 — Models
- ✅ **Fase 3** — Auth routes + Login UI ← estás aquí
- Fase 4 — CSS Design System + App Shell
- Fase 5 — Dashboard modules
- Fase 6 — HTMX API endpoints
- Fase 7 — SQL Migration + smoke test

---

## File Map (esta fase)

| Archivo | Responsabilidad |
|---|---|
| `app/auth/__init__.py` | Blueprint `auth` |
| `app/auth/routes.py` | `/login`, `/logout`, `/cambiar-contrasena` |
| `app/__init__.py` | Registra blueprint auth + context processor base |
| `app/templates/auth/login.html` | Página de login split-panel |
| `tests/test_auth.py` | Tests de rutas auth |

---

## Task 12: Auth blueprint + rutas

**Files:**
- Modificar: `app/auth/__init__.py`
- Crear: `app/auth/routes.py`

- [ ] **Step 1: Escribir tests que fallan**

```python
# tests/test_auth.py
import pytest
from unittest.mock import MagicMock, patch


# ── Login ──────────────────────────────────────────────────────────────────

def test_login_get_returns_200(client):
    resp = client.get('/login')
    assert resp.status_code == 200


def test_login_post_success_redirects_to_dashboard(client, mock_auth_client, mock_data_client):
    # Supabase Auth devuelve sesión válida
    mock_session = MagicMock()
    mock_session.user.id = 'uid-1'
    mock_session.session.access_token = 'tok-abc'
    mock_session.session.refresh_token = 'ref-abc'
    mock_auth_client.auth.sign_in_with_password.return_value = mock_session

    # Tabla usuarios devuelve el usuario
    mock_data_client.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value.data = {
        'id': 'uid-1', 'nombre_completo': 'Ana Torres',
        'rol': 'administrador', 'activo': True,
    }
    # get_modulos_visibles
    mock_data_client.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value.data = [
        {'modulo': 'general'}, {'modulo': 'hitos'},
    ]
    # get_contratos_by_user (admin → select all)
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
```

- [ ] **Step 2: Correr tests — deben fallar**

```powershell
python -m pytest tests/test_auth.py -v
```

Esperado: `ERROR` o `FAILED` — blueprint no registrado aún

- [ ] **Step 3: Definir blueprint en `app/auth/__init__.py`**

```python
# app/auth/__init__.py
from flask import Blueprint

bp = Blueprint('auth', __name__)

from app.auth import routes  # noqa: E402,F401
```

- [ ] **Step 4: Implementar `app/auth/routes.py`**

```python
# app/auth/routes.py
from flask import render_template, redirect, url_for, request, session, flash
from app.auth import bp
from app.utils.supabase_client import get_auth_client, get_data_client
from app.utils.auth import login_required
from app.models.usuarios import get_usuario, get_modulos_visibles, get_contratos_by_user


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('dashboard.general'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()

        if not email or not password:
            flash('Email y contraseña son requeridos', 'error')
            return render_template('auth/login.html')

        try:
            auth_client = get_auth_client()
            resp = auth_client.auth.sign_in_with_password(
                {'email': email, 'password': password}
            )
            user_id = resp.user.id
            access_token = resp.session.access_token
            refresh_token = resp.session.refresh_token

            usuario = get_usuario(user_id)
            if not usuario or not usuario.get('activo'):
                flash('Usuario inactivo o no encontrado', 'error')
                return render_template('auth/login.html')

            rol = usuario['rol']
            contratos = get_contratos_by_user(user_id, rol)
            modulos = get_modulos_visibles(rol)

            session.clear()
            session['user_id'] = user_id
            session['email'] = email
            session['nombre'] = usuario['nombre_completo']
            session['rol'] = rol
            session['access_token'] = access_token
            session['refresh_token'] = refresh_token
            session['contratos_lista'] = contratos
            session['contrato_activo_id'] = contratos[0]['id'] if contratos else None
            session['modulos_visibles'] = modulos

            return redirect(url_for('dashboard.general'))

        except Exception:
            flash('Credenciales incorrectas', 'error')
            return render_template('auth/login.html')

    return render_template('auth/login.html')


@bp.route('/logout', methods=['POST'])
@login_required
def logout():
    try:
        auth_client = get_auth_client()
        auth_client.auth.set_session(
            session.get('access_token', ''),
            session.get('refresh_token', ''),
        )
        auth_client.auth.sign_out()
    except Exception:
        pass
    session.clear()
    return redirect(url_for('auth.login'))


@bp.route('/cambiar-contrasena', methods=['POST'])
@login_required
def cambiar_contrasena():
    current_password = request.form.get('current_password', '')
    new_password = request.form.get('new_password', '')
    confirm_password = request.form.get('confirm_password', '')
    redirect_to = request.referrer or url_for('dashboard.general')

    if new_password != confirm_password:
        flash('Las contraseñas nuevas no coinciden', 'error')
        return redirect(redirect_to)

    if len(new_password) < 8:
        flash('La contraseña debe tener al menos 8 caracteres', 'error')
        return redirect(redirect_to)

    try:
        auth_client = get_auth_client()
        # Verificar contraseña actual
        auth_client.auth.sign_in_with_password(
            {'email': session['email'], 'password': current_password}
        )
        # Actualizar contraseña
        auth_client.auth.set_session(
            session['access_token'],
            session['refresh_token'],
        )
        auth_client.auth.update_user({'password': new_password})
        flash('Contraseña actualizada exitosamente', 'success')
    except Exception:
        flash('Contraseña actual incorrecta', 'error')

    return redirect(redirect_to)
```

- [ ] **Step 5: Registrar blueprint en la app factory**

Reemplazar `app/__init__.py` con:

```python
# app/__init__.py
from flask import Flask
from config import Config


def create_app(config_object=None):
    app = Flask(__name__)

    if isinstance(config_object, dict):
        app.config.from_object(Config)
        app.config.update(config_object)
    else:
        app.config.from_object(config_object or Config)

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp)

    # Ruta raíz — redirige según sesión
    from flask import session, redirect, url_for

    @app.route('/')
    def index():
        if 'user_id' in session:
            return redirect(url_for('dashboard.general'))
        return redirect(url_for('auth.login'))

    # Context processor — datos disponibles en todos los templates
    @app.context_processor
    def inject_globals():
        from flask import session
        return {
            'modulos_visibles': session.get('modulos_visibles', []),
            'contratos_lista': session.get('contratos_lista', []),
            'contrato_activo_id': session.get('contrato_activo_id'),
            'current_user_nombre': session.get('nombre', ''),
            'current_user_rol': session.get('rol', ''),
        }

    return app
```

- [ ] **Step 6: Crear template mínimo para que los tests pasen**

```html
<!-- app/templates/auth/login.html -->
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <title>Iniciar sesión</title>
</head>
<body>
  {% with messages = get_flashed_messages(with_categories=true) %}
    {% for category, message in messages %}
      <p class="flash flash--{{ category }}">{{ message }}</p>
    {% endfor %}
  {% endwith %}

  <form method="POST" action="/login">
    <input type="email" name="email" placeholder="Correo electrónico" required>
    <input type="password" name="password" placeholder="Contraseña" required>
    <button type="submit">Ingresar al sistema</button>
  </form>
</body>
</html>
```

> Este template se reemplaza con el diseño completo en el Step 7.

- [ ] **Step 7: Correr tests — deben pasar**

```powershell
python -m pytest tests/test_auth.py -v
```

Esperado: `9 passed`

- [ ] **Step 8: Correr suite completa**

```powershell
python -m pytest tests/ -v --tb=short
```

Esperado: `31 passed, 0 failed`

- [ ] **Step 9: Commit**

```powershell
git add app/auth/__init__.py app/auth/routes.py app/__init__.py app/templates/auth/login.html tests/test_auth.py
git commit -m "feat: add auth blueprint with login, logout, cambiar-contrasena and tests"
```

---

## Task 13: Template de login (diseño completo)

**Files:**
- Modificar: `app/templates/auth/login.html`

> El CSS completo se agrega en Fase 4. Este template usa clases semánticas que el CSS de Fase 4 estilizará. Funciona visualmente básico hasta que se agregue el CSS.

- [ ] **Step 1: Reemplazar login.html con diseño completo**

```html
<!-- app/templates/auth/login.html -->
<!DOCTYPE html>
<html lang="es" data-theme="light">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Iniciar sesión — ORBIT SERVIALCO</title>
  <link rel="stylesheet" href="{{ url_for('static', filename='css/base.css') }}">
  <link rel="stylesheet" href="{{ url_for('static', filename='css/desktop.css') }}" media="(min-width: 768px)">
  <link rel="stylesheet" href="{{ url_for('static', filename='css/mobile.css') }}" media="(max-width: 767px)">
</head>
<body class="login-page">

  <div class="login-layout">

    <!-- Panel izquierdo: imagen de fondo técnico -->
    <div class="login-hero" aria-hidden="true">
      <div class="login-hero__overlay">
        <div class="login-hero__brand">
          <span class="login-hero__logo-mark">⬡</span>
          <span class="login-hero__brand-name">ORBIT SERVIALCO</span>
        </div>
        <p class="login-hero__tagline">
          Sistema de Gestión de Contratos<br>de Infraestructura
        </p>
      </div>
    </div>

    <!-- Panel derecho: formulario -->
    <div class="login-form-panel">
      <div class="login-card">

        <div class="login-card__header">
          <h1 class="login-card__title">Bienvenido</h1>
          <p class="login-card__subtitle">Ingresa tus credenciales para continuar</p>
        </div>

        <!-- Mensajes flash -->
        {% with messages = get_flashed_messages(with_categories=true) %}
          {% for category, message in messages %}
            <div class="alert alert--{{ category }}" role="alert">
              {{ message }}
            </div>
          {% endfor %}
        {% endwith %}

        <form method="POST" action="{{ url_for('auth.login') }}" class="login-form" novalidate>

          <div class="form-group">
            <label for="email" class="form-label">Correo electrónico</label>
            <input
              type="email"
              id="email"
              name="email"
              class="form-input"
              placeholder="usuario@empresa.com"
              autocomplete="email"
              required
            >
          </div>

          <div class="form-group">
            <label for="password" class="form-label">Contraseña</label>
            <input
              type="password"
              id="password"
              name="password"
              class="form-input"
              placeholder="••••••••"
              autocomplete="current-password"
              required
            >
          </div>

          <button type="submit" class="btn btn--primary btn--full">
            Ingresar al sistema
          </button>

        </form>

      </div>
    </div>

  </div>

</body>
</html>
```

- [ ] **Step 2: Correr tests de auth para verificar que el template no rompe nada**

```powershell
python -m pytest tests/test_auth.py -v
```

Esperado: `9 passed`

- [ ] **Step 3: Commit**

```powershell
git add app/templates/auth/login.html
git commit -m "feat: add complete login template (styled in fase 4)"
```

---

## Verificación final de Fase 3

- [ ] **Suite completa**

```powershell
python -m pytest tests/ -v --tb=short
```

Esperado: `31 passed, 0 failed`

- [ ] **Verificar que Flask arranca sin errores**

```powershell
python -c "from app import create_app; app = create_app(); print([str(r) for r in app.url_map.iter_rules()])"
```

Debe incluir: `/login`, `/logout`, `/cambiar-contrasena`, `/`

---

**Fase 3 completada. Continuar con Fase 4: CSS Design System + App Shell.**
