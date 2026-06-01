# Gestión de Contratos — Plan Fase 2: Models (Supabase Data Access)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Prerequisito:** Fase 1 completada. `6 passed` en la suite de tests.

**Goal:** Implementar todas las funciones de acceso a Supabase para las 6 tablas del dominio, con tests usando mocks. Ninguna función conecta a Supabase real.

**Fases del proyecto:**
- ✅ Fase 1 — Scaffolding + Config + Auth Utils
- ✅ **Fase 2** — Models (Supabase data access) ← estás aquí
- Fase 3 — Auth routes + Login UI
- Fase 4 — CSS Design System + App Shell
- Fase 5 — Dashboard modules
- Fase 6 — HTMX API endpoints
- Fase 7 — SQL Migration + smoke test

---

## File Map (esta fase)

| Archivo | Responsabilidad |
|---|---|
| `app/models/usuarios.py` | get_usuario, get_modulos_visibles, get_contratos_by_user |
| `app/models/contratos.py` | get_contrato, calcular_progreso_tiempo, update_porcentaje_ejecutado |
| `app/models/hitos.py` | get_hitos, update_estado_hito |
| `app/models/encuestas.py` | get_encuestas (con filtros + paginación), delete_encuesta |
| `app/models/instalaciones.py` | get_instalaciones (con filtros + paginación), delete_instalacion |
| `app/models/comentarios.py` | get_comentarios, create_comentario |
| `tests/test_models/test_usuarios.py` | Tests para usuarios model |
| `tests/test_models/test_contratos.py` | Tests para contratos model |
| `tests/test_models/test_hitos.py` | Tests para hitos model |
| `tests/test_models/test_encuestas.py` | Tests para encuestas model |
| `tests/test_models/test_instalaciones.py` | Tests para instalaciones model |
| `tests/test_models/test_comentarios.py` | Tests para comentarios model |

---

## Task 7: usuarios model

**Files:**
- Crear: `app/models/usuarios.py`
- Crear: `tests/test_models/test_usuarios.py`

- [ ] **Step 1: Escribir tests que fallan**

```python
# tests/test_models/test_usuarios.py
import pytest
from unittest.mock import MagicMock, patch


@pytest.fixture
def mock_db():
    mock = MagicMock()
    with patch('app.utils.supabase_client._data_client', new=mock):
        yield mock


def test_get_usuario_returns_dict(mock_db):
    mock_db.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value.data = {
        'id': 'uid-1', 'nombre_completo': 'Ana Torres', 'rol': 'administrador', 'activo': True
    }
    from app.models.usuarios import get_usuario
    result = get_usuario('uid-1')
    assert result['rol'] == 'administrador'
    assert result['nombre_completo'] == 'Ana Torres'


def test_get_usuario_not_found_returns_none(mock_db):
    mock_db.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value.data = None
    from app.models.usuarios import get_usuario
    result = get_usuario('no-existe')
    assert result is None


def test_get_modulos_visibles_returns_list(mock_db):
    mock_db.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value.data = [
        {'modulo': 'general'},
        {'modulo': 'hitos'},
        {'modulo': 'encuestas'},
    ]
    from app.models.usuarios import get_modulos_visibles
    result = get_modulos_visibles('supervision')
    assert result == ['general', 'hitos', 'encuestas']


def test_get_contratos_by_user_admin_returns_all(mock_db):
    mock_db.table.return_value.select.return_value.execute.return_value.data = [
        {'id': 'c1', 'nombre': 'Contrato A'},
        {'id': 'c2', 'nombre': 'Contrato B'},
    ]
    from app.models.usuarios import get_contratos_by_user
    result = get_contratos_by_user('uid-1', 'administrador')
    assert len(result) == 2


def test_get_contratos_by_user_non_admin_filters_by_assignment(mock_db):
    mock_db.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [
        {'contrato_id': 'c1', 'contratos': {'id': 'c1', 'nombre': 'Contrato A'}},
    ]
    from app.models.usuarios import get_contratos_by_user
    result = get_contratos_by_user('uid-2', 'supervision')
    assert len(result) == 1
    assert result[0]['id'] == 'c1'
```

