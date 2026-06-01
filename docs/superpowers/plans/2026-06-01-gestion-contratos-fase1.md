# Gestión de Contratos — Plan Fase 1: Scaffolding + Config + Auth Utils

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Proyecto Flask vacío pero funcional: estructura de archivos, dependencias, configuración segura de credenciales, cliente Supabase singleton y decoradores de autenticación con tests.

**Architecture:** Factory pattern con blueprints. Credenciales en `.env`. Dos clientes Supabase: anon (Auth) y service role (datos). Decoradores `@login_required` y `@role_required` protegen todas las rutas.

**Tech Stack:** Python 3.12, Flask 3.x, supabase-py 2.x, python-dotenv, pytest 8.x, pytest-flask

**Fases del proyecto:**
- ✅ **Fase 1** — Scaffolding + Config + Auth Utils ← estás aquí
- Fase 2 — Models (Supabase data access)
- Fase 3 — Auth routes + Login UI
- Fase 4 — CSS Design System + App Shell
- Fase 5 — Dashboard modules
- Fase 6 — HTMX API endpoints
- Fase 7 — SQL Migration + smoke test

---

## File Map (esta fase)

| Archivo | Responsabilidad |
|---|---|
| `run.py` | Entry point |
| `config.py` | Lee `.env`, expone clase `Config` |
| `requirements.txt` | Dependencias Python |
| `.env.example` | Plantilla de credenciales |
| `.gitignore` | Excluye `.env` y archivos generados |
| `app/__init__.py` | App factory (stub — se amplía en fases siguientes) |
| `app/utils/supabase_client.py` | Singletons: `get_auth_client()`, `get_data_client()` |
| `app/utils/auth.py` | Decoradores `@login_required`, `@role_required` |
| `tests/conftest.py` | Fixtures pytest: app, client, mocks Supabase |
| `tests/test_utils/test_auth.py` | Tests para decoradores |

---

## Task 1: Git init + estructura de directorios

**Files:**
- Crear todos los directorios del proyecto

- [ ] **Step 1: Inicializar git y crear estructura**

```powershell
git init
New-Item -ItemType Directory -Force app, app/auth, app/dashboard, app/api, app/models, app/utils, app/templates/auth, app/templates/dashboard, app/templates/partials, app/static/css, app/static/js, tests/test_models, tests/test_utils, docs/supabase
```

- [ ] **Step 2: Crear archivos `__init__.py` vacíos**

```powershell
$dirs = @("app","app/auth","app/dashboard","app/api","app/models","app/utils","tests","tests/test_models","tests/test_utils")
foreach ($d in $dirs) { New-Item -ItemType File -Path "$d/__init__.py" -Force }
```

- [ ] **Step 3: Verificar estructura**

```powershell
Get-ChildItem -Recurse -Filter "__init__.py" | Select-Object FullName
```

Esperado: 9 archivos `__init__.py` listados.

- [ ] **Step 4: Commit inicial**

```powershell
git add .
git commit -m "chore: initialize project structure"
```

---

## Task 2: Dependencias, config y archivos raíz

**Files:**
- Crear: `requirements.txt`, `config.py`, `.env.example`, `.gitignore`, `run.py`

- [ ] **Step 1: Crear `requirements.txt`**

```
flask>=3.0.0
supabase>=2.0.0
python-dotenv>=1.0.0
pytest>=8.0.0
pytest-flask>=1.3.0
```

Guarda en `requirements.txt`.

- [ ] **Step 2: Crear `config.py`**

```python
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')
    SUPABASE_URL = os.environ.get('SUPABASE_URL', '')
    SUPABASE_ANON_KEY = os.environ.get('SUPABASE_ANON_KEY', '')
    SUPABASE_SERVICE_KEY = os.environ.get('SUPABASE_SERVICE_KEY', '')
```

- [ ] **Step 3: Crear `.env.example`**

```
SECRET_KEY=cambia-esto-por-una-clave-segura
SUPABASE_URL=https://tu-proyecto.supabase.co
SUPABASE_ANON_KEY=tu-anon-key-aqui
SUPABASE_SERVICE_KEY=tu-service-role-key-aqui
```

- [ ] **Step 4: Crear `.gitignore`**

```
.env
__pycache__/
*.pyc
*.pyo
.pytest_cache/
.venv/
venv/
*.egg-info/
dist/
build/
.DS_Store
```

- [ ] **Step 5: Crear `run.py`**

```python
from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
```

- [ ] **Step 6: Instalar dependencias**

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

- [ ] **Step 7: Commit**

```powershell
git add requirements.txt config.py .env.example .gitignore run.py
git commit -m "chore: add dependencies and base config"
```

---

## Task 3: App factory (stub)

**Files:**
- Modificar: `app/__init__.py`

