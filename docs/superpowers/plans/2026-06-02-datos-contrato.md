# Datos del Contrato — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reconstruir la página Datos del Contrato sobre el esquema real de Supabase, consultando las tablas `contratos`, `contratos_prorrogas` y `contratos_adiciones`.

**Architecture:** Se añaden dos funciones al modelo (`get_prorrogas_resumen`, `get_adiciones_resumen`), se elimina `update_porcentaje_ejecutado` (campo inexistente en la DB), se actualiza la ruta `general()` para llamar a las tres consultas, y se reescribe el template con layout header + dos columnas + partes.

**Tech Stack:** Python 3.12, Flask, Jinja2, Supabase (supabase-py), pytest, unittest.mock. Sin nuevas dependencias.

---

## File Map

| Archivo | Acción |
|---|---|
| `app/models/contratos.py` | Modificar: añadir 2 funciones, eliminar 1 |
| `app/dashboard/routes.py` | Modificar: actualizar función `general()` |
| `app/templates/dashboard/general.html` | Reescribir completamente |
| `tests/test_models/test_contratos.py` | Modificar: actualizar fixture, añadir 4 tests, eliminar 1 |
| `tests/test_dashboard.py` | Modificar: actualizar fixture y assertions del test general |

---

## Task 1: Actualizar tests del modelo de contratos

**Files:**
- Modify: `tests/test_models/test_contratos.py`

- [ ] **Step 1: Reemplazar el contenido de `test_contratos.py`**

El archivo existente tiene fixtures con campos falsos (`porcentaje_ejecutado`) y un test de `update_porcentaje_ejecutado` que ya no tendrá función. Reemplazar el archivo completo:

```python
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
```

- [ ] **Step 2: Verificar que los tests nuevos fallan (funciones aún no existen)**

```bash
cd c:\Users\Victor Pulido\Documents\GIT\ORBIT_SERVIALCO_FLASK
.venv\Scripts\python -m pytest tests/test_models/test_contratos.py -v
```

Resultado esperado: `test_get_prorrogas_resumen_*` y `test_get_adiciones_resumen_*` fallan con `ImportError` o `AttributeError`. Los 4 tests existentes (`get_contrato`, `calcular_progreso_tiempo_*`) pasan.

- [ ] **Step 3: Commit del test actualizado**

```bash
git add tests/test_models/test_contratos.py
git commit -m "test: actualizar test_contratos al esquema real de Supabase"
```

---

## Task 2: Añadir funciones al modelo de contratos

**Files:**
- Modify: `app/models/contratos.py`

- [ ] **Step 1: Reemplazar el contenido completo de `contratos.py`**

```python
from datetime import date
from app.utils.supabase_client import get_data_client


def get_contrato(contrato_id: str) -> dict | None:
    client = get_data_client()
    if client is None:
        return None
    resp = (
        client.table('contratos')
        .select('*')
        .eq('id', contrato_id)
        .single()
        .execute()
    )
    return resp.data


def calcular_progreso_tiempo(
    fecha_inicio: date,
    fecha_fin: date,
    hoy: date | None = None,
) -> float:
    if hoy is None:
        hoy = date.today()
    if hoy <= fecha_inicio:
        return 0.0
    if hoy >= fecha_fin:
        return 100.0
    total = (fecha_fin - fecha_inicio).days
    transcurrido = (hoy - fecha_inicio).days
    return round((transcurrido / total) * 100, 1)


def get_prorrogas_resumen(contrato_id: str) -> dict:
    client = get_data_client()
    if client is None:
        return {'count': 0, 'plazo_actual': None}
    resp = (
        client.table('contratos_prorrogas')
        .select('numero, fecha_fin')
        .eq('contrato_id', contrato_id)
        .order('numero')
        .execute()
    )
    rows = resp.data or []
    ultima = rows[-1] if rows else None
    return {
        'count': len(rows),
        'plazo_actual': ultima['fecha_fin'] if ultima else None,
    }


def get_adiciones_resumen(contrato_id: str) -> dict:
    client = get_data_client()
    if client is None:
        return {'count': 0, 'valor_actual': None}
    resp = (
        client.table('contratos_adiciones')
        .select('numero, valor_actual')
        .eq('contrato_id', contrato_id)
        .order('numero')
        .execute()
    )
    rows = resp.data or []
    ultima = rows[-1] if rows else None
    return {
        'count': len(rows),
        'valor_actual': ultima['valor_actual'] if ultima else None,
    }
```

- [ ] **Step 2: Ejecutar tests del modelo — todos deben pasar**

```bash
.venv\Scripts\python -m pytest tests/test_models/test_contratos.py -v
```

Resultado esperado: 8 tests, todos `PASSED`.