- [ ] **Step 2: Correr tests — deben fallar**

```powershell
python -m pytest tests/test_models/test_usuarios.py -v
```

Esperado: `ERROR` — `ModuleNotFoundError`

- [ ] **Step 3: Implementar `usuarios.py`**

```python
# app/models/usuarios.py
from app.utils.supabase_client import get_data_client


def get_usuario(user_id: str) -> dict | None:
    client = get_data_client()
    resp = (
        client.table('usuarios')
        .select('id, nombre_completo, rol, activo')
        .eq('id', user_id)
        .single()
        .execute()
    )
    return resp.data


def get_modulos_visibles(rol: str) -> list[str]:
    client = get_data_client()
    resp = (
        client.table('rol_permisos')
        .select('modulo')
        .eq('rol', rol)
        .eq('visible', True)
        .execute()
    )
    return [row['modulo'] for row in (resp.data or [])]


def get_contratos_by_user(user_id: str, rol: str) -> list[dict]:
    client = get_data_client()
    if rol == 'administrador':
        resp = client.table('contratos').select('id, nombre').execute()
        return resp.data or []
    resp = (
        client.table('usuarios_contratos')
        .select('contrato_id, contratos(id, nombre)')
        .eq('user_id', user_id)
        .execute()
    )
    return [row['contratos'] for row in (resp.data or []) if row.get('contratos')]
```

- [ ] **Step 4: Correr tests — deben pasar**

```powershell
python -m pytest tests/test_models/test_usuarios.py -v
```

Esperado: `5 passed`

- [ ] **Step 5: Commit**

```powershell
git add app/models/usuarios.py tests/test_models/test_usuarios.py
git commit -m "feat: add usuarios model with tests"
```

---

## Task 8: contratos model

**Files:**
- Crear: `app/models/contratos.py`
- Crear: `tests/test_models/test_contratos.py`

- [ ] **Step 1: Escribir tests que fallan**

```python
# tests/test_models/test_contratos.py
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
    # Exactamente a la mitad del contrato
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
```

- [ ] **Step 2: Correr tests — deben fallar**

```powershell
python -m pytest tests/test_models/test_contratos.py -v
```

Esperado: `ERROR` — `ModuleNotFoundError`

- [ ] **Step 3: Implementar `contratos.py`**

```python
# app/models/contratos.py
from datetime import date
from app.utils.supabase_client import get_data_client


def get_contrato(contrato_id: str) -> dict | None:
    client = get_data_client()
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


def update_porcentaje_ejecutado(contrato_id: str, porcentaje: float) -> dict:
    client = get_data_client()
    resp = (
        client.table('contratos')
        .update({'porcentaje_ejecutado': porcentaje})
        .eq('id', contrato_id)
        .execute()
    )
    return resp.data[0] if resp.data else {}
```

- [ ] **Step 4: Correr tests — deben pasar**

```powershell
python -m pytest tests/test_models/test_contratos.py -v
```

Esperado: `5 passed`

- [ ] **Step 5: Commit**

```powershell
git add app/models/contratos.py tests/test_models/test_contratos.py
git commit -m "feat: add contratos model with progress calculation and tests"
```

---

## Task 9: hitos model

**Files:**
- Crear: `app/models/hitos.py`
- Crear: `tests/test_models/test_hitos.py`

- [ ] **Step 1: Escribir tests que fallan**

