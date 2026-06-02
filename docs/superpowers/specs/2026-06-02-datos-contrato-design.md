# Spec: Página Datos del Contrato

**Fecha:** 2026-06-02
**Registro:** product (dashboard — diseño sirve al producto)
**Skills de respaldo:** impeccable (product register), design-taste-frontend

---

## Contexto

La página `dashboard/general` ("Datos del Contrato") existía con campos ficticios que no coincidían con el esquema real de Supabase. Se reconstruye completa sobre las tablas reales: `contratos`, `contratos_prorrogas` y `contratos_adiciones`.

El usuario que abre esta página es un supervisor o administrador de contrato que necesita entender el estado del contrato (financiero y temporal) en menos de 10 segundos. Densidad informativa, sin decoración innecesaria.

---

## Decisiones de diseño

| Decisión | Elección | Alternativas descartadas |
|---|---|---|
| Prórrogas y adiciones | Solo KPIs de resumen (conteo + valor/plazo actual) | Tablas completas, cards colapsables |
| Barras de progreso | Solo avance de tiempo (calculado desde fechas) | Ambas barras, reemplazar por avance financiero |
| Layout | Header prominente + dos columnas + sección partes | Flat layout, minimal card-per-topic |

---

## Arquitectura

Tres archivos modificados, ninguno nuevo:

### `app/models/contratos.py`

**Funciones existentes que se conservan:**
- `get_contrato(contrato_id)` — sin cambios

**Funciones que se eliminan:**
- `update_porcentaje_ejecutado()` — campo no existe en el esquema real

**Funciones nuevas:**
- `get_prorrogas_resumen(contrato_id)` — consulta `contratos_prorrogas`, devuelve `{count, plazo_actual, ultima_fecha_fin}`
- `get_adiciones_resumen(contrato_id)` — consulta `contratos_adiciones`, devuelve `{count, valor_actual}`

### `app/dashboard/routes.py`

La función `general()` se amplía:
1. Llama a `get_contrato()`, `get_prorrogas_resumen()`, `get_adiciones_resumen()`
2. Calcula `progreso_tiempo` usando `plazo_actual` como extremo derecho (fallback a `fecha_fin` si `plazo_actual` es null)
3. Elimina lógica de `progreso_ejecutado`
4. Pasa al template: `contrato`, `prorrogas`, `adiciones`, `progreso_tiempo`

### `app/templates/dashboard/general.html`

Reescritura completa del bloque `{% block content %}`. Sin CSS nuevo — usa las clases existentes del sistema de diseño (`card`, `kpi-card`, `kpi-grid`, `progress-wrap`, `progress-bar`).

---

## Layout

```
┌─────────────────────────────────────────────────────────┐
│  HEADER CARD                                             │
│  [id contrato — muted xs]       [● ACTIVO / ○ INACTIVO] │
│  [nombre del contrato — bold]                            │
│  ──────────────────────────────────────────────────────  │
│  Avance de tiempo  ████████████░░░░░  67%               │
│  fecha_inicio ─────────────────────── plazo_actual       │
└─────────────────────────────────────────────────────────┘

┌──────────────────────────┐  ┌──────────────────────────┐
│  FINANZAS                │  │  CRONOGRAMA              │
│                          │  │                          │
│  Valor original          │  │  Inicio                  │
│  $ 1.200.000.000         │  │  15 ene 2024             │
│                          │  │                          │
│  ↓ 2 adiciones           │  │  + 3 prórrogas           │
│  [línea muted]           │  │  [línea muted]           │
│                          │  │                          │
│  Valor actual            │  │  Plazo actual            │
│  $ 1.450.000.000         │  │  30 jun 2025             │
└──────────────────────────┘  └──────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  PARTES                                                  │
│  Contratista          Interventoría       Supervisor     │
│  Empresa XYZ          Empresa ABC         Juan Pérez     │
└─────────────────────────────────────────────────────────┘
```

---

## Componentes en detalle

### Header card

- Contenedor: clase `card` existente
- `id` del contrato: `text-xs`, `color-text-muted`, arriba a la izquierda
- Nombre: `font-weight: 700`, `text-xl`
- Badge activo/inactivo: alineado a la derecha en la misma fila del nombre
  - Activo: fondo `--color-success-bg`, texto `--color-success`
  - Inactivo: fondo `--color-surface-2`, texto `--color-text-muted`
- Barra de tiempo: reutiliza exactamente el `.progress-wrap` actual, extremo derecho usa `plazo_actual` con fallback a `fecha_fin`

### Bloque Finanzas (columna izquierda)

Estructura vertical dentro de un `card`:
1. Label "Valor original" + valor `valor_contrato` formateado con `|currency_col`
2. Línea intermedia: `↓ N adiciones` en `text-xs muted` (si `adiciones = 0`: "Sin adiciones")
3. Label "Valor actual" + valor (`adiciones.valor_actual` si existe, sino `valor_contrato`)

### Bloque Cronograma (columna derecha)

Misma estructura vertical:
1. Label "Inicio" + valor `fecha_inicio` con `|date_col`
2. Línea intermedia: `+ N prórrogas` en `text-xs muted` (si `prorrogas = 0`: "Sin prórrogas")
3. Label "Plazo actual" + valor (`plazo_actual` si existe, sino `fecha_fin`)

### Sección Partes

- Contenedor: `card` con `kpi-grid` de 3 columnas
- Cada celda: label en `text-xs uppercase muted` + valor en `font-weight: 600 text-sm`
- Si `supervisor` es null: muestra `—`

---

## Manejo de estados

| Situación | Comportamiento |
|---|---|
| Sin contrato activo | Tarjeta centrada "No hay contrato activo" (se conserva el existente) |
| `client is None` (Supabase no disponible) | Mismo estado vacío |
| `fecha_inicio` / `fecha_fin` ausentes | Barra de progreso oculta con `{% if %}` |
| `supervisor` es null | Celda muestra `—` explícito |
| `valor_actual` es null | Muestra `valor_contrato` sin modificar |
| `prorrogas = 0` | Línea intermedia: "Sin prórrogas" en muted |
| `adiciones = 0` | Línea intermedia: "Sin adiciones" en muted |

---

## Criterios de calidad (según impeccable product register)

- Ningún campo muestra un valor calculado o falso cuando el dato real no existe
- Sin motion decorativo — la barra de progreso es estática
- Las clases de color reutilizan el vocabulario semántico existente (`--color-success`, `--color-text-muted`, etc.)
- Sin CSS nuevo en este feature — solo clases existentes
- Contraste WCAG AA garantizado por el sistema de diseño existente (colores definidos en `base.css`)

---

## Archivos que NO se tocan

- `base.css`, `desktop.css`, `mobile.css` — no hay CSS nuevo
- Resto de rutas del dashboard — sin cambios
- Tests existentes — se adaptan los tests de `contratos.py` para las nuevas funciones