- [ ] **Step 3: Commit**

```bash
git add app/models/contratos.py
git commit -m "feat: añadir get_prorrogas_resumen y get_adiciones_resumen, eliminar update_porcentaje_ejecutado"
```

---

## Task 3: Actualizar tests del dashboard

**Files:**
- Modify: `tests/test_dashboard.py`

- [ ] **Step 1: Reemplazar `CONTRATO_FIXTURE` y actualizar los tests que lo usan**

```python
import pytest
from unittest.mock import patch

CONTRATO_FIXTURE = {
    'id': 'test-contrato-id',
    'nombre': 'Contrato Fibra',
    'contratista': 'Empresa A SAS',
    'intrventoria': 'Interventores SA',
    'supervisor': 'Juan Perez',
    'fecha_inicio': '2024-01-01',
    'fecha_fin': '2025-12-31',
    'activo': True,
    'valor_contrato': 40700000,
    'plazo_actual': '2026-03-31',
    'prorrogas': 1,
    'adiciones': 1,
    'valor_actual': 45000000,
}

PRORROGAS_FIXTURE = {'count': 1, 'plazo_actual': '2026-03-31'}
ADICIONES_FIXTURE = {'count': 1, 'valor_actual': 45000000}


def test_general_redirects_to_login_when_not_authenticated(client):
    resp = client.get('/dashboard/general')
    assert resp.status_code == 302
    assert '/login' in resp.headers['Location']


def test_general_returns_200_when_authenticated(auth_session):
    with patch('app.dashboard.routes.get_contrato', return_value=CONTRATO_FIXTURE), \
         patch('app.dashboard.routes.get_prorrogas_resumen', return_value=PRORROGAS_FIXTURE), \
         patch('app.dashboard.routes.get_adiciones_resumen', return_value=ADICIONES_FIXTURE):
        resp = auth_session.get('/dashboard/general')
        assert resp.status_code == 200
        assert 'Contrato Fibra'.encode() in resp.data


def test_general_returns_403_if_module_not_visible(client):
    with client.session_transaction() as sess:
        sess['user_id'] = 'uid-1'
        sess['rol'] = 'operativo'
        sess['modulos_visibles'] = []
        sess['contrato_activo_id'] = 'c1'
    resp = client.get('/dashboard/general')
    assert resp.status_code == 403


def test_general_muestra_estado_vacio_sin_contrato(auth_session):
    with patch('app.dashboard.routes.get_contrato', return_value=None), \
         patch('app.dashboard.routes.get_prorrogas_resumen', return_value={'count': 0, 'plazo_actual': None}), \
         patch('app.dashboard.routes.get_adiciones_resumen', return_value={'count': 0, 'valor_actual': None}):
        resp = auth_session.get('/dashboard/general')
        assert resp.status_code == 200
        assert 'contrato activo'.encode() in resp.data.lower()


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

- [ ] **Step 2: Verificar que `test_general_returns_200_when_authenticated` falla (ruta aún sin actualizar)**

```bash
.venv\Scripts\python -m pytest tests/test_dashboard.py::test_general_returns_200_when_authenticated -v
```

Resultado esperado: `FAILED` — la ruta no acepta aún `get_prorrogas_resumen` como argumento patcheable porque no lo importa.

- [ ] **Step 3: Commit**

```bash
git add tests/test_dashboard.py
git commit -m "test: actualizar test_dashboard al esquema real y añadir test estado vacío"
```

---

## Task 4: Actualizar la ruta `general()` en el dashboard

**Files:**
- Modify: `app/dashboard/routes.py:1-31`

- [ ] **Step 1: Reemplazar el bloque de imports y la función `general()` en `routes.py`**

Reemplazar las líneas 1-31 (todo desde `from datetime import date` hasta el final de la función `general`):

```python
from datetime import date
from flask import render_template, session, abort
from app.dashboard import bp
from app.utils.auth import login_required
from app.models.contratos import (
    get_contrato,
    calcular_progreso_tiempo,
    get_prorrogas_resumen,
    get_adiciones_resumen,
)
from app.models.hitos import get_hitos


@bp.route('/dashboard/general')
@login_required
def general():
    if 'general' not in session.get('modulos_visibles', []):
        abort(403)

    contrato_id = session.get('contrato_activo_id')
    contrato = get_contrato(contrato_id) if contrato_id else None
    prorrogas = get_prorrogas_resumen(contrato_id) if contrato_id else {'count': 0, 'plazo_actual': None}
    adiciones = get_adiciones_resumen(contrato_id) if contrato_id else {'count': 0, 'valor_actual': None}

    progreso_tiempo = 0.0
    if contrato and contrato.get('fecha_inicio'):
        fecha_limite = contrato.get('plazo_actual') or contrato.get('fecha_fin')
        if fecha_limite:
            inicio = date.fromisoformat(str(contrato['fecha_inicio']))
            fin = date.fromisoformat(str(fecha_limite))
            progreso_tiempo = calcular_progreso_tiempo(inicio, fin)

    return render_template(
        'dashboard/general.html',
        contrato=contrato,
        prorrogas=prorrogas,
        adiciones=adiciones,
        progreso_tiempo=progreso_tiempo,
    )
