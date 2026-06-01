# Gestión de Contratos — Plan Fase 5: Dashboard Modules

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Prerequisito:** Fase 4 completada. `31 passed` en la suite de tests.

**Goal:** Rutas y templates completos para los 4 módulos del dashboard (General, Hitos, Encuestas, Instalaciones). Las tablas de Encuestas e Instalaciones se cargan vía HTMX desde los endpoints de Fase 6.

**Fases del proyecto:**
- ✅ Fase 1–4 completadas
- ✅ **Fase 5** — Dashboard modules ← estás aquí
- Fase 6 — HTMX API endpoints
- Fase 7 — SQL Migration + smoke test

---

## File Map (esta fase)

| Archivo | Responsabilidad |
|---|---|
| `app/dashboard/__init__.py` | Blueprint `dashboard` |
| `app/dashboard/routes.py` | general, hitos, encuestas, instalaciones views |
| `app/__init__.py` | Registra dashboard blueprint + filtros Jinja2 |
| `app/templates/dashboard/general.html` | KPI cards + barras de progreso |
| `app/templates/dashboard/hitos.html` | Tabla hitos + cambio estado inline + comentarios |
| `app/templates/dashboard/encuestas.html` | Frame filtros + tabla cargada por HTMX |
| `app/templates/dashboard/instalaciones.html` | Idéntico a encuestas |
| `tests/test_dashboard.py` | Tests de rutas dashboard |

---

## Task 18: Dashboard blueprint + rutas + filtros Jinja2

**Files:**
- Modificar: `app/dashboard/__init__.py`
- Crear: `app/dashboard/routes.py`
- Modificar: `app/__init__.py`

- [ ] **Step 1: Escribir tests que fallan**

```python
# tests/test_dashboard.py
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
        sess['modulos_visibles'] = []   # sin acceso
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
```

- [ ] **Step 2: Correr tests — deben fallar**

```powershell
python -m pytest tests/test_dashboard.py -v
```

Esperado: `ERROR` — blueprint no registrado

- [ ] **Step 3: Definir blueprint en `app/dashboard/__init__.py`**

```python
# app/dashboard/__init__.py
from flask import Blueprint

bp = Blueprint('dashboard', __name__)

from app.dashboard import routes  # noqa: E402,F401
```

- [ ] **Step 4: Crear `app/dashboard/routes.py`**

```python
# app/dashboard/routes.py
from datetime import date
from flask import render_template, session, abort
from app.dashboard import bp
from app.utils.auth import login_required
from app.models.contratos import get_contrato, calcular_progreso_tiempo
from app.models.hitos import get_hitos


@bp.route('/dashboard/general')
@login_required
def general():
    if 'general' not in session.get('modulos_visibles', []):
        abort(403)

    contrato_id = session.get('contrato_activo_id')
    contrato = get_contrato(contrato_id) if contrato_id else None

    progreso_tiempo = 0.0
    if contrato and contrato.get('fecha_inicio') and contrato.get('fecha_fin'):
        inicio = date.fromisoformat(str(contrato['fecha_inicio']))
        fin = date.fromisoformat(str(contrato['fecha_fin']))
        progreso_tiempo = calcular_progreso_tiempo(inicio, fin)

    progreso_ejecutado = float(contrato.get('porcentaje_ejecutado', 0)) if contrato else 0.0

    return render_template(
        'dashboard/general.html',
        contrato=contrato,
        progreso_tiempo=progreso_tiempo,
        progreso_ejecutado=progreso_ejecutado,
    )


@bp.route('/dashboard/hitos')
@login_required
def hitos():
    if 'hitos' not in session.get('modulos_visibles', []):
        abort(403)

    contrato_id = session.get('contrato_activo_id')
    hitos_list = get_hitos(contrato_id) if contrato_id else []

    return render_template('dashboard/hitos.html', hitos=hitos_list)


@bp.route('/dashboard/encuestas')
@login_required
def encuestas():
    if 'encuestas' not in session.get('modulos_visibles', []):
        abort(403)
    return render_template('dashboard/encuestas.html')


@bp.route('/dashboard/instalaciones')
@login_required
def instalaciones():
    if 'instalaciones' not in session.get('modulos_visibles', []):
        abort(403)
    return render_template('dashboard/instalaciones.html')
```

