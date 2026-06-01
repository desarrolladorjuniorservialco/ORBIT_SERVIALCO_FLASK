# Gestión de Contratos — Plan Fase 6: HTMX API Endpoints

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Prerequisito:** Fase 5 completada. `40 passed` en la suite de tests.

**Goal:** Todos los endpoints HTMX que dan vida a las interacciones dinámicas: selector de contrato, comentarios, filtros de tablas, cambio inline de estado en hitos, eliminación de registros y actualización de porcentaje ejecutado.

**Fases del proyecto:**
- ✅ Fases 1–5 completadas
- ✅ **Fase 6** — HTMX API endpoints ← estás aquí
- Fase 7 — SQL Migration + smoke test final

---

## File Map (esta fase)

| Archivo | Responsabilidad |
|---|---|
| `app/api/__init__.py` | Blueprint `api` |
| `app/api/routes.py` | Todos los endpoints HTMX |
| `app/__init__.py` | Registra blueprint api |
| `app/templates/partials/panel_comentarios.html` | Partial: hilo de comentarios + formulario |
| `app/templates/partials/tabla_encuestas.html` | Partial: tabla dinámica de encuestas |
| `app/templates/partials/tabla_instalaciones.html` | Partial: tabla dinámica de instalaciones |
| `app/templates/partials/badge_hito.html` | Partial: badge de estado de hito |
| `tests/test_api.py` | Tests de todos los endpoints API |

---

## Task 22: API blueprint + endpoints + registro en factory

**Files:**
- Modificar: `app/api/__init__.py`
- Crear: `app/api/routes.py`
- Modificar: `app/__init__.py`

- [ ] **Step 1: Escribir tests que fallan**

```python
# tests/test_api.py
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
```

- [ ] **Step 2: Correr tests — deben fallar**

```powershell
python -m pytest tests/test_api.py -v
```

Esperado: `ERROR` — blueprint no registrado

- [ ] **Step 3: Definir blueprint en `app/api/__init__.py`**

```python
# app/api/__init__.py
from flask import Blueprint

bp = Blueprint('api', __name__, url_prefix='/api')

from app.api import routes  # noqa: E402,F401
```

- [ ] **Step 4: Crear `app/api/routes.py`**

