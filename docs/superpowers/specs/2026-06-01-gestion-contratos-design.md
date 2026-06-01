# Diseño: Aplicación Web de Gestión de Contratos

**Fecha:** 2026-06-01  
**Proyecto:** ORBIT SERVIALCO FLASK  
**Stack:** Flask + HTMX + Tailwind CSS + Supabase

---

## 1. Resumen

Aplicación web multi-contrato para la gestión, visualización y seguimiento de contratos del sector de infraestructura/construcción. Permite a equipos con distintos roles consultar el estado de contratos, registros de encuestas e instalaciones, hitos y comentarios, con una interfaz profesional y sofisticada.

---

## 2. Stack Técnico

| Capa | Tecnología |
|---|---|
| Backend | Python 3.12 + Flask |
| Frontend rendering | Jinja2 + HTMX |
| Estilos | CSS personalizado (base, desktop, mobile) |
| Base de datos | Supabase (PostgreSQL) |
| Auth | Supabase Auth (JWT) gestionado desde Flask session |
| Credenciales | Variables de entorno via `.env` + `python-dotenv` |

---

## 3. Estructura del Proyecto

```
ORBIT_SERVIALCO_FLASK/
├── app/
│   ├── __init__.py              # Factory pattern, registra blueprints
│   ├── auth/
│   │   ├── __init__.py
│   │   └── routes.py            # /login, /logout, /cambiar-contrasena
│   ├── dashboard/
│   │   ├── __init__.py
│   │   └── routes.py            # General, Hitos, Encuestas, Instalaciones
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py            # Endpoints HTMX: tablas, comentarios, filtros
│   ├── models/
│   │   ├── contratos.py         # Acceso a tabla contratos
│   │   ├── encuestas.py         # Acceso a tabla encuestas
│   │   ├── instalaciones.py     # Acceso a tabla instalaciones
│   │   ├── hitos.py             # Acceso a tabla hitos
│   │   ├── comentarios.py       # Acceso a tabla comentarios
│   │   └── usuarios.py          # Acceso a tabla usuarios y permisos
│   ├── utils/
│   │   ├── auth.py              # Decoradores @login_required, @role_required
│   │   └── supabase_client.py   # Singleton cliente Supabase
│   ├── templates/
│   │   ├── base.html            # Shell: topbar + sidebar + selector contrato
│   │   ├── auth/
│   │   │   └── login.html
│   │   └── dashboard/
│   │       ├── general.html
│   │       ├── hitos.html
│   │       ├── encuestas.html
│   │       └── instalaciones.html
│   └── static/
│       ├── css/
│       │   ├── base.css         # Variables de color, tipografía, tokens compartidos
│       │   ├── desktop.css      # Layout sidebar + topbar, grillas (≥768px)
│       │   └── mobile.css       # Navegación colapsada, tarjetas en columna (<768px)
│       └── js/
│           └── main.js          # Interacciones mínimas (selector, modal)
├── .env                         # Credenciales reales — NUNCA en git
├── .env.example                 # Plantilla sin valores reales
├── .gitignore
├── config.py                    # Lee .env, expone clase Config
├── requirements.txt
└── run.py                       # Entry point
```

---

## 4. Seguridad de Credenciales

- `SUPABASE_URL`, `SUPABASE_ANON_KEY`, `SUPABASE_SERVICE_KEY` y `SECRET_KEY` viven únicamente en `.env`.
- `config.py` los lee con `os.environ.get()` y los expone como atributos de clase `Config`.
- Las credenciales nunca se pasan a templates Jinja2 ni al frontend.
- `.gitignore` excluye `.env` explícitamente.
- `.env.example` documenta las variables requeridas sin valores reales.

---

## 5. Autenticación

### Flujo de login
1. Usuario accede a `/login` (única ruta pública).
2. Flask llama `supabase.auth.sign_in_with_password(email, password)`.
3. Supabase devuelve JWT; Flask lo almacena en la sesión del servidor (firmada con `SECRET_KEY`).
4. Se consulta la tabla `usuarios` para obtener `nombre_completo` y `rol`.
5. El `contrato_activo_id` se inicializa con el primer contrato asignado.
6. Todas las rutas protegidas aplican `@login_required`.

### Cambio de contraseña
- Accesible desde la topbar (avatar del usuario) para todos los roles.
- Modal con campos: contraseña actual, nueva contraseña, confirmar nueva contraseña.
- Flask llama `supabase.auth.update_user(access_token, password=nueva)`.

### Logout
- `POST /logout` invalida la sesión Flask y redirige a `/login`.

---

## 6. Control de Acceso por Rol (RBAC)

### Roles disponibles
| Rol | Descripción |
|---|---|
| `administrador` | Acceso total; puede eliminar registros de BD |
| `directivo` | Ve todos los módulos; puede editar anotaciones; sin botón eliminar |
| `supervision` | Ve módulos permitidos; puede crear registros y comentarios; sin eliminar |
| `operativo` | Visualización de módulos específicos asignados; sin crear ni eliminar |