- [ ] **Step 5: Actualizar `app/__init__.py` — registrar dashboard + filtros**

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

    # ── Blueprints ─────────────────────────────────────────
    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp)

    from app.dashboard import bp as dashboard_bp
    app.register_blueprint(dashboard_bp)

    # ── Ruta raíz ──────────────────────────────────────────
    from flask import session, redirect, url_for

    @app.route('/')
    def index():
        if 'user_id' in session:
            return redirect(url_for('dashboard.general'))
        return redirect(url_for('auth.login'))

    # ── Context processor ──────────────────────────────────
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

    # ── Filtros Jinja2 ─────────────────────────────────────
    @app.template_filter('currency_col')
    def currency_col(value):
        if value is None:
            return 'N/A'
        try:
            v = float(value)
        except (TypeError, ValueError):
            return str(value)
        if v >= 1_000_000_000:
            return f'${v / 1_000_000_000:,.2f} milM'
        if v >= 1_000_000:
            return f'${v / 1_000_000:,.2f} M'
        return f'${v:,.0f}'

    @app.template_filter('date_col')
    def date_col(value):
        if not value:
            return '—'
        from datetime import date
        if isinstance(value, str):
            try:
                value = date.fromisoformat(value)
            except ValueError:
                return value
        return value.strftime('%d/%m/%Y')

    @app.template_filter('progress_color')
    def progress_color(value):
        try:
            v = float(value)
        except (TypeError, ValueError):
            return 'neutral'
        if v >= 50:
            return 'success'
        if v >= 20:
            return 'warning'
        return 'danger'

    return app
```

- [ ] **Step 6: Correr tests — deben pasar**

```powershell
python -m pytest tests/test_dashboard.py -v
```

Esperado: `9 passed`

- [ ] **Step 7: Suite completa**

```powershell
python -m pytest tests/ -v --tb=short
```

Esperado: `40 passed, 0 failed`

- [ ] **Step 8: Commit**

```powershell
git add app/dashboard/__init__.py app/dashboard/routes.py app/__init__.py tests/test_dashboard.py
git commit -m "feat: add dashboard blueprint with general/hitos/encuestas/instalaciones routes and Jinja2 filters"
```

---

## Task 19: Template general.html

**Files:**
- Crear: `app/templates/dashboard/general.html`

- [ ] **Step 1: Crear template**

```html
<!-- app/templates/dashboard/general.html -->
{% extends 'base.html' %}

{% block title %}Datos del Contrato — ORBIT SERVIALCO{% endblock %}
{% block breadcrumb %}Datos del Contrato{% endblock %}

{% block content %}

{% if not contrato %}
<div class="card" style="text-align:center; padding:3rem;">
  <p class="text-muted">No hay un contrato activo seleccionado.</p>
</div>
{% else %}

<!-- ── Barras de progreso ──────────────────────────────────── -->
<div class="progress-grid" style="margin-bottom:1.5rem;">

  <div class="card card--compact">
    <div class="progress-wrap">
      <div class="progress-wrap__header">
        <span style="font-weight:600;">Avance de tiempo</span>
        <span style="font-size:var(--text-lg); font-weight:700; color:var(--color-{{ progreso_tiempo|progress_color }});">
          {{ progreso_tiempo }}%
        </span>
      </div>
      <div class="progress-track">
        <div class="progress-bar progress-bar--{{ progreso_tiempo|progress_color }}"
             style="width:{{ progreso_tiempo }}%;"></div>
      </div>
      <div style="display:flex;justify-content:space-between;font-size:var(--text-xs);color:var(--color-text-muted);">
        <span>{{ contrato.fecha_inicio|date_col }}</span>
        <span>{{ contrato.fecha_fin|date_col }}</span>
      </div>
    </div>
  </div>

  <div class="card card--compact">
    <div class="progress-wrap">
      <div class="progress-wrap__header">
        <span style="font-weight:600;">Ejecución del contrato</span>
        <span style="font-size:var(--text-lg); font-weight:700; color:var(--color-{{ progreso_ejecutado|progress_color }});">
          {{ progreso_ejecutado }}%
        </span>
      </div>
      <div class="progress-track">
        <div class="progress-bar progress-bar--{{ progreso_ejecutado|progress_color }}"
             style="width:{{ progreso_ejecutado }}%;"></div>
      </div>
      {% if current_user_rol in ['administrador', 'supervision'] %}
      <form style="display:flex;gap:.5rem;margin-top:.5rem;"
            hx-post="/api/contratos/ejecutado"
            hx-swap="none"
            hx-on::after-request="window.location.reload()">
        <input type="number" name="porcentaje" min="0" max="100" step="0.1"
               value="{{ progreso_ejecutado }}"
               class="form-input"
               style="width:90px;"
               placeholder="%">
        <button type="submit" class="btn btn--ghost btn--sm">Actualizar</button>
      </form>
      {% endif %}
    </div>
  </div>