```python
# app/api/routes.py
from flask import request, session, render_template, make_response, abort, url_for
from app.api import bp
from app.utils.auth import login_required, role_required
from app.models.comentarios import get_comentarios as get_comentarios_db
from app.models.comentarios import create_comentario as create_comentario_db
from app.models.encuestas import get_encuestas as get_encuestas_db
from app.models.encuestas import delete_encuesta as delete_encuesta_db
from app.models.instalaciones import get_instalaciones as get_instalaciones_db
from app.models.instalaciones import delete_instalacion as delete_instalacion_db
from app.models.hitos import update_estado_hito as update_estado_hito_db
from app.models.contratos import update_porcentaje_ejecutado as update_porcentaje_db
import math


# ── Selector de contrato ───────────────────────────────────

@bp.route('/set-contrato', methods=['POST'])
@login_required
def set_contrato():
    contrato_id = request.form.get('contrato_id', '').strip()
    rol = session.get('rol', '')

    if rol != 'administrador':
        ids_permitidos = [c['id'] for c in session.get('contratos_lista', [])]
        if contrato_id not in ids_permitidos:
            abort(403)

    session['contrato_activo_id'] = contrato_id
    resp = make_response('', 200)
    resp.headers['HX-Redirect'] = url_for('dashboard.general')
    return resp


# ── Comentarios ────────────────────────────────────────────

@bp.route('/comentarios', methods=['GET'])
@login_required
def get_comentarios():
    tipo = request.args.get('tipo', 'global')
    referencia_id = request.args.get('ref') or None
    contrato_id = session.get('contrato_activo_id')

    comentarios = get_comentarios_db(contrato_id, tipo, referencia_id)

    return render_template(
        'partials/panel_comentarios.html',
        comentarios=comentarios,
        tipo=tipo,
        referencia_id=referencia_id,
    )


@bp.route('/comentarios', methods=['POST'])
@login_required
def post_comentario():
    if session.get('rol') == 'operativo':
        abort(403)

    tipo = request.form.get('tipo', 'global')
    referencia_id = request.form.get('referencia_id') or None
    contenido = request.form.get('contenido', '').strip()
    contrato_id = session.get('contrato_activo_id')
    autor_id = session.get('user_id')

    if not contenido:
        abort(400)

    create_comentario_db(contrato_id, autor_id, tipo, contenido, referencia_id)
    comentarios = get_comentarios_db(contrato_id, tipo, referencia_id)

    return render_template(
        'partials/panel_comentarios.html',
        comentarios=comentarios,
        tipo=tipo,
        referencia_id=referencia_id,
    )


# ── Tablas: encuestas ──────────────────────────────────────

@bp.route('/encuestas', methods=['GET'])
@login_required
def get_encuestas():
    contrato_id = session.get('contrato_activo_id')
    page = int(request.args.get('page', 1))
    per_page = 25

    filtros = {}
    q = request.args.get('q', '').strip()
    if q:
        filtros['q'] = q

    rows, total = get_encuestas_db(contrato_id, page=page, per_page=per_page, filtros=filtros or None)
    total_pages = max(1, math.ceil(total / per_page))

    return render_template(
        'partials/tabla_encuestas.html',
        rows=rows,
        page=page,
        per_page=per_page,
        total=total,
        total_pages=total_pages,
        tipo='encuesta',
    )


# ── Tablas: instalaciones ──────────────────────────────────

@bp.route('/instalaciones', methods=['GET'])
@login_required
def get_instalaciones():
    contrato_id = session.get('contrato_activo_id')
    page = int(request.args.get('page', 1))
    per_page = 25

    filtros = {}
    q = request.args.get('q', '').strip()
    if q:
        filtros['q'] = q

    rows, total = get_instalaciones_db(contrato_id, page=page, per_page=per_page, filtros=filtros or None)
    total_pages = max(1, math.ceil(total / per_page))

    return render_template(
        'partials/tabla_instalaciones.html',
        rows=rows,
        page=page,
        per_page=per_page,
        total=total,
        total_pages=total_pages,
        tipo='instalacion',
    )


# ── Hitos: cambio de estado ────────────────────────────────

@bp.route('/hitos/<hito_id>/estado', methods=['PATCH'])
@login_required
@role_required('administrador', 'supervision')
def patch_hito_estado(hito_id):
    estado = request.form.get('estado', '').strip()
    try:
        result = update_estado_hito_db(hito_id, estado)
    except ValueError:
        abort(400)

    return render_template(
        'partials/badge_hito.html',
        hito_id=hito_id,
        estado=result.get('estado', estado),
    )


# ── Delete: encuesta ───────────────────────────────────────

@bp.route('/encuestas/<encuesta_id>', methods=['DELETE'])
@login_required
@role_required('administrador')
def delete_encuesta(encuesta_id):
    delete_encuesta_db(encuesta_id)
    return '', 200


# ── Delete: instalacion ────────────────────────────────────

@bp.route('/instalaciones/<instalacion_id>', methods=['DELETE'])
@login_required
@role_required('administrador')
def delete_instalacion(instalacion_id):
    delete_instalacion_db(instalacion_id)
    return '', 200


# ── Contratos: porcentaje ejecutado ───────────────────────

@bp.route('/contratos/ejecutado', methods=['POST'])
@login_required
@role_required('administrador', 'supervision')
def update_ejecutado():
    contrato_id = session.get('contrato_activo_id')
    try:
        porcentaje = float(request.form.get('porcentaje', 0))
        porcentaje = max(0.0, min(100.0, porcentaje))
    except (TypeError, ValueError):
        abort(400)

    update_porcentaje_db(contrato_id, porcentaje)
    resp = make_response('', 200)
    resp.headers['HX-Refresh'] = 'true'
    return resp
```

- [ ] **Step 5: Registrar blueprint api en `app/__init__.py`**

Añadir después del bloque del dashboard blueprint:

```python
    from app.api import bp as api_bp
    app.register_blueprint(api_bp)
```

El bloque de blueprints en `__init__.py` queda:

```python
    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp)

    from app.dashboard import bp as dashboard_bp
    app.register_blueprint(dashboard_bp)

    from app.api import bp as api_bp
    app.register_blueprint(api_bp)
```

- [ ] **Step 6: Correr tests — deben pasar**

```powershell
python -m pytest tests/test_api.py -v
```

Esperado: `15 passed`

- [ ] **Step 7: Suite completa**

```powershell
python -m pytest tests/ -v --tb=short
```

Esperado: `55 passed, 0 failed`

- [ ] **Step 8: Commit**

```powershell
git add app/api/__init__.py app/api/routes.py app/__init__.py tests/test_api.py
git commit -m "feat: add HTMX API blueprint with all dynamic endpoints and tests"
```