- [ ] **Step 1: Escribir factory mínima**

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

    # Blueprints se registran en fases siguientes
    return app
```

- [ ] **Step 2: Verificar que Flask arranca**

```powershell
python -c "from app import create_app; app = create_app(); print('OK')"
```

Esperado: `OK`

- [ ] **Step 3: Commit**

```powershell
git add app/__init__.py
git commit -m "feat: add Flask app factory stub"
```

---

## Task 4: Supabase client singleton

**Files:**
- Crear: `app/utils/supabase_client.py`
- Crear: `tests/test_utils/test_supabase_client.py`

- [ ] **Step 1: Escribir test que falla**

```python
# tests/test_utils/test_supabase_client.py
import os
import pytest
from unittest.mock import patch, MagicMock


def test_get_data_client_returns_singleton():
    """get_data_client devuelve siempre la misma instancia."""
    mock = MagicMock()
    with patch('app.utils.supabase_client._data_client', mock):
        from app.utils.supabase_client import get_data_client
        c1 = get_data_client()
        c2 = get_data_client()
        assert c1 is c2


def test_get_auth_client_returns_singleton():
    """get_auth_client devuelve siempre la misma instancia."""
    mock = MagicMock()
    with patch('app.utils.supabase_client._auth_client', mock):
        from app.utils.supabase_client import get_auth_client
        c1 = get_auth_client()
        c2 = get_auth_client()
        assert c1 is c2
```

- [ ] **Step 2: Correr test — debe fallar**

```powershell
python -m pytest tests/test_utils/test_supabase_client.py -v
```

Esperado: `ERROR` — `ModuleNotFoundError`

- [ ] **Step 3: Implementar `supabase_client.py`**

```python
# app/utils/supabase_client.py
import os
from supabase import create_client, Client

_auth_client: Client | None = None
_data_client: Client | None = None


def get_auth_client() -> Client:
    """Cliente con anon key — solo para operaciones de Supabase Auth."""
    global _auth_client
    if _auth_client is None:
        _auth_client = create_client(
            os.environ['SUPABASE_URL'],
            os.environ['SUPABASE_ANON_KEY'],
        )
    return _auth_client


def get_data_client() -> Client:
    """Cliente con service key — operaciones de base de datos (bypasses RLS)."""
    global _data_client
    if _data_client is None:
        _data_client = create_client(
            os.environ['SUPABASE_URL'],
            os.environ['SUPABASE_SERVICE_KEY'],
        )
    return _data_client
```

- [ ] **Step 4: Correr test — debe pasar**

```powershell
python -m pytest tests/test_utils/test_supabase_client.py -v
```

Esperado: `2 passed`

- [ ] **Step 5: Commit**

```powershell
git add app/utils/supabase_client.py tests/test_utils/test_supabase_client.py
git commit -m "feat: add Supabase client singletons with tests"
```

---

## Task 5: Auth decoradores

**Files:**
- Crear: `app/utils/auth.py`
- Crear: `tests/test_utils/test_auth.py`

- [ ] **Step 1: Escribir tests que fallan**

```python
# tests/test_utils/test_auth.py
import pytest
from flask import Flask, session


def make_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'test-secret'
    app.config['TESTING'] = True
    return app


def test_login_required_redirects_when_no_session():
    app = make_app()
    from app.utils.auth import login_required

    @app.route('/protected')
    @login_required
    def protected():
        return 'OK'

    with app.test_client() as c:
        resp = c.get('/protected')
        assert resp.status_code == 302
        assert '/login' in resp.headers['Location']


def test_login_required_allows_authenticated():
    app = make_app()
    from app.utils.auth import login_required

    @app.route('/protected')
    @login_required
    def protected():
        return 'OK'

    with app.test_client() as c:
        with c.session_transaction() as sess:
            sess['user_id'] = 'abc-123'
        resp = c.get('/protected')
        assert resp.status_code == 200
        assert resp.data == b'OK'


def test_role_required_allows_correct_role():
    app = make_app()
    from app.utils.auth import login_required, role_required

    @app.route('/admin')
    @login_required
    @role_required('administrador')
    def admin_only():
        return 'ADMIN'

    with app.test_client() as c:
        with c.session_transaction() as sess:
            sess['user_id'] = 'abc-123'
            sess['rol'] = 'administrador'
        resp = c.get('/admin')
        assert resp.status_code == 200


def test_role_required_returns_403_for_wrong_role():
    app = make_app()
    from app.utils.auth import login_required, role_required

    @app.route('/admin')
    @login_required
    @role_required('administrador')
    def admin_only():
        return 'ADMIN'

    with app.test_client() as c:
        with c.session_transaction() as sess:
            sess['user_id'] = 'abc-123'
            sess['rol'] = 'operativo'
        resp = c.get('/admin')
        assert resp.status_code == 403