</div>

<!-- ── Tarjetas KPI ────────────────────────────────────────── -->
<div class="kpi-grid">

  <div class="kpi-card">
    <div class="kpi-card__label">Valor del contrato</div>
    <div class="kpi-card__value">{{ contrato.valor_contrato|currency_col }}</div>
  </div>

  <div class="kpi-card">
    <div class="kpi-card__label">Plazo</div>
    <div class="kpi-card__value">{{ contrato.plazo_meses or '—' }}</div>
    <div class="kpi-card__sub">meses</div>
  </div>

  <div class="kpi-card">
    <div class="kpi-card__label">Fecha inicio</div>
    <div class="kpi-card__value" style="font-size:var(--text-xl);">{{ contrato.fecha_inicio|date_col }}</div>
  </div>

  <div class="kpi-card">
    <div class="kpi-card__label">Fecha fin</div>
    <div class="kpi-card__value" style="font-size:var(--text-xl);">{{ contrato.fecha_fin|date_col }}</div>
  </div>

</div>

<!-- ── Actores y localización ─────────────────────────────── -->
<div class="kpi-grid">

  <div class="kpi-card">
    <div class="kpi-card__label">Entidad contratante</div>
    <div class="kpi-card__value" style="font-size:var(--text-base); font-weight:600;">
      {{ contrato.entidad_contratante or '—' }}
    </div>
  </div>

  <div class="kpi-card">
    <div class="kpi-card__label">Contratista</div>
    <div class="kpi-card__value" style="font-size:var(--text-base); font-weight:600;">
      {{ contrato.nombre_contratista or '—' }}
    </div>
  </div>

  <div class="kpi-card">
    <div class="kpi-card__label">Interventoría</div>
    <div class="kpi-card__value" style="font-size:var(--text-base); font-weight:600;">
      {{ contrato.nombre_interventoria or '—' }}
    </div>
  </div>

  <div class="kpi-card">
    <div class="kpi-card__label">Localización</div>
    <div class="kpi-card__value" style="font-size:var(--text-base); font-weight:600;">
      {{ contrato.localizacion or '—' }}
    </div>
  </div>

</div>

<!-- ── Objeto del contrato ────────────────────────────────── -->
<div class="card" style="margin-top:1rem;">
  <div style="font-size:var(--text-xs);font-weight:700;letter-spacing:.05em;text-transform:uppercase;color:var(--color-text-muted);margin-bottom:.5rem;">
    Objeto del contrato
  </div>
  <p style="font-size:var(--text-sm);line-height:1.7;">{{ contrato.objeto or 'Sin descripción.' }}</p>
</div>

{% endif %}
{% endblock %}
```

- [ ] **Step 2: Verificar que el template renderiza sin errores**

```powershell
python -m pytest tests/test_dashboard.py::test_general_returns_200_when_authenticated -v
```

Esperado: `1 passed`

- [ ] **Step 3: Commit**

```powershell
git add app/templates/dashboard/general.html
git commit -m "feat: add general dashboard template with KPI cards and progress bars"
```

---

## Task 20: Template hitos.html

**Files:**
- Crear: `app/templates/dashboard/hitos.html`

- [ ] **Step 1: Crear template**

```html
<!-- app/templates/dashboard/hitos.html -->
{% extends 'base.html' %}

{% block title %}Hitos — ORBIT SERVIALCO{% endblock %}
{% block breadcrumb %}Hitos{% endblock %}

{% block content %}

<div class="page-header">
  <h1 class="page-header__title">Hitos del Contrato</h1>
  <p class="page-header__sub">Entregables y su estado de aprobación</p>
</div>