```python
# tests/test_models/test_hitos.py
import pytest
from unittest.mock import MagicMock, patch


@pytest.fixture
def mock_db():
    mock = MagicMock()
    with patch('app.utils.supabase_client._data_client', new=mock):
        yield mock


def test_get_hitos_returns_list(mock_db):
    mock_db.table.return_value.select.return_value.eq.return_value.order.return_value.execute.return_value.data = [
        {'id': 'h1', 'nombre': 'Hito 1', 'estado': 'pendiente', 'fecha_limite': '2025-03-01'},
        {'id': 'h2', 'nombre': 'Hito 2', 'estado': 'aprobado', 'fecha_limite': '2025-06-01'},
    ]
    from app.models.hitos import get_hitos
    result = get_hitos('c1')
    assert len(result) == 2
    assert result[0]['estado'] == 'pendiente'


def test_get_hitos_empty_returns_empty_list(mock_db):
    mock_db.table.return_value.select.return_value.eq.return_value.order.return_value.execute.return_value.data = []
    from app.models.hitos import get_hitos
    assert get_hitos('c1') == []


def test_update_estado_hito(mock_db):
    mock_db.table.return_value.update.return_value.eq.return_value.execute.return_value.data = [
        {'id': 'h1', 'estado': 'aprobado'}
    ]
    from app.models.hitos import update_estado_hito
    result = update_estado_hito('h1', 'aprobado')
    assert result['estado'] == 'aprobado'


def test_update_estado_hito_estado_invalido():
    from app.models.hitos import update_estado_hito
    with pytest.raises(ValueError, match='Estado inválido'):
        update_estado_hito('h1', 'invalido')
```

- [ ] **Step 2: Correr tests — deben fallar**

```powershell
python -m pytest tests/test_models/test_hitos.py -v
```

- [ ] **Step 3: Implementar `hitos.py`**

```python
# app/models/hitos.py
from app.utils.supabase_client import get_data_client

ESTADOS_VALIDOS = ('pendiente', 'en_revision', 'aprobado')


def get_hitos(contrato_id: str) -> list[dict]:
    client = get_data_client()
    resp = (
        client.table('hitos')
        .select('id, nombre, descripcion, fecha_limite, estado, archivo_url')
        .eq('contrato_id', contrato_id)
        .order('fecha_limite')
        .execute()
    )
    return resp.data or []


def update_estado_hito(hito_id: str, estado: str) -> dict:
    if estado not in ESTADOS_VALIDOS:
        raise ValueError(f'Estado inválido: {estado}. Valores permitidos: {ESTADOS_VALIDOS}')
    client = get_data_client()
    resp = (
        client.table('hitos')
        .update({'estado': estado})
        .eq('id', hito_id)
        .execute()
    )
    return resp.data[0] if resp.data else {}
```

- [ ] **Step 4: Correr tests — deben pasar**

```powershell
python -m pytest tests/test_models/test_hitos.py -v
```

Esperado: `4 passed`

- [ ] **Step 5: Commit**

```powershell
git add app/models/hitos.py tests/test_models/test_hitos.py
git commit -m "feat: add hitos model with state validation and tests"
```

---

## Task 10: encuestas + instalaciones models

**Files:**
- Crear: `app/models/encuestas.py`
- Crear: `app/models/instalaciones.py`
- Crear: `tests/test_models/test_encuestas.py`
- Crear: `tests/test_models/test_instalaciones.py`

> Nota: Los campos específicos de `encuestas` e `instalaciones` se conocerán al conectar con Supabase real. Los models usan `select('*')` y la paginación/filtros funcionan sobre cualquier columna que exista.

- [ ] **Step 1: Escribir tests para encuestas**

```python
# tests/test_models/test_encuestas.py
import pytest
from unittest.mock import MagicMock, patch


@pytest.fixture
def mock_db():
    mock = MagicMock()
    with patch('app.utils.supabase_client._data_client', new=mock):
        yield mock


def test_get_encuestas_returns_data_and_count(mock_db):
    mock_chain = mock_db.table.return_value
    mock_chain.select.return_value.eq.return_value.range.return_value.execute.return_value.data = [
        {'id': 'e1', 'contrato_id': 'c1'},
        {'id': 'e2', 'contrato_id': 'c1'},
    ]
    mock_chain.select.return_value.eq.return_value.range.return_value.execute.return_value.count = 2

    from app.models.encuestas import get_encuestas
    data, count = get_encuestas('c1', page=1, per_page=25)
    assert len(data) == 2
    assert count == 2


def test_delete_encuesta_calls_delete(mock_db):
    mock_db.table.return_value.delete.return_value.eq.return_value.execute.return_value.data = [{'id': 'e1'}]
    from app.models.encuestas import delete_encuesta
    result = delete_encuesta('e1')
    assert result is True
```

- [ ] **Step 2: Escribir tests para instalaciones**