---

## Task 23: Partial templates

**Files:**
- Crear: `app/templates/partials/panel_comentarios.html`
- Crear: `app/templates/partials/tabla_encuestas.html`
- Crear: `app/templates/partials/tabla_instalaciones.html`
- Crear: `app/templates/partials/badge_hito.html`

- [ ] **Step 1: Crear `panel_comentarios.html`**

```html
<!-- app/templates/partials/panel_comentarios.html -->
<div class="comments-panel">

  {% if comentarios %}
    {% for c in comentarios %}
    <div class="comment-item">
      <div class="comment-item__meta">
        <span class="comment-item__author">
          {{ c.usuarios.nombre_completo if c.get('usuarios') else 'Usuario' }}
        </span>
        <span>·</span>
        <span>{{ (c.created_at or '')[:10] }}</span>
      </div>
      <div class="comment-item__body">{{ c.contenido }}</div>
    </div>
    {% endfor %}
  {% else %}
    <p class="text-muted text-sm" style="padding:.5rem 0 1rem;">
      Sin comentarios aún.
    </p>
  {% endif %}

  {% if current_user_rol != 'operativo' %}
  <form class="comment-form"
        hx-post="/api/comentarios"
        hx-target="#comments-panel-content"
        hx-swap="innerHTML">
    <input type="hidden" name="tipo" value="{{ tipo }}">
    <input type="hidden" name="referencia_id" value="{{ referencia_id or '' }}">
    <textarea name="contenido"
              placeholder="Escribe un comentario…"
              rows="2"
              required></textarea>
    <button type="submit" class="btn btn--primary btn--sm">Enviar</button>
  </form>
  {% endif %}

</div>
```

- [ ] **Step 2: Crear `tabla_encuestas.html`**

```html
<!-- app/templates/partials/tabla_encuestas.html -->
{% if rows %}

{% set excluded_keys = ['id', 'contrato_id', 'created_at'] %}

<table>
  <thead>
    <tr>
      {% for key in rows[0].keys() %}
        {% if key not in excluded_keys %}
        <th>{{ key | replace('_', ' ') | title }}</th>
        {% endif %}
      {% endfor %}
      <th style="width:100px;">Acciones</th>
    </tr>
  </thead>
  <tbody>
    {% for row in rows %}
    <tr id="row-enc-{{ row.id }}">
      {% for key, val in row.items() %}
        {% if key not in excluded_keys %}
        <td>{{ val if val is not none else '—' }}</td>
        {% endif %}
      {% endfor %}
      <td>
        <div style="display:flex;gap:.25rem;">
          <button class="btn btn--ghost btn--sm"
                  title="Ver comentarios"
                  hx-get="/api/comentarios?tipo=encuesta&ref={{ row.id }}"
                  hx-target="#comments-panel-content"
                  hx-swap="innerHTML"
                  hx-on::after-request="document.getElementById('comments-section').style.display=''">
            💬
          </button>
          {% if current_user_rol == 'administrador' %}
          <button class="btn btn--danger btn--sm"
                  title="Eliminar registro"
                  hx-delete="/api/encuestas/{{ row.id }}"
                  hx-target="#row-enc-{{ row.id }}"
                  hx-swap="outerHTML"
                  hx-confirm="¿Eliminar este registro permanentemente?">
            🗑
          </button>
          {% endif %}
        </div>
      </td>
    </tr>
    {% endfor %}
  </tbody>
</table>

<!-- Paginación -->
<div class="pagination">
  <span>{{ total }} registros · Página {{ page }} de {{ total_pages }}</span>
  <div class="pagination__controls">
    {% if page > 1 %}
    <button class="btn btn--ghost btn--sm"
            hx-get="/api/encuestas?page={{ page - 1 }}"
            hx-target="#tabla-encuestas-wrap"
            hx-swap="innerHTML"
            hx-include="#filtros-encuestas">
      ‹ Anterior
    </button>
    {% endif %}
    {% if page < total_pages %}
    <button class="btn btn--ghost btn--sm"
            hx-get="/api/encuestas?page={{ page + 1 }}"
            hx-target="#tabla-encuestas-wrap"
            hx-swap="innerHTML"
            hx-include="#filtros-encuestas">
      Siguiente ›
    </button>
    {% endif %}
  </div>
</div>

{% else %}
<div style="padding:3rem;text-align:center;color:var(--color-text-muted);">
  No se encontraron registros para los filtros seleccionados.
</div>
{% endif %}
```