### Implementación
- Decorador `@login_required`: redirige a `/login` si no hay sesión activa.
- Decorador `@role_required(*roles)`: devuelve HTTP 403 si el rol no está en la lista.
- Tabla `rol_permisos` en Supabase: mapea `(rol, modulo) → visible: bool`. Permite ajustar visibilidad sin modificar código.
- Botones de eliminar se renderizan condicionalmente: `{% if session.rol == 'administrador' %}`.
- Módulos ocultos no se incluyen en el HTML del sidebar (no son solo CSS `display:none`).

---

## 7. Navegación Multi-Contrato

- Selector desplegable en la topbar que lista los contratos asignados al usuario.
- Si el usuario tiene un solo contrato, el selector aparece deshabilitado.
- Al cambiar de contrato: HTMX envía `POST /api/set-contrato` → Flask actualiza `session['contrato_activo_id']` → recarga del contenido principal.
- Administrador tiene acceso implícito a todos los contratos (sin filas en `usuarios_contratos`).
- Todo el contenido de la app se filtra siempre por `session['contrato_activo_id']`.

---

## 8. Esquema de Base de Datos

### `contratos`
```sql
id               UUID PRIMARY KEY
nombre           TEXT
objeto           TEXT
entidad_contratante TEXT
localizacion     TEXT
fecha_inicio     DATE
fecha_fin        DATE
plazo_meses      INTEGER
valor_contrato   NUMERIC
nombre_contratista   TEXT
nombre_interventoria TEXT
porcentaje_ejecutado NUMERIC DEFAULT 0
created_at       TIMESTAMPTZ DEFAULT now()
```

### `hitos`
```sql
id              UUID PRIMARY KEY
contrato_id     UUID REFERENCES contratos(id)
nombre          TEXT
descripcion     TEXT
fecha_limite    DATE
estado          TEXT CHECK (estado IN ('pendiente','en_revision','aprobado'))
archivo_url     TEXT
created_at      TIMESTAMPTZ DEFAULT now()
updated_at      TIMESTAMPTZ DEFAULT now()
```

### `encuestas`
```sql
id              UUID PRIMARY KEY
contrato_id     UUID REFERENCES contratos(id)
-- campos específicos del dataset (definidos al implementar)
created_at      TIMESTAMPTZ DEFAULT now()
```

### `instalaciones`
```sql
id              UUID PRIMARY KEY
contrato_id     UUID REFERENCES contratos(id)
-- campos específicos del dataset (definidos al implementar)
created_at      TIMESTAMPTZ DEFAULT now()
```

### `comentarios`
```sql
id              UUID PRIMARY KEY
contrato_id     UUID REFERENCES contratos(id)
autor_id        UUID REFERENCES usuarios(id)
tipo            TEXT CHECK (tipo IN ('global','encuesta','instalacion','hito'))
referencia_id   UUID  -- FK al registro específico, NULL para comentarios globales
contenido       TEXT
created_at      TIMESTAMPTZ DEFAULT now()
updated_at      TIMESTAMPTZ DEFAULT now()
```

### `usuarios`
```sql
id              UUID PRIMARY KEY  -- mismo id que auth.users
nombre_completo TEXT
rol             TEXT CHECK (rol IN ('administrador','directivo','supervision','operativo'))
activo          BOOLEAN DEFAULT true
created_at      TIMESTAMPTZ DEFAULT now()
```

### `usuarios_contratos`
```sql
user_id         UUID REFERENCES usuarios(id)
contrato_id     UUID REFERENCES contratos(id)
fecha_asignacion DATE DEFAULT CURRENT_DATE
PRIMARY KEY (user_id, contrato_id)
```

### `rol_permisos`
```sql
rol             TEXT
modulo          TEXT
visible         BOOLEAN
PRIMARY KEY (rol, modulo)
```

**Valores iniciales:**
| rol | modulo | visible |
|---|---|---|
| administrador | general | true |
| administrador | hitos | true |
| administrador | encuestas | true |
| administrador | instalaciones | true |
| directivo | general | true |
| directivo | hitos | true |
| directivo | encuestas | true |
| directivo | instalaciones | true |
| supervision | general | true |
| supervision | hitos | true |
| supervision | encuestas | true |
| supervision | instalaciones | false |
| operativo | general | true |
| operativo | hitos | false |
| operativo | encuestas | false |
| operativo | instalaciones | false |

> Los valores de Supervisión y Operativo son un punto de partida. Ajustar según requerimiento real antes de deploy.

---

## 9. Módulos y Comportamiento UI

### Login (`/login`)
- Pantalla dividida: imagen técnica (blueprint infraestructura) a la izquierda, tarjeta blanca centrada a la derecha.
- Formulario: email, contraseña, botón "Ingresar al sistema" en `#0055B3`.
- Sin opción de registro ni recuperación de contraseña pública.