```

El resto del archivo (rutas de hitos, encuestas, instalaciones, etc.) se deja intacto.

- [ ] **Step 2: Ejecutar los tests del dashboard — todos deben pasar**

```bash
.venv\Scripts\python -m pytest tests/test_dashboard.py -v
```

Resultado esperado: todos `PASSED`.

- [ ] **Step 3: Ejecutar la suite completa para verificar que no hay regresiones**

```bash
.venv\Scripts\python -m pytest -v
```

Resultado esperado: misma cantidad de tests que antes más los 4 nuevos, todos `PASSED`.

- [ ] **Step 4: Commit**

```bash
git add app/dashboard/routes.py
git commit -m "feat: actualizar ruta general() para consultar prorrogas y adiciones reales"
```

---

## Task 5: Reescribir el template `general.html`

**Files:**
- Modify: `app/templates/dashboard/general.html`

- [ ] **Step 1: Reemplazar el contenido completo del archivo**

```html
{% extends 'base.html' %}

{% block title %}Datos del Contrato — ORBIT SERVIALCO{% endblock %}
{% block breadcrumb %}Datos del Contrato{% endblock %}

{% block content %}

{% if not contrato %}
<div class="card" style="text-align:center; padding:3rem;">
  <p style="color:var(--color-text-muted);">No hay un contrato activo seleccionado.</p>
</div>
{% else %}

<!-- ── Encabezado ──────────────────────────────────────────── -->
<div class="card" style="margin-bottom:1.5rem;">

  <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:1rem;">
    <div>
      <div style="font-size:var(--text-xs); color:var(--color-text-muted); font-family:var(--font-mono); margin-bottom:0.25rem;">
        {{ contrato.id }}
      </div>
      <div style="font-size:var(--text-xl); font-weight:700; color:var(--color-text); line-height:1.3;">
        {{ contrato.nombre }}
      </div>
    </div>
    {% if contrato.activo %}
      <span class="badge badge--success">Activo</span>
    {% else %}
      <span class="badge badge--neutral">Inactivo</span>
    {% endif %}
  </div>

  {% set fecha_limite = contrato.plazo_actual or contrato.fecha_fin %}
  {% if contrato.fecha_inicio and fecha_limite %}
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
    <div style="display:flex; justify-content:space-between; font-size:var(--text-xs); color:var(--color-text-muted); margin-top:0.25rem;">
      <span>{{ contrato.fecha_inicio|date_col }}</span>
      <span>{{ fecha_limite|date_col }}</span>
    </div>
  </div>
  {% endif %}

</div>

<!-- ── Finanzas y Cronograma ───────────────────────────────── -->
<div class="progress-grid" style="margin-bottom:1.5rem;">

  <div class="card">
    <div class="kpi-card__label" style="margin-bottom:1.25rem;">Finanzas</div>

    <div style="margin-bottom:0.75rem;">
      <div class="kpi-card__label" style="text-transform:none; letter-spacing:0; font-weight:400; margin-bottom:0.2rem;">Valor original</div>
      <div style="font-size:var(--text-2xl); font-weight:700; color:var(--color-text);">{{ contrato.valor_contrato|currency_col }}</div>
    </div>

    <div style="font-size:var(--text-xs); color:var(--color-text-muted); padding:0.5rem 0; border-top:1px solid var(--color-border); border-bottom:1px solid var(--color-border); margin-bottom:0.75rem;">
      {% if adiciones.count > 0 %}
        + {{ adiciones.count }} adicion{% if adiciones.count != 1 %}es{% endif %} registradas
      {% else %}
        Sin adiciones registradas
      {% endif %}
    </div>

    <div>
      <div class="kpi-card__label" style="text-transform:none; letter-spacing:0; font-weight:400; margin-bottom:0.2rem;">Valor actual</div>
      <div style="font-size:var(--text-2xl); font-weight:700; color:var(--color-text);">
        {% if adiciones.valor_actual %}
          {{ adiciones.valor_actual|currency_col }}
        {% else %}
          {{ contrato.valor_contrato|currency_col }}
        {% endif %}
      </div>
    </div>
  </div>

  <div class="card">
    <div class="kpi-card__label" style="margin-bottom:1.25rem;">Cronograma</div>

    <div style="margin-bottom:0.75rem;">
      <div class="kpi-card__label" style="text-transform:none; letter-spacing:0; font-weight:400; margin-bottom:0.2rem;">Inicio</div>
      <div style="font-size:var(--text-2xl); font-weight:700; color:var(--color-text);">
        {% if contrato.fecha_inicio %}{{ contrato.fecha_inicio|date_col }}{% else %}—{% endif %}
      </div>
    </div>

    <div style="font-size:var(--text-xs); color:var(--color-text-muted); padding:0.5rem 0; border-top:1px solid var(--color-border); border-bottom:1px solid var(--color-border); margin-bottom:0.75rem;">
      {% if prorrogas.count > 0 %}
        + {{ prorrogas.count }} prorroga{% if prorrogas.count != 1 %}s{% endif %} registradas
      {% else %}
        Sin prorrogas registradas
      {% endif %}
    </div>

    <div>
      <div class="kpi-card__label" style="text-transform:none; letter-spacing:0; font-weight:400; margin-bottom:0.2rem;">Plazo actual</div>
      <div style="font-size:var(--text-2xl); font-weight:700; color:var(--color-text);">
        {% set fecha_plazo = contrato.plazo_actual or contrato.fecha_fin %}
        {% if fecha_plazo %}{{ fecha_plazo|date_col }}{% else %}—{% endif %}
      </div>
    </div>
  </div>