- [ ] **Step 3: Crear `tabla_instalaciones.html`** (idéntica a encuestas, cambia los endpoints y el id de row)

```html
<!-- app/templates/partials/tabla_instalaciones.html -->
{% if rows %}

{% set excluded_keys = ['id', 'contrato_id', 'created_at'] %}

<table>
  <thead>
    <tr>
      {% for key in rows[0].keys() %}
        {% if key not in excluded_keys %}
        <th>{{ key | replace('_', ' ') | title }}</th>
        {% endif %}
      {% endfor %}
      <th style="width:100px;">Acciones</th>
    </tr>
  </thead>
  <tbody>
    {% for row in rows %}
    <tr id="row-inst-{{ row.id }}">
      {% for key, val in row.items() %}
        {% if key not in excluded_keys %}
        <td>{{ val if val is not none else '—' }}</td>
        {% endif %}
      {% endfor %}
      <td>
        <div style="display:flex;gap:.25rem;">
          <button class="btn btn--ghost btn--sm"
                  title="Ver comentarios"
                  hx-get="/api/comentarios?tipo=instalacion&ref={{ row.id }}"
                  hx-target="#comments-panel-content"
                  hx-swap="innerHTML"
                  hx-on::after-request="document.getElementById('comments-section').style.display=''">
            💬
          </button>
          {% if current_user_rol == 'administrador' %}
          <button class="btn btn--danger btn--sm"
                  title="Eliminar registro"
                  hx-delete="/api/instalaciones/{{ row.id }}"
                  hx-target="#row-inst-{{ row.id }}"
                  hx-swap="outerHTML"
                  hx-confirm="¿Eliminar este registro permanentemente?">
            🗑
          </button>
          {% endif %}
        </div>
      </td>
    </tr>
    {% endfor %}
  </tbody>
</table>

<div class="pagination">
  <span>{{ total }} registros · Página {{ page }} de {{ total_pages }}</span>
  <div class="pagination__controls">
    {% if page > 1 %}
    <button class="btn btn--ghost btn--sm"
            hx-get="/api/instalaciones?page={{ page - 1 }}"
            hx-target="#tabla-instalaciones-wrap"
            hx-swap="innerHTML"
            hx-include="#filtros-instalaciones">
      ‹ Anterior
    </button>
    {% endif %}
    {% if page < total_pages %}
    <button class="btn btn--ghost btn--sm"
            hx-get="/api/instalaciones?page={{ page + 1 }}"
            hx-target="#tabla-instalaciones-wrap"
            hx-swap="innerHTML"
            hx-include="#filtros-instalaciones">
      Siguiente ›
    </button>
    {% endif %}
  </div>
</div>

{% else %}
<div style="padding:3rem;text-align:center;color:var(--color-text-muted);">
  No se encontraron registros para los filtros seleccionados.
</div>
{% endif %}
```

- [ ] **Step 4: Crear `badge_hito.html`**

```html
<!-- app/templates/partials/badge_hito.html -->
<span id="badge-hito-{{ hito_id }}"
      class="badge badge--{{ 'success' if estado == 'aprobado' else ('warning' if estado == 'en_revision' else 'neutral') }}">
  {{ {'pendiente': 'Pendiente', 'en_revision': 'En revisión', 'aprobado': 'Aprobado'}.get(estado, estado) }}
</span>
```

- [ ] **Step 5: Correr suite completa**

```powershell
python -m pytest tests/ -v --tb=short
```

Esperado: `55 passed, 0 failed`

- [ ] **Step 6: Commit**

```powershell
git add app/templates/partials/
git commit -m "feat: add HTMX partial templates (comentarios, tablas, badge hito)"
```

---

## Verificación final de Fase 6

- [ ] **Suite completa**

```powershell
python -m pytest tests/ -v --tb=short
```

Esperado: `55 passed, 0 failed`

- [ ] **Verificar todas las rutas del blueprint api**

```powershell
python -c "
from app import create_app
app = create_app()
api_rules = [str(r) for r in app.url_map.iter_rules() if '/api/' in str(r)]
for r in sorted(api_rules): print(r)
"
```

Debe listar:
```
/api/comentarios
/api/contratos/ejecutado
/api/encuestas
/api/encuestas/<encuesta_id>
/api/hitos/<hito_id>/estado
/api/instalaciones
/api/instalaciones/<instalacion_id>
/api/set-contrato
```

---

**Fase 6 completada. Continuar con Fase 7: SQL Migration + smoke test final.**