```python
# tests/test_models/test_instalaciones.py
import pytest
from unittest.mock import MagicMock, patch


@pytest.fixture
def mock_db():
    mock = MagicMock()
    with patch('app.utils.supabase_client._data_client', new=mock):
        yield mock


def test_get_instalaciones_returns_data_and_count(mock_db):
    mock_chain = mock_db.table.return_value
    mock_chain.select.return_value.eq.return_value.range.return_value.execute.return_value.data = [
        {'id': 'i1', 'contrato_id': 'c1'},
    ]
    mock_chain.select.return_value.eq.return_value.range.return_value.execute.return_value.count = 1

    from app.models.instalaciones import get_instalaciones
    data, count = get_instalaciones('c1', page=1, per_page=25)
    assert len(data) == 1
    assert count == 1


def test_delete_instalacion_calls_delete(mock_db):
    mock_db.table.return_value.delete.return_value.eq.return_value.execute.return_value.data = [{'id': 'i1'}]
    from app.models.instalaciones import delete_instalacion
    result = delete_instalacion('i1')
    assert result is True
```

- [ ] **Step 3: Correr ambos tests — deben fallar**

```powershell
python -m pytest tests/test_models/test_encuestas.py tests/test_models/test_instalaciones.py -v
```

- [ ] **Step 4: Implementar `encuestas.py`**

```python
# app/models/encuestas.py
from app.utils.supabase_client import get_data_client


def get_encuestas(
    contrato_id: str,
    page: int = 1,
    per_page: int = 25,
    filtros: dict | None = None,
) -> tuple[list[dict], int]:
    client = get_data_client()
    offset = (page - 1) * per_page

    query = (
        client.table('encuestas')
        .select('*', count='exact')
        .eq('contrato_id', contrato_id)
    )

    if filtros:
        for campo, valor in filtros.items():
            if valor:
                query = query.ilike(campo, f'%{valor}%')

    resp = query.range(offset, offset + per_page - 1).execute()
    return resp.data or [], resp.count or 0


def delete_encuesta(encuesta_id: str) -> bool:
    client = get_data_client()
    resp = client.table('encuestas').delete().eq('id', encuesta_id).execute()
    return bool(resp.data)
```

- [ ] **Step 5: Implementar `instalaciones.py`**

```python
# app/models/instalaciones.py
from app.utils.supabase_client import get_data_client


def get_instalaciones(
    contrato_id: str,
    page: int = 1,
    per_page: int = 25,
    filtros: dict | None = None,
) -> tuple[list[dict], int]:
    client = get_data_client()
    offset = (page - 1) * per_page

    query = (
        client.table('instalaciones')
        .select('*', count='exact')
        .eq('contrato_id', contrato_id)
    )

    if filtros:
        for campo, valor in filtros.items():
            if valor:
                query = query.ilike(campo, f'%{valor}%')

    resp = query.range(offset, offset + per_page - 1).execute()
    return resp.data or [], resp.count or 0


def delete_instalacion(instalacion_id: str) -> bool:
    client = get_data_client()
    resp = client.table('instalaciones').delete().eq('id', instalacion_id).execute()
    return bool(resp.data)
```

- [ ] **Step 6: Correr tests — deben pasar**

```powershell
python -m pytest tests/test_models/test_encuestas.py tests/test_models/test_instalaciones.py -v
```

Esperado: `4 passed`

- [ ] **Step 7: Commit**

```powershell
git add app/models/encuestas.py app/models/instalaciones.py tests/test_models/test_encuestas.py tests/test_models/test_instalaciones.py
git commit -m "feat: add encuestas and instalaciones models with pagination and tests"
```

---

## Task 11: comentarios model

**Files:**
- Crear: `app/models/comentarios.py`
- Crear: `tests/test_models/test_comentarios.py`

- [ ] **Step 1: Escribir tests que fallan**