```

- [ ] **Step 2: Correr tests — deben fallar**

```powershell
python -m pytest tests/test_utils/test_auth.py -v
```

Esperado: `ERROR` — `ModuleNotFoundError`

- [ ] **Step 3: Implementar `auth.py`**

```python
# app/utils/auth.py
from functools import wraps
from flask import session, redirect, url_for, abort


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated


def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if session.get('rol') not in roles:
                abort(403)
            return f(*args, **kwargs)
        return decorated
    return decorator
```

- [ ] **Step 4: Correr tests — deben pasar**

```powershell
python -m pytest tests/test_utils/test_auth.py -v
```

Esperado: `4 passed`

- [ ] **Step 5: Correr toda la suite**

```powershell
python -m pytest tests/ -v
```

Esperado: `6 passed`

- [ ] **Step 6: Commit**

```powershell
git add app/utils/auth.py tests/test_utils/test_auth.py
git commit -m "feat: add login_required and role_required decorators with tests"
```

---

## Task 6: conftest.py para la suite completa

**Files:**
- Crear: `tests/conftest.py`

- [ ] **Step 1: Crear conftest**

```python
# tests/conftest.py
import pytest
from unittest.mock import MagicMock, patch
from app import create_app

TEST_CONFIG = {
    'TESTING': True,
    'SECRET_KEY': 'test-secret',
    'SUPABASE_URL': 'https://test.supabase.co',
    'SUPABASE_ANON_KEY': 'test-anon-key',
    'SUPABASE_SERVICE_KEY': 'test-service-key',
}


@pytest.fixture
def app():
    return create_app(TEST_CONFIG)


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def mock_data_client():
    """Mock del cliente de datos Supabase para todos los tests de modelos."""
    mock = MagicMock()
    with patch('app.utils.supabase_client._data_client', new=mock):
        yield mock


@pytest.fixture
def mock_auth_client():
    """Mock del cliente Auth Supabase."""
    mock = MagicMock()
    with patch('app.utils.supabase_client._auth_client', new=mock):
        yield mock


@pytest.fixture
def auth_session(client):
    """Sesión autenticada como administrador."""
    with client.session_transaction() as sess:
        sess['user_id'] = 'test-user-id'
        sess['rol'] = 'administrador'
        sess['nombre'] = 'Test Admin'
        sess['email'] = 'admin@test.com'
        sess['contrato_activo_id'] = 'test-contrato-id'
        sess['access_token'] = 'test-access-token'
        sess['refresh_token'] = 'test-refresh-token'
        sess['contratos_lista'] = [{'id': 'test-contrato-id', 'nombre': 'Contrato Test'}]
        sess['modulos_visibles'] = ['general', 'hitos', 'encuestas', 'instalaciones']
    return client


@pytest.fixture
def supervisor_session(client):
    """Sesión autenticada como supervisión."""
    with client.session_transaction() as sess:
        sess['user_id'] = 'supervisor-id'
        sess['rol'] = 'supervision'
        sess['nombre'] = 'Test Supervisor'
        sess['email'] = 'super@test.com'
        sess['contrato_activo_id'] = 'test-contrato-id'
        sess['access_token'] = 'test-access-token'
        sess['refresh_token'] = 'test-refresh-token'
        sess['contratos_lista'] = [{'id': 'test-contrato-id', 'nombre': 'Contrato Test'}]
        sess['modulos_visibles'] = ['general', 'hitos', 'encuestas']
    return client
```

- [ ] **Step 2: Correr toda la suite para verificar que conftest no rompe nada**

```powershell
python -m pytest tests/ -v
```

Esperado: `6 passed`

- [ ] **Step 3: Commit**

```powershell
git add tests/conftest.py
git commit -m "test: add shared pytest fixtures (conftest)"
```

---

## Verificación final de Fase 1

- [ ] **Correr suite completa**

```powershell
python -m pytest tests/ -v --tb=short
```

Esperado: `6 passed, 0 failed`

- [ ] **Verificar estructura de archivos**

```powershell
Get-ChildItem -Recurse -Name | Where-Object { $_ -notmatch '__pycache__|\.pyc|\.venv' }
```

Archivos que deben existir:
```
run.py
config.py
requirements.txt
.env.example
.gitignore
app/__init__.py
app/utils/__init__.py
app/utils/supabase_client.py
app/utils/auth.py
app/auth/__init__.py
app/dashboard/__init__.py
app/api/__init__.py
app/models/__init__.py
tests/__init__.py
tests/conftest.py
tests/test_utils/__init__.py
tests/test_utils/test_supabase_client.py
tests/test_utils/test_auth.py
tests/test_models/__init__.py
```

---

**Fase 1 completada. Continuar con Fase 2: Models.**