### Shell principal (`base.html`)
- **Topbar**: selector de contrato, breadcrumbs, toggle modo oscuro/claro, avatar con dropdown (perfil, cambiar contraseña, logout).
- **Sidebar** fijo izquierda, fondo azul oscuro, grupos: GENERAL / ENCUESTAS / INSTALACIONES. Módulos ocultos no se renderizan.
- **Área de contenido**: zona central que cambia según la ruta activa.

### General — Datos del Contrato (`/dashboard/general`)
- Grilla de tarjetas KPI: Entidad contratante, Objeto, Localización, Fecha inicio, Fecha fin, Plazo (meses), Valor del contrato.
- Dos barras de progreso prominentes:
  - **Tiempo**: calculado en Python `(hoy - fecha_inicio) / (fecha_fin - fecha_inicio) × 100`.
  - **Ejecución**: campo `porcentaje_ejecutado` en `contratos`, editable por Administrador y Supervisión.
- Colores de progreso: verde ≥ 50%, naranja 20–49%, rojo < 20%.

### General — Hitos (`/dashboard/hitos`)
- Tabla con columnas: Nombre, Descripción, Fecha límite, Estado (badge), Archivo.
- Estado cambiable por Administrador y Supervisión via dropdown inline (HTMX).
- Archivo enlaza a Supabase Storage.
- Panel de comentarios por hito (desplegable al hacer clic en la fila).

### Encuestas (`/dashboard/encuestas`)
- Frame de filtros superior (campos dinámicos via HTMX, actualizan solo la tabla).
- Tabla de registros paginada; botón eliminar visible solo para Administrador.
- Panel de comentarios por registro (desplegable al hacer clic en la fila).

### Instalaciones (`/dashboard/instalaciones`)
- Estructura idéntica a Encuestas.

---

## 10. Sistema de Estilos CSS

### Paleta de colores
| Token | Valor | Uso |
|---|---|---|
| `--color-primary` | `#0055B3` | Botones primarios, elementos activos, sidebar |
| `--color-success` | `#22C55E` | Progreso positivo, estados aprobados |
| `--color-warning` | `#F97316` | Valores pendientes, progreso bajo |
| `--color-danger` | `#EF4444` | Alertas, 0% ejecución |
| `--color-bg` | `#F8FAFC` | Fondo general |
| `--color-surface` | `#FFFFFF` | Tarjetas y paneles |
| `--color-sidebar` | `#0F172A` | Fondo sidebar |

### Archivos CSS
- **`base.css`**: Variables CSS, reset, tipografía, componentes atómicos (badges, barras de progreso, botones, modales).
- **`desktop.css`** (media `min-width: 768px`): Layout de dos columnas (sidebar fijo + contenido), grilla de tarjetas KPI, topbar horizontal.
- **`mobile.css`** (media `max-width: 767px`): Sidebar colapsado (hamburger menu), tarjetas en columna única, topbar compacta.

---

## 11. Interacciones HTMX

| Acción | Endpoint | Target |
|---|---|---|
| Cambiar contrato activo | `POST /api/set-contrato` | Recarga topbar + contenido |
| Filtrar tabla encuestas | `GET /api/encuestas?filtros=...` | `#tabla-encuestas` |
| Filtrar tabla instalaciones | `GET /api/instalaciones?filtros=...` | `#tabla-instalaciones` |
| Cargar comentarios de registro | `GET /api/comentarios?tipo=&ref=` | `#panel-comentarios` |
| Agregar comentario | `POST /api/comentarios` | `#panel-comentarios` |
| Cambiar estado de hito | `PATCH /api/hitos/{id}/estado` | `#fila-hito-{id}` |
| Eliminar registro | `DELETE /api/{tabla}/{id}` | Elimina fila del DOM |

---

## 12. Extensibilidad de Módulos

La arquitectura está diseñada para que agregar una nueva pestaña al sidebar sea un proceso estandarizado de bajo costo:

1. **Nuevo Blueprint Flask** en `app/dashboard/` con su propio `routes.py`.
2. **Nuevo template** en `app/templates/dashboard/nuevo_modulo.html` heredando de `base.html`.
3. **Nuevas filas en `rol_permisos`** para controlar qué roles ven el módulo.
4. **Registro del Blueprint** en `app/__init__.py`.
5. **Entrada en el sidebar** dentro de `base.html` (renderizado condicionalmente por permisos).

No se requiere modificar ninguna otra parte del sistema. Los nuevos módulos heredan automáticamente el sistema de autenticación, RBAC, selector de contrato y estilos.

---

## 13. Restricciones y Decisiones Clave

- La `anon key` de Supabase se usa solo para operaciones de Auth desde Flask. Para operaciones de datos se usa la `service_role key` en el backend, nunca expuesta al cliente.
- No hay ORM; el acceso a datos usa el cliente Python de Supabase directamente en funciones de `models/`.
- Los campos específicos de `encuestas` e `instalaciones` se definen durante la implementación según el dataset real de Supabase.
- El toggle de modo oscuro/claro usa una clase CSS en `<html>` y variables CSS redefinidas; persiste en `localStorage`.