</div>

<!-- ── Partes ──────────────────────────────────────────────── -->
<div class="card">
  <div class="kpi-card__label" style="margin-bottom:1.25rem;">Partes</div>
  <div style="display:grid; grid-template-columns:repeat(3,1fr); gap:1.5rem;">

    <div>
      <div class="kpi-card__label" style="margin-bottom:0.375rem;">Contratista</div>
      <div style="font-size:var(--text-sm); font-weight:600; color:var(--color-text);">{{ contrato.contratista or '—' }}</div>
    </div>

    <div>
      <div class="kpi-card__label" style="margin-bottom:0.375rem;">Interventoria</div>
      <div style="font-size:var(--text-sm); font-weight:600; color:var(--color-text);">{{ contrato.intrventoria or '—' }}</div>
    </div>

    <div>
      <div class="kpi-card__label" style="margin-bottom:0.375rem;">Supervisor</div>
      <div style="font-size:var(--text-sm); font-weight:600; color:var(--color-text);">{{ contrato.supervisor or '—' }}</div>
    </div>

  </div>
</div>

{% endif %}
{% endblock %}
```

- [ ] **Step 2: Ejecutar la suite completa**

```bash
.venv\Scripts\python -m pytest -v
```

Resultado esperado: todos los tests `PASSED`, sin regresiones.

- [ ] **Step 3: Commit final**

```bash
git add app/templates/dashboard/general.html
git commit -m "feat: reescribir página Datos del Contrato sobre esquema real de Supabase"
```

---

## Self-Review

### Spec coverage

| Requisito del spec | Tarea que lo implementa |
|---|---|
| `get_prorrogas_resumen()` en modelo | Task 2 |
| `get_adiciones_resumen()` en modelo | Task 2 |
| Eliminar `update_porcentaje_ejecutado()` | Task 2 |
| Ruta usa `plazo_actual` con fallback a `fecha_fin` | Task 4 |
| Ruta pasa `prorrogas` y `adiciones` al template | Task 4 |
| Header card con nombre, id, badge activo | Task 5 |
| Barra de tiempo (solo avance de tiempo) | Task 5 |
| Bloque Finanzas: valor original / conector / valor actual | Task 5 |
| Bloque Cronograma: inicio / conector / plazo actual | Task 5 |
| Sección Partes: contratista, interventoría, supervisor | Task 5 |
| Estado vacío sin contrato activo | Task 3 (test) + Task 5 (template) |
| `supervisor` null muestra `—` | Task 5 |
| `adiciones = 0` muestra "Sin adiciones registradas" | Task 5 |
| `prorrogas = 0` muestra "Sin prorrogas registradas" | Task 5 |
| Sin CSS nuevo (solo clases existentes) | Task 5 — solo usa `.card`, `.progress-wrap`, `.progress-grid`, `.badge`, `.kpi-card__label` |

### Consistencia de tipos

- `get_prorrogas_resumen` devuelve `{'count': int, 'plazo_actual': str | None}` — usado así en la ruta (Task 4) y en el template (Task 5).
- `get_adiciones_resumen` devuelve `{'count': int, 'valor_actual': int | None}` — usado así en la ruta y template.
- Firma de `calcular_progreso_tiempo` no cambia — los tests existentes siguen funcionando.
- `prorrogas` e `adiciones` como nombres de variable en la ruta y en el template son consistentes.