<div class="table-wrap">
  {% if hitos %}
  <table>
    <thead>
      <tr>
        <th>Nombre</th>
        <th>Descripción</th>
        <th>Fecha límite</th>
        <th>Estado</th>
        <th>Archivo</th>
        {% if current_user_rol in ['administrador', 'supervision'] %}
        <th>Cambiar estado</th>
        {% endif %}
        <th>Comentarios</th>
      </tr>
    </thead>
    <tbody>
      {% for hito in hitos %}
      <tr>
        <td style="font-weight:500;">{{ hito.nombre }}</td>
        <td class="text-muted text-sm">{{ hito.descripcion or '—' }}</td>
        <td>{{ hito.fecha_limite|date_col }}</td>
        <td>
          <span id="badge-hito-{{ hito.id }}"
                class="badge badge--{{ 'success' if hito.estado == 'aprobado' else ('warning' if hito.estado == 'en_revision' else 'neutral') }}">
            {{ {'pendiente':'Pendiente','en_revision':'En revisión','aprobado':'Aprobado'}.get(hito.estado, hito.estado) }}
          </span>
        </td>
        <td>
          {% if hito.archivo_url %}
          <a href="{{ hito.archivo_url }}" target="_blank" rel="noopener" class="btn btn--ghost btn--sm">
            📎 Ver
          </a>
          {% else %}
          <span class="text-muted text-sm">—</span>
          {% endif %}
        </td>
        {% if current_user_rol in ['administrador', 'supervision'] %}
        <td>
          <select class="form-select"
                  style="width:auto;padding:.25rem .5rem;font-size:var(--text-xs);"
                  hx-patch="/api/hitos/{{ hito.id }}/estado"
                  hx-trigger="change"
                  hx-target="#badge-hito-{{ hito.id }}"
                  hx-swap="outerHTML"
                  onclick="event.stopPropagation()">
            <option value="pendiente"    {% if hito.estado == 'pendiente' %}selected{% endif %}>Pendiente</option>
            <option value="en_revision"  {% if hito.estado == 'en_revision' %}selected{% endif %}>En revisión</option>
            <option value="aprobado"     {% if hito.estado == 'aprobado' %}selected{% endif %}>Aprobado</option>
          </select>
        </td>
        {% endif %}
        <td>
          <button class="btn btn--ghost btn--sm"
                  hx-get="/api/comentarios?tipo=hito&ref={{ hito.id }}&contrato_id={{ contrato_activo_id }}"
                  hx-target="#comments-panel-content"
                  hx-swap="innerHTML"
                  hx-on::after-request="document.getElementById('comments-section').style.display=''">
            💬
          </button>
        </td>
      </tr>
      {% endfor %}
    </tbody>
  </table>
  {% else %}
  <div style="padding:3rem;text-align:center;color:var(--color-text-muted);">
    No hay hitos registrados para este contrato.
  </div>
  {% endif %}
</div>

<!-- Panel de comentarios (cargado por HTMX) -->
<div id="comments-section" class="card" style="margin-top:1rem;display:none;">
  <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:1rem;">
    <h3 style="font-size:var(--text-base);font-weight:600;">Comentarios del hito</h3>
    <button class="btn btn--ghost btn--sm"
            onclick="document.getElementById('comments-section').style.display='none'">
      ✕ Cerrar
    </button>
  </div>
  <div id="comments-panel-content"></div>
</div>

{% endblock %}
```

- [ ] **Step 2: Verificar que el template renderiza**

```powershell
python -m pytest tests/test_dashboard.py::test_hitos_returns_200_when_authenticated -v
```

Esperado: `1 passed`

- [ ] **Step 3: Commit**

```powershell
git add app/templates/dashboard/hitos.html
git commit -m "feat: add hitos template with inline state change and comments panel"
```

---

## Task 21: Templates encuestas.html e instalaciones.html

**Files:**
- Crear: `app/templates/dashboard/encuestas.html`
- Crear: `app/templates/dashboard/instalaciones.html`

- [ ] **Step 1: Crear `encuestas.html`**

```html
<!-- app/templates/dashboard/encuestas.html -->
{% extends 'base.html' %}

{% block title %}Encuestas — ORBIT SERVIALCO{% endblock %}
{% block breadcrumb %}Encuestas{% endblock %}

{% block content %}

<div class="page-header">
  <h1 class="page-header__title">Registros de Encuestas</h1>
  <p class="page-header__sub">Datos del contrato activo</p>
</div>

<!-- Frame de filtros -->
<form id="filtros-encuestas" class="filters-frame"
      hx-get="/api/encuestas"
      hx-target="#tabla-encuestas-wrap"
      hx-trigger="submit, change delay:500ms"
      hx-include="this">

  <div class="form-group">
    <label class="form-label">Buscar</label>
    <input type="text" name="q" class="form-input" placeholder="Texto libre…">
  </div>

  <div class="form-group">
    <label class="form-label">Desde</label>
    <input type="date" name="fecha_desde" class="form-input">
  </div>

  <div class="form-group">
    <label class="form-label">Hasta</label>
    <input type="date" name="fecha_hasta" class="form-input">
  </div>

  <div style="align-self:flex-end;">
    <button type="submit" class="btn btn--primary">Filtrar</button>
    <button type="reset"  class="btn btn--ghost"
            hx-get="/api/encuestas"
            hx-target="#tabla-encuestas-wrap"
            hx-trigger="click">
      Limpiar
    </button>
  </div>
</form>