```python
# tests/test_models/test_comentarios.py
import pytest
from unittest.mock import MagicMock, patch


@pytest.fixture
def mock_db():
    mock = MagicMock()
    with patch('app.utils.supabase_client._data_client', new=mock):
        yield mock


def test_get_comentarios_globales(mock_db):
    mock_db.table.return_value.select.return_value.eq.return_value.eq.return_value.is_.return_value.order.return_value.execute.return_value.data = [
        {'id': 'cm1', 'tipo': 'global', 'contenido': 'Nota global', 'referencia_id': None},
    ]
    from app.models.comentarios import get_comentarios
    result = get_comentarios('c1', tipo='global')
    assert len(result) == 1
    assert result[0]['tipo'] == 'global'


def test_get_comentarios_por_registro(mock_db):
    mock_db.table.return_value.select.return_value.eq.return_value.eq.return_value.eq.return_value.order.return_value.execute.return_value.data = [
        {'id': 'cm2', 'tipo': 'encuesta', 'contenido': 'Obs registro', 'referencia_id': 'e1'},
    ]
    from app.models.comentarios import get_comentarios
    result = get_comentarios('c1', tipo='encuesta', referencia_id='e1')
    assert result[0]['referencia_id'] == 'e1'


def test_create_comentario(mock_db):
    mock_db.table.return_value.insert.return_value.execute.return_value.data = [
        {'id': 'cm3', 'contenido': 'Nuevo comentario', 'tipo': 'global', 'contrato_id': 'c1'}
    ]
    from app.models.comentarios import create_comentario
    result = create_comentario(
        contrato_id='c1',
        autor_id='uid-1',
        tipo='global',
        contenido='Nuevo comentario',
    )
    assert result['contenido'] == 'Nuevo comentario'


def test_create_comentario_tipo_invalido():
    from app.models.comentarios import create_comentario
    with pytest.raises(ValueError, match='Tipo inválido'):
        create_comentario('c1', 'uid-1', 'invalido', 'texto')
```

- [ ] **Step 2: Correr tests — deben fallar**

```powershell
python -m pytest tests/test_models/test_comentarios.py -v
```

- [ ] **Step 3: Implementar `comentarios.py`**

```python
# app/models/comentarios.py
from app.utils.supabase_client import get_data_client

TIPOS_VALIDOS = ('global', 'encuesta', 'instalacion', 'hito')


def get_comentarios(
    contrato_id: str,
    tipo: str,
    referencia_id: str | None = None,
) -> list[dict]:
    client = get_data_client()
    query = (
        client.table('comentarios')
        .select('id, contenido, tipo, referencia_id, created_at, usuarios(nombre_completo)')
        .eq('contrato_id', contrato_id)
        .eq('tipo', tipo)
    )
    if referencia_id:
        query = query.eq('referencia_id', referencia_id)
    else:
        query = query.is_('referencia_id', 'null')

    resp = query.order('created_at').execute()
    return resp.data or []


def create_comentario(
    contrato_id: str,
    autor_id: str,
    tipo: str,
    contenido: str,
    referencia_id: str | None = None,
) -> dict:
    if tipo not in TIPOS_VALIDOS:
        raise ValueError(f'Tipo inválido: {tipo}. Permitidos: {TIPOS_VALIDOS}')
    client = get_data_client()
    payload = {
        'contrato_id': contrato_id,
        'autor_id': autor_id,
        'tipo': tipo,
        'contenido': contenido.strip(),
        'referencia_id': referencia_id,
    }
    resp = client.table('comentarios').insert(payload).execute()
    return resp.data[0] if resp.data else {}
```

- [ ] **Step 4: Correr tests — deben pasar**

```powershell
python -m pytest tests/test_models/test_comentarios.py -v
```

Esperado: `4 passed`

- [ ] **Step 5: Commit**

```powershell
git add app/models/comentarios.py tests/test_models/test_comentarios.py
git commit -m "feat: add comentarios model with type validation and tests"
```

---

## Verificación final de Fase 2

- [ ] **Correr suite completa**

```powershell
python -m pytest tests/ -v --tb=short
```

Esperado: `22 passed, 0 failed`

- [ ] **Commit de cierre de fase**

```powershell
git commit --allow-empty -m "chore: fase 2 completa — todos los models con tests"
```

---

**Fase 2 completada. Continuar con Fase 3: Auth routes + Login UI.**