<!-- Tabla cargada por HTMX -->
<div id="tabla-encuestas-wrap"
     class="table-wrap"
     hx-get="/api/encuestas?page=1"
     hx-trigger="load"
     hx-indicator="#tabla-encuestas-wrap">
  <div style="padding:2rem;text-align:center;color:var(--color-text-muted);">
    Cargando registros…
  </div>
</div>

<!-- Panel de comentarios -->
<div id="comments-section" class="card" style="margin-top:1rem;display:none;">
  <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:1rem;">
    <h3 style="font-size:var(--text-base);font-weight:600;">Anotaciones del registro</h3>
    <button class="btn btn--ghost btn--sm"
            onclick="document.getElementById('comments-section').style.display='none'">
      ✕ Cerrar
    </button>
  </div>
  <div id="comments-panel-content"></div>
</div>

{% endblock %}
```

- [ ] **Step 2: Crear `instalaciones.html`** (estructura idéntica, solo cambia el endpoint y los textos)

```html
<!-- app/templates/dashboard/instalaciones.html -->
{% extends 'base.html' %}

{% block title %}Instalaciones — ORBIT SERVIALCO{% endblock %}
{% block breadcrumb %}Instalaciones{% endblock %}

{% block content %}

<div class="page-header">
  <h1 class="page-header__title">Registros de Instalaciones</h1>
  <p class="page-header__sub">Datos del contrato activo</p>
</div>

<!-- Frame de filtros -->
<form id="filtros-instalaciones" class="filters-frame"
      hx-get="/api/instalaciones"
      hx-target="#tabla-instalaciones-wrap"
      hx-trigger="submit, change delay:500ms"
      hx-include="this">

  <div class="form-group">
    <label class="form-label">Buscar</label>
    <input type="text" name="q" class="form-input" placeholder="Texto libre…">
  </div>

  <div class="form-group">
    <label class="form-label">Desde</label>
    <input type="date" name="fecha_desde" class="form-input">
  </div>

  <div class="form-group">
    <label class="form-label">Hasta</label>
    <input type="date" name="fecha_hasta" class="form-input">
  </div>

  <div style="align-self:flex-end;">
    <button type="submit" class="btn btn--primary">Filtrar</button>
    <button type="reset" class="btn btn--ghost"
            hx-get="/api/instalaciones"
            hx-target="#tabla-instalaciones-wrap"
            hx-trigger="click">
      Limpiar
    </button>
  </div>
</form>

<!-- Tabla cargada por HTMX -->
<div id="tabla-instalaciones-wrap"
     class="table-wrap"
     hx-get="/api/instalaciones?page=1"
     hx-trigger="load"
     hx-indicator="#tabla-instalaciones-wrap">
  <div style="padding:2rem;text-align:center;color:var(--color-text-muted);">
    Cargando registros…
  </div>
</div>

<!-- Panel de comentarios -->
<div id="comments-section" class="card" style="margin-top:1rem;display:none;">
  <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:1rem;">
    <h3 style="font-size:var(--text-base);font-weight:600;">Anotaciones del registro</h3>
    <button class="btn btn--ghost btn--sm"
            onclick="document.getElementById('comments-section').style.display='none'">
      ✕ Cerrar
    </button>
  </div>
  <div id="comments-panel-content"></div>
</div>

{% endblock %}
```

- [ ] **Step 3: Verificar que ambos templates renderizan**

```powershell
python -m pytest tests/test_dashboard.py::test_encuestas_returns_200_when_authenticated tests/test_dashboard.py::test_instalaciones_returns_200_when_authenticated -v
```

Esperado: `2 passed`

- [ ] **Step 4: Suite completa**

```powershell
python -m pytest tests/ -v --tb=short
```

Esperado: `40 passed, 0 failed`

- [ ] **Step 5: Commit**

```powershell
git add app/templates/dashboard/encuestas.html app/templates/dashboard/instalaciones.html
git commit -m "feat: add encuestas and instalaciones templates with HTMX filter frames"
```

---

## Verificación final de Fase 5

- [ ] **Suite completa**

```powershell
python -m pytest tests/ -v --tb=short
```

Esperado: `40 passed, 0 failed`

- [ ] **Verificar todas las rutas registradas**

```powershell
python -c "
from app import create_app
app = create_app()
rutas = [str(r) for r in app.url_map.iter_rules()]
for r in sorted(rutas): print(r)
"
```

Debe listar: `/`, `/login`, `/logout`, `/cambiar-contrasena`, `/dashboard/general`, `/dashboard/hitos`, `/dashboard/encuestas`, `/dashboard/instalaciones`

---

**Fase 5 completada. Continuar con Fase 6: HTMX API endpoints.**
