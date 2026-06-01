# Gestión de Contratos — Plan Fase 4: CSS Design System + App Shell

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Prerequisito:** Fase 3 completada. `31 passed` en la suite de tests.

**Goal:** Sistema de estilos CSS completo (variables, componentes, layouts responsive) y template `base.html` con sidebar, topbar, selector de contrato y modal de cambio de contraseña.

**Fases del proyecto:**
- ✅ Fase 1 — Scaffolding + Config + Auth Utils
- ✅ Fase 2 — Models
- ✅ Fase 3 — Auth routes + Login UI
- ✅ **Fase 4** — CSS Design System + App Shell ← estás aquí
- Fase 5 — Dashboard modules
- Fase 6 — HTMX API endpoints
- Fase 7 — SQL Migration + smoke test

---

## File Map (esta fase)

| Archivo | Responsabilidad |
|---|---|
| `app/static/css/base.css` | Variables, reset, componentes atómicos |
| `app/static/css/desktop.css` | Layout sidebar + topbar + grillas (≥768px) |
| `app/static/css/mobile.css` | Layout colapsado para <768px |
| `app/static/js/main.js` | Dark mode, hamburger, modal, HTMX helpers |
| `app/templates/base.html` | Shell: sidebar, topbar, selector contrato, modal |

> No hay tests unitarios para CSS/JS. La verificación es visual al correr la app.

---

## Task 14: base.css — variables, reset y componentes

**Files:**
- Crear: `app/static/css/base.css`

- [ ] **Step 1: Crear `base.css`**

```css
/* =========================================================
   base.css — Variables, reset y componentes atómicos
   Cargado en todas las vistas (login + dashboard)
   ========================================================= */

/* ── 1. Tokens de diseño ─────────────────────────────────── */
:root {
  /* Colores principales */
  --color-primary:        #0055B3;
  --color-primary-dark:   #003D82;
  --color-primary-light:  #EBF3FF;

  /* Estados */
  --color-success:        #22C55E;
  --color-success-bg:     #DCFCE7;
  --color-warning:        #F97316;
  --color-warning-bg:     #FFF7ED;
  --color-danger:         #EF4444;
  --color-danger-bg:      #FEF2F2;

  /* Superficies */
  --color-bg:             #F8FAFC;
  --color-surface:        #FFFFFF;
  --color-surface-2:      #F1F5F9;
  --color-sidebar:        #0F172A;
  --color-sidebar-hover:  #1E293B;
  --color-sidebar-active: #0055B3;

  /* Texto */
  --color-text:           #1E293B;
  --color-text-muted:     #64748B;
  --color-text-inverse:   #F8FAFC;

  /* Bordes y sombras */
  --color-border:         #E2E8F0;
  --shadow-sm:            0 1px 3px 0 rgb(0 0 0 / .10), 0 1px 2px -1px rgb(0 0 0 / .10);
  --shadow-md:            0 4px 6px -1px rgb(0 0 0 / .10), 0 2px 4px -2px rgb(0 0 0 / .10);
  --shadow-lg:            0 10px 15px -3px rgb(0 0 0 / .10), 0 4px 6px -4px rgb(0 0 0 / .10);

  /* Tipografía */
  --font-sans:            'Inter', system-ui, -apple-system, sans-serif;
  --font-mono:            'JetBrains Mono', 'Fira Code', monospace;
  --text-xs:              0.75rem;
  --text-sm:              0.875rem;
  --text-base:            1rem;
  --text-lg:              1.125rem;
  --text-xl:              1.25rem;
  --text-2xl:             1.5rem;
  --text-3xl:             1.875rem;

  /* Espaciado base */
  --radius-sm:            4px;
  --radius-md:            8px;
  --radius-lg:            12px;
  --radius-xl:            16px;

  /* Transiciones */
  --transition-fast:      150ms ease;
  --transition-base:      250ms ease;
}

/* Modo oscuro */
[data-theme="dark"] {
  --color-bg:             #0F172A;
  --color-surface:        #1E293B;
  --color-surface-2:      #334155;
  --color-text:           #F1F5F9;
  --color-text-muted:     #94A3B8;
  --color-border:         #334155;
  --color-sidebar:        #020617;
  --color-sidebar-hover:  #0F172A;
}

/* ── 2. Reset ─────────────────────────────────────────────── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html { font-size: 16px; scroll-behavior: smooth; }

body {
  font-family: var(--font-sans);
  font-size: var(--text-base);
  color: var(--color-text);
  background-color: var(--color-bg);
  line-height: 1.6;
  -webkit-font-smoothing: antialiased;
}

a { color: var(--color-primary); text-decoration: none; }
a:hover { text-decoration: underline; }

img, svg { display: block; max-width: 100%; }

/* ── 3. Botones ───────────────────────────────────────────── */
.btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  font-size: var(--text-sm);
  font-weight: 600;
  border-radius: var(--radius-md);
  border: 1.5px solid transparent;
  cursor: pointer;
  transition: background-color var(--transition-fast),
              border-color var(--transition-fast),
              opacity var(--transition-fast);
  white-space: nowrap;
  text-decoration: none;
}

.btn:disabled { opacity: .5; cursor: not-allowed; }

.btn--primary {
  background-color: var(--color-primary);
  color: #fff;
  border-color: var(--color-primary);
}
.btn--primary:hover { background-color: var(--color-primary-dark); border-color: var(--color-primary-dark); text-decoration: none; }

.btn--danger {
  background-color: transparent;
  color: var(--color-danger);
  border-color: var(--color-danger);
}
.btn--danger:hover { background-color: var(--color-danger-bg); text-decoration: none; }

.btn--ghost {
  background-color: transparent;
  color: var(--color-text-muted);
  border-color: var(--color-border);
}
.btn--ghost:hover { background-color: var(--color-surface-2); color: var(--color-text); text-decoration: none; }

.btn--sm { padding: 0.25rem 0.625rem; font-size: var(--text-xs); }
.btn--full { width: 100%; justify-content: center; }

/* ── 4. Formularios ──────────────────────────────────────── */
.form-group { display: flex; flex-direction: column; gap: 0.375rem; }

.form-label {
  font-size: var(--text-sm);
  font-weight: 500;
  color: var(--color-text);
}

.form-input, .form-select {
  width: 100%;
  padding: 0.5rem 0.75rem;
  font-size: var(--text-sm);
  color: var(--color-text);
  background-color: var(--color-surface);
  border: 1.5px solid var(--color-border);
  border-radius: var(--radius-md);
  transition: border-color var(--transition-fast), box-shadow var(--transition-fast);
  outline: none;
}

.form-input:focus, .form-select:focus {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px var(--color-primary-light);
}

.form-input::placeholder { color: var(--color-text-muted); }

/* ── 5. Tarjetas ─────────────────────────────────────────── */
.card {
  background-color: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
  padding: 1.5rem;
}

.card--compact { padding: 1rem; }

/* KPI card */
.kpi-card {
  background-color: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
  padding: 1.25rem 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.kpi-card__label {
  font-size: var(--text-xs);
  font-weight: 600;
  letter-spacing: .05em;
  text-transform: uppercase;
  color: var(--color-text-muted);
}

.kpi-card__value {
  font-size: var(--text-2xl);
  font-weight: 700;
  color: var(--color-text);
  line-height: 1.2;
}

.kpi-card__sub {
  font-size: var(--text-sm);
  color: var(--color-text-muted);
}

/* ── 6. Barras de progreso ───────────────────────────────── */
.progress-wrap {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.progress-wrap__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: var(--text-sm);
  font-weight: 500;
}

.progress-track {
  width: 100%;
  height: 10px;
  background-color: var(--color-surface-2);
  border-radius: 99px;
  overflow: hidden;
}

.progress-bar {
  height: 100%;
  border-radius: 99px;
  transition: width 0.6s ease;
}

.progress-bar--success { background-color: var(--color-success); }
.progress-bar--warning { background-color: var(--color-warning); }
.progress-bar--danger  { background-color: var(--color-danger); }

/* ── 7. Badges de estado ─────────────────────────────────── */
.badge {
  display: inline-flex;
  align-items: center;
  padding: 0.2rem 0.6rem;
  font-size: var(--text-xs);
  font-weight: 600;
  border-radius: 99px;
  white-space: nowrap;
}

.badge--success  { background-color: var(--color-success-bg); color: #16A34A; }
.badge--warning  { background-color: var(--color-warning-bg); color: #EA580C; }
.badge--danger   { background-color: var(--color-danger-bg);  color: #DC2626; }
.badge--neutral  { background-color: var(--color-surface-2);  color: var(--color-text-muted); }

/* ── 8. Tablas ───────────────────────────────────────────── */
.table-wrap {
  width: 100%;
  overflow-x: auto;
  border-radius: var(--radius-lg);
  border: 1px solid var(--color-border);
  background-color: var(--color-surface);
}

table {
  width: 100%;
  border-collapse: collapse;
  font-size: var(--text-sm);
}

thead th {
  padding: 0.75rem 1rem;
  text-align: left;
  font-size: var(--text-xs);
  font-weight: 600;
  letter-spacing: .05em;
  text-transform: uppercase;
  color: var(--color-text-muted);
  background-color: var(--color-surface-2);
  border-bottom: 1px solid var(--color-border);
  white-space: nowrap;
}

tbody td {
  padding: 0.75rem 1rem;
  border-bottom: 1px solid var(--color-border);
  color: var(--color-text);
  vertical-align: middle;
}

tbody tr:last-child td { border-bottom: none; }
tbody tr:hover { background-color: var(--color-primary-light); }
tbody tr { cursor: pointer; transition: background-color var(--transition-fast); }

/* ── 9. Alertas y mensajes flash ─────────────────────────── */
.alert {
  padding: 0.75rem 1rem;
  border-radius: var(--radius-md);
  font-size: var(--text-sm);
  font-weight: 500;
  border-left: 4px solid;
  margin-bottom: 1rem;
}

.alert--success { background-color: var(--color-success-bg); border-color: var(--color-success); color: #16A34A; }
.alert--error   { background-color: var(--color-danger-bg);  border-color: var(--color-danger);  color: #DC2626; }
.alert--warning { background-color: var(--color-warning-bg); border-color: var(--color-warning); color: #EA580C; }
.alert--info    { background-color: var(--color-primary-light); border-color: var(--color-primary); color: var(--color-primary); }

/* ── 10. Modales ─────────────────────────────────────────── */
.modal-backdrop {
  position: fixed;
  inset: 0;
  background-color: rgb(0 0 0 / .5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
  opacity: 0;
  visibility: hidden;
  transition: opacity var(--transition-base), visibility var(--transition-base);
}

.modal-backdrop.is-open {
  opacity: 1;
  visibility: visible;
}

.modal {
  background-color: var(--color-surface);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-lg);
  padding: 2rem;
  width: 100%;
  max-width: 440px;
  margin: 1rem;
  transform: translateY(8px);
  transition: transform var(--transition-base);
}

.modal-backdrop.is-open .modal { transform: translateY(0); }

.modal__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.modal__title {
  font-size: var(--text-lg);
  font-weight: 700;
  color: var(--color-text);
}

.modal__close {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 1.25rem;
  color: var(--color-text-muted);
  padding: 0.25rem;
  line-height: 1;
  transition: color var(--transition-fast);
}

.modal__close:hover { color: var(--color-text); }

.modal__body { display: flex; flex-direction: column; gap: 1rem; }
.modal__footer { display: flex; justify-content: flex-end; gap: 0.5rem; margin-top: 1.5rem; }

/* ── 11. Paginación ──────────────────────────────────────── */
.pagination {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem 1rem;
  border-top: 1px solid var(--color-border);
  font-size: var(--text-sm);
  color: var(--color-text-muted);
}

.pagination__controls { display: flex; gap: 0.25rem; }

/* ── 12. Panel de comentarios ────────────────────────────── */
.comments-panel {
  border-top: 1px solid var(--color-border);
  padding: 1rem;
  background-color: var(--color-surface-2);
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.comment-item {
  background-color: var(--color-surface);
  border-radius: var(--radius-md);
  padding: 0.75rem 1rem;
  border-left: 3px solid var(--color-primary);
}

.comment-item__meta {
  display: flex;
  gap: 0.5rem;
  align-items: center;
  margin-bottom: 0.25rem;
  font-size: var(--text-xs);
  color: var(--color-text-muted);
}

.comment-item__author { font-weight: 600; color: var(--color-text); }
.comment-item__body   { font-size: var(--text-sm); }

.comment-form { display: flex; gap: 0.5rem; margin-top: 0.5rem; }
.comment-form textarea {
  flex: 1;
  padding: 0.5rem 0.75rem;
  font-size: var(--text-sm);
  border: 1.5px solid var(--color-border);
  border-radius: var(--radius-md);
  background-color: var(--color-surface);
  resize: vertical;
  min-height: 60px;
  font-family: var(--font-sans);
  color: var(--color-text);
  outline: none;
}
.comment-form textarea:focus {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px var(--color-primary-light);
}

/* ── 13. Filtros ─────────────────────────────────────────── */
.filters-frame {
  background-color: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: 1rem 1.5rem;
  margin-bottom: 1rem;
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  align-items: flex-end;
}

.filters-frame .form-group { min-width: 160px; flex: 1; }

/* ── 14. Select de contrato (topbar) ─────────────────────── */
.contrato-selector {
  padding: 0.375rem 0.75rem;
  font-size: var(--text-sm);
  font-weight: 500;
  border: 1.5px solid var(--color-border);
  border-radius: var(--radius-md);
  background-color: var(--color-surface);
  color: var(--color-text);
  cursor: pointer;
  max-width: 280px;
  outline: none;
}
.contrato-selector:focus { border-color: var(--color-primary); }
.contrato-selector:disabled { opacity: .7; cursor: default; }

/* ── 15. Utilidades ──────────────────────────────────────── */
.sr-only { position: absolute; width: 1px; height: 1px; overflow: hidden; clip: rect(0,0,0,0); white-space: nowrap; }
.text-muted { color: var(--color-text-muted); }
.text-sm { font-size: var(--text-sm); }
.font-bold { font-weight: 700; }
.mt-1 { margin-top: 0.25rem; }
.mt-2 { margin-top: 0.5rem; }
.mt-4 { margin-top: 1rem; }
.gap-1 { gap: 0.25rem; }
.flex { display: flex; }
.items-center { align-items: center; }
.justify-between { justify-content: space-between; }
```

- [ ] **Step 2: Commit**

```powershell
git add app/static/css/base.css
git commit -m "feat: add base CSS design system with tokens and components"
```

---

## Task 15: desktop.css — layout sidebar + topbar

**Files:**
- Crear: `app/static/css/desktop.css`

- [ ] **Step 1: Crear `desktop.css`**

```css
/* =========================================================
   desktop.css — Layout para pantallas ≥ 768px
   Cargado solo cuando min-width: 768px
   ========================================================= */

/* ── Layout raíz ─────────────────────────────────────────── */
.app-layout {
  display: flex;
  height: 100vh;
  overflow: hidden;
}

/* ── Sidebar ─────────────────────────────────────────────── */
.sidebar {
  width: 260px;
  min-width: 260px;
  height: 100vh;
  background-color: var(--color-sidebar);
  display: flex;
  flex-direction: column;
  overflow-y: auto;
  overflow-x: hidden;
  scrollbar-width: thin;
  scrollbar-color: #334155 transparent;
  flex-shrink: 0;
}

.sidebar__brand {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1.5rem 1.25rem 1.25rem;
  border-bottom: 1px solid #1E293B;
}

.sidebar__logo {
  font-size: 1.5rem;
  line-height: 1;
}

.sidebar__name {
  font-size: var(--text-sm);
  font-weight: 700;
  color: var(--color-text-inverse);
  letter-spacing: .03em;
  line-height: 1.3;
}

.sidebar__sub {
  font-size: var(--text-xs);
  color: #64748B;
}

/* Grupos de navegación */
.sidebar__group { padding: 1rem 0 0.5rem; }

.sidebar__group-label {
  padding: 0 1.25rem 0.375rem;
  font-size: 0.65rem;
  font-weight: 700;
  letter-spacing: .1em;
  text-transform: uppercase;
  color: #475569;
}

.sidebar__item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.6rem 1.25rem;
  font-size: var(--text-sm);
  font-weight: 500;
  color: #94A3B8;
  text-decoration: none;
  border-radius: 0;
  transition: background-color var(--transition-fast), color var(--transition-fast);
  position: relative;
}

.sidebar__item:hover {
  background-color: var(--color-sidebar-hover);
  color: var(--color-text-inverse);
  text-decoration: none;
}

.sidebar__item.is-active {
  background-color: var(--color-sidebar-active);
  color: #fff;
}

.sidebar__item.is-active::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 3px;
  background-color: #60A5FA;
  border-radius: 0 2px 2px 0;
}

.sidebar__icon { font-size: 1rem; width: 1.25rem; text-align: center; flex-shrink: 0; }

/* ── Área de contenido principal ─────────────────────────── */
.main-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* ── Topbar ──────────────────────────────────────────────── */
.topbar {
  height: 64px;
  min-height: 64px;
  background-color: var(--color-surface);
  border-bottom: 1px solid var(--color-border);
  display: flex;
  align-items: center;
  padding: 0 1.5rem;
  gap: 1rem;
  position: sticky;
  top: 0;
  z-index: 10;
}

.topbar__left {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex: 1;
  min-width: 0;
}

.topbar__breadcrumb {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  font-size: var(--text-sm);
  color: var(--color-text-muted);
  overflow: hidden;
}

.topbar__breadcrumb a { color: var(--color-text-muted); }
.topbar__breadcrumb a:hover { color: var(--color-text); }
.topbar__breadcrumb .current { color: var(--color-text); font-weight: 500; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }

.topbar__right {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-shrink: 0;
}

/* Toggle modo oscuro */
.theme-toggle {
  background: none;
  border: 1.5px solid var(--color-border);
  border-radius: var(--radius-md);
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  font-size: 1rem;
  color: var(--color-text-muted);
  transition: background-color var(--transition-fast), border-color var(--transition-fast);
}

.theme-toggle:hover { background-color: var(--color-surface-2); border-color: var(--color-primary); }

/* Avatar / dropdown de usuario */
.user-menu { position: relative; }

.user-menu__trigger {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.375rem 0.75rem;
  border: 1.5px solid var(--color-border);
  border-radius: var(--radius-md);
  background: none;
  cursor: pointer;
  font-size: var(--text-sm);
  color: var(--color-text);
  transition: background-color var(--transition-fast);
}

.user-menu__trigger:hover { background-color: var(--color-surface-2); }

.user-menu__avatar {
  width: 28px;
  height: 28px;
  background-color: var(--color-primary);
  color: #fff;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: var(--text-xs);
  font-weight: 700;
  flex-shrink: 0;
}

.user-menu__name {
  max-width: 140px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.user-menu__dropdown {
  position: absolute;
  right: 0;
  top: calc(100% + 8px);
  background-color: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-lg);
  min-width: 200px;
  z-index: 50;
  display: none;
  overflow: hidden;
}

.user-menu__dropdown.is-open { display: block; }

.user-menu__dropdown-item {
  display: flex;
  align-items: center;
  gap: 0.625rem;
  padding: 0.625rem 1rem;
  font-size: var(--text-sm);
  color: var(--color-text);
  cursor: pointer;
  transition: background-color var(--transition-fast);
  border: none;
  background: none;
  width: 100%;
  text-align: left;
  text-decoration: none;
}

.user-menu__dropdown-item:hover { background-color: var(--color-surface-2); text-decoration: none; }
.user-menu__dropdown-item--danger:hover { background-color: var(--color-danger-bg); color: var(--color-danger); }
.user-menu__dropdown-divider { height: 1px; background-color: var(--color-border); }

/* ── Área de scroll del contenido ────────────────────────── */
.content-area {
  flex: 1;
  overflow-y: auto;
  padding: 1.5rem 2rem;
}

/* ── Página de login (desktop) ───────────────────────────── */
.login-page { height: 100vh; overflow: hidden; }

.login-layout {
  display: grid;
  grid-template-columns: 1fr 480px;
  height: 100vh;
}

.login-hero {
  background-color: var(--color-sidebar);
  background-image:
    linear-gradient(135deg, rgba(0,85,179,.85) 0%, rgba(15,23,42,.95) 100%),
    repeating-linear-gradient(
      0deg,
      transparent,
      transparent 40px,
      rgba(255,255,255,.03) 40px,
      rgba(255,255,255,.03) 41px
    ),
    repeating-linear-gradient(
      90deg,
      transparent,
      transparent 40px,
      rgba(255,255,255,.03) 40px,
      rgba(255,255,255,.03) 41px
    );
  display: flex;
  align-items: flex-end;
  padding: 3rem;
}

.login-hero__overlay { width: 100%; }

.login-hero__brand {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 0.75rem;
}

.login-hero__logo-mark { font-size: 2rem; }

.login-hero__brand-name {
  font-size: var(--text-xl);
  font-weight: 800;
  color: #fff;
  letter-spacing: .05em;
}

.login-hero__tagline {
  font-size: var(--text-base);
  color: #94A3B8;
  line-height: 1.6;
}

.login-form-panel {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  background-color: var(--color-bg);
}

.login-card {
  width: 100%;
  max-width: 380px;
}

.login-card__header { margin-bottom: 1.5rem; }

.login-card__title {
  font-size: var(--text-2xl);
  font-weight: 700;
  color: var(--color-text);
}

.login-card__subtitle {
  font-size: var(--text-sm);
  color: var(--color-text-muted);
  margin-top: 0.25rem;
}

.login-form { display: flex; flex-direction: column; gap: 1rem; }
.login-form .btn--primary { margin-top: 0.5rem; padding: 0.75rem; font-size: var(--text-base); }

/* ── Grilla de KPIs (dashboard) ──────────────────────────── */
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.progress-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

/* ── Page header ─────────────────────────────────────────── */
.page-header {
  margin-bottom: 1.5rem;
}

.page-header__title {
  font-size: var(--text-2xl);
  font-weight: 700;
  color: var(--color-text);
}

.page-header__sub {
  font-size: var(--text-sm);
  color: var(--color-text-muted);
  margin-top: 0.25rem;
}
```

- [ ] **Step 2: Commit**

```powershell
git add app/static/css/desktop.css
git commit -m "feat: add desktop CSS layout (sidebar, topbar, KPI grid)"
```

---

## Task 16: mobile.css + main.js

**Files:**
- Crear: `app/static/css/mobile.css`
- Crear: `app/static/js/main.js`

- [ ] **Step 1: Crear `mobile.css`**

```css
/* =========================================================
   mobile.css — Layout para pantallas < 768px
   Cargado solo cuando max-width: 767px
   ========================================================= */

/* ── Layout raíz ─────────────────────────────────────────── */
.app-layout {
  display: flex;
  flex-direction: column;
  height: 100vh;
  overflow: hidden;
}

/* ── Topbar móvil ────────────────────────────────────────── */
.topbar {
  height: 56px;
  min-height: 56px;
  background-color: var(--color-surface);
  border-bottom: 1px solid var(--color-border);
  display: flex;
  align-items: center;
  padding: 0 1rem;
  gap: 0.75rem;
  position: sticky;
  top: 0;
  z-index: 10;
}

.hamburger {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 1.25rem;
  color: var(--color-text);
  padding: 0.25rem;
  flex-shrink: 0;
}

.topbar__left { flex: 1; min-width: 0; }

.topbar__breadcrumb .current {
  font-size: var(--text-sm);
  font-weight: 500;
  color: var(--color-text);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  display: block;
}

.topbar__breadcrumb a { display: none; }

/* ── Sidebar móvil (offcanvas) ───────────────────────────── */
.sidebar-overlay {
  position: fixed;
  inset: 0;
  background-color: rgb(0 0 0 / .5);
  z-index: 40;
  display: none;
}

.sidebar-overlay.is-open { display: block; }

.sidebar {
  position: fixed;
  top: 0;
  left: 0;
  width: 280px;
  height: 100vh;
  background-color: var(--color-sidebar);
  display: flex;
  flex-direction: column;
  overflow-y: auto;
  z-index: 50;
  transform: translateX(-100%);
  transition: transform var(--transition-base);
}

.sidebar.is-open { transform: translateX(0); }

.sidebar__brand {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1.25rem;
  border-bottom: 1px solid #1E293B;
}

.sidebar__logo { font-size: 1.5rem; }

.sidebar__name {
  font-size: var(--text-sm);
  font-weight: 700;
  color: var(--color-text-inverse);
}

.sidebar__sub { font-size: var(--text-xs); color: #64748B; }

.sidebar__group { padding: 1rem 0 0.5rem; }

.sidebar__group-label {
  padding: 0 1.25rem 0.375rem;
  font-size: 0.65rem;
  font-weight: 700;
  letter-spacing: .1em;
  text-transform: uppercase;
  color: #475569;
}

.sidebar__item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.7rem 1.25rem;
  font-size: var(--text-sm);
  font-weight: 500;
  color: #94A3B8;
  text-decoration: none;
}

.sidebar__item:hover { background-color: var(--color-sidebar-hover); color: #fff; }
.sidebar__item.is-active { background-color: var(--color-sidebar-active); color: #fff; }

/* ── Área de contenido ───────────────────────────────────── */
.main-area { flex: 1; overflow: hidden; display: flex; flex-direction: column; }

.content-area {
  flex: 1;
  overflow-y: auto;
  padding: 1rem;
}

/* ── Login móvil ─────────────────────────────────────────── */
.login-page { min-height: 100vh; }

.login-layout {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.login-hero {
  background-color: var(--color-sidebar);
  background-image: linear-gradient(135deg, rgba(0,85,179,.85) 0%, rgba(15,23,42,.95) 100%);
  padding: 2rem 1.5rem 1.5rem;
}

.login-hero__brand {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}

.login-hero__logo-mark { font-size: 1.5rem; }
.login-hero__brand-name { font-size: var(--text-base); font-weight: 800; color: #fff; }
.login-hero__tagline { font-size: var(--text-sm); color: #94A3B8; }

.login-form-panel {
  flex: 1;
  padding: 2rem 1.5rem;
  background-color: var(--color-bg);
}

.login-card__title { font-size: var(--text-xl); font-weight: 700; }
.login-card__subtitle { font-size: var(--text-sm); color: var(--color-text-muted); margin-top: 0.25rem; }
.login-card__header { margin-bottom: 1.5rem; }
.login-form { display: flex; flex-direction: column; gap: 1rem; }

/* ── Grillas adaptadas ───────────────────────────────────── */
.kpi-grid { grid-template-columns: 1fr 1fr; }
.progress-grid { grid-template-columns: 1fr; }

/* ── Contrato selector — topbar móvil ────────────────────── */
.contrato-selector { max-width: 160px; font-size: var(--text-xs); }

/* ── User menu mobile ────────────────────────────────────── */
.user-menu__name { display: none; }
.user-menu__trigger { padding: 0.375rem; }
.user-menu__dropdown { right: -0.5rem; }
```

- [ ] **Step 2: Crear `main.js`**

```javascript
// app/static/js/main.js

document.addEventListener('DOMContentLoaded', () => {

  // ── Dark mode ──────────────────────────────────────────
  const html = document.documentElement;
  const savedTheme = localStorage.getItem('orbit-theme') || 'light';
  html.setAttribute('data-theme', savedTheme);

  const themeToggle = document.getElementById('theme-toggle');
  if (themeToggle) {
    themeToggle.addEventListener('click', () => {
      const next = html.getAttribute('data-theme') === 'light' ? 'dark' : 'light';
      html.setAttribute('data-theme', next);
      localStorage.setItem('orbit-theme', next);
      themeToggle.setAttribute('aria-label', next === 'dark' ? 'Cambiar a modo claro' : 'Cambiar a modo oscuro');
    });
  }

  // ── Hamburger (mobile sidebar) ─────────────────────────
  const hamburger = document.getElementById('hamburger');
  const sidebar = document.getElementById('sidebar');
  const overlay = document.getElementById('sidebar-overlay');

  function openSidebar() {
    sidebar?.classList.add('is-open');
    overlay?.classList.add('is-open');
    document.body.style.overflow = 'hidden';
  }

  function closeSidebar() {
    sidebar?.classList.remove('is-open');
    overlay?.classList.remove('is-open');
    document.body.style.overflow = '';
  }

  hamburger?.addEventListener('click', openSidebar);
  overlay?.addEventListener('click', closeSidebar);

  // Cerrar sidebar al navegar (HTMX)
  document.addEventListener('htmx:afterRequest', closeSidebar);

  // ── User menu dropdown ─────────────────────────────────
  const userTrigger = document.getElementById('user-menu-trigger');
  const userDropdown = document.getElementById('user-menu-dropdown');

  userTrigger?.addEventListener('click', (e) => {
    e.stopPropagation();
    userDropdown?.classList.toggle('is-open');
  });

  document.addEventListener('click', () => {
    userDropdown?.classList.remove('is-open');
  });

  // ── Modal cambiar contraseña ───────────────────────────
  const modalBackdrop = document.getElementById('modal-password');

  function openModal() { modalBackdrop?.classList.add('is-open'); }
  function closeModal() { modalBackdrop?.classList.remove('is-open'); }

  document.getElementById('btn-cambiar-contrasena')?.addEventListener('click', (e) => {
    e.stopPropagation();
    userDropdown?.classList.remove('is-open');
    openModal();
  });

  document.getElementById('modal-password-close')?.addEventListener('click', closeModal);

  modalBackdrop?.addEventListener('click', (e) => {
    if (e.target === modalBackdrop) closeModal();
  });

  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') closeModal();
  });

  // ── HTMX: indicador de carga en tablas ─────────────────
  document.body.addEventListener('htmx:beforeRequest', (e) => {
    const target = e.detail.target;
    if (target?.classList.contains('table-wrap')) {
      target.style.opacity = '0.5';
    }
  });

  document.body.addEventListener('htmx:afterRequest', (e) => {
    const target = e.detail.target;
    if (target?.style?.opacity) target.style.opacity = '1';
  });

});
```

- [ ] **Step 3: Commit**

```powershell
git add app/static/css/mobile.css app/static/js/main.js
git commit -m "feat: add mobile CSS layout and main.js (dark mode, hamburger, modal)"
```

---

## Task 17: base.html — App Shell completo

**Files:**
- Crear: `app/templates/base.html`

- [ ] **Step 1: Crear `base.html`**

```html
<!-- app/templates/base.html -->
<!DOCTYPE html>
<html lang="es" data-theme="light">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{% block title %}ORBIT SERVIALCO{% endblock %}</title>
  <link rel="stylesheet" href="{{ url_for('static', filename='css/base.css') }}">
  <link rel="stylesheet" href="{{ url_for('static', filename='css/desktop.css') }}" media="(min-width: 768px)">
  <link rel="stylesheet" href="{{ url_for('static', filename='css/mobile.css') }}" media="(max-width: 767px)">
  <script src="https://unpkg.com/htmx.org@2.0.3" defer></script>
  <script src="{{ url_for('static', filename='js/main.js') }}" defer></script>
</head>
<body>

<!-- Overlay para sidebar móvil -->
<div id="sidebar-overlay" class="sidebar-overlay" aria-hidden="true"></div>

<div class="app-layout">

  <!-- ══ SIDEBAR ══════════════════════════════════════════ -->
  <aside id="sidebar" class="sidebar" aria-label="Navegación principal">

    <div class="sidebar__brand">
      <span class="sidebar__logo" aria-hidden="true">⬡</span>
      <div>
        <div class="sidebar__name">ORBIT</div>
        <div class="sidebar__sub">SERVIALCO</div>
      </div>
    </div>

    {% if 'general' in modulos_visibles or 'hitos' in modulos_visibles %}
    <nav class="sidebar__group" aria-label="General">
      <div class="sidebar__group-label">General</div>

      {% if 'general' in modulos_visibles %}
      <a href="{{ url_for('dashboard.general') }}"
         class="sidebar__item {% if request.endpoint == 'dashboard.general' %}is-active{% endif %}">
        <span class="sidebar__icon" aria-hidden="true">📋</span>
        Datos del Contrato
      </a>
      {% endif %}

      {% if 'hitos' in modulos_visibles %}
      <a href="{{ url_for('dashboard.hitos') }}"
         class="sidebar__item {% if request.endpoint == 'dashboard.hitos' %}is-active{% endif %}">
        <span class="sidebar__icon" aria-hidden="true">🏁</span>
        Hitos
      </a>
      {% endif %}
    </nav>
    {% endif %}

    {% if 'encuestas' in modulos_visibles %}
    <nav class="sidebar__group" aria-label="Encuestas">
      <div class="sidebar__group-label">Encuestas</div>
      <a href="{{ url_for('dashboard.encuestas') }}"
         class="sidebar__item {% if request.endpoint == 'dashboard.encuestas' %}is-active{% endif %}">
        <span class="sidebar__icon" aria-hidden="true">📊</span>
        Registros
      </a>
    </nav>
    {% endif %}

    {% if 'instalaciones' in modulos_visibles %}
    <nav class="sidebar__group" aria-label="Instalaciones">
      <div class="sidebar__group-label">Instalaciones</div>
      <a href="{{ url_for('dashboard.instalaciones') }}"
         class="sidebar__item {% if request.endpoint == 'dashboard.instalaciones' %}is-active{% endif %}">
        <span class="sidebar__icon" aria-hidden="true">🔧</span>
        Registros
      </a>
    </nav>
    {% endif %}

  </aside><!-- /sidebar -->

  <!-- ══ ÁREA PRINCIPAL ═══════════════════════════════════ -->
  <div class="main-area">

    <!-- Topbar -->
    <header class="topbar" role="banner">

      <!-- Hamburger (solo móvil) -->
      <button id="hamburger" class="hamburger" aria-label="Abrir menú" aria-expanded="false">☰</button>

      <div class="topbar__left">
        <!-- Selector de contrato -->
        {% if contratos_lista %}
        <select id="contrato-selector"
                class="contrato-selector"
                name="contrato_id"
                {% if contratos_lista|length <= 1 %}disabled{% endif %}
                hx-post="{{ url_for('api.set_contrato') }}"
                hx-trigger="change"
                hx-swap="none">
          {% for c in contratos_lista %}
          <option value="{{ c.id }}" {% if c.id == contrato_activo_id %}selected{% endif %}>
            {{ c.nombre }}
          </option>
          {% endfor %}
        </select>
        {% endif %}

        <!-- Breadcrumbs -->
        <nav class="topbar__breadcrumb" aria-label="Ruta de navegación">
          <span>Panel</span>
          <span aria-hidden="true">›</span>
          <span class="current">{% block breadcrumb %}Inicio{% endblock %}</span>
        </nav>
      </div>

      <div class="topbar__right">

        <!-- Toggle modo oscuro -->
        <button id="theme-toggle"
                class="theme-toggle"
                aria-label="Cambiar a modo oscuro"
                title="Alternar modo oscuro">
          🌙
        </button>

        <!-- Menú de usuario -->
        <div class="user-menu">
          <button id="user-menu-trigger"
                  class="user-menu__trigger"
                  aria-haspopup="true"
                  aria-expanded="false">
            <div class="user-menu__avatar" aria-hidden="true">
              {{ (current_user_nombre or 'U')[:1].upper() }}
            </div>
            <span class="user-menu__name">{{ current_user_nombre }}</span>
            <span aria-hidden="true">▾</span>
          </button>

          <div id="user-menu-dropdown" class="user-menu__dropdown" role="menu">
            <div style="padding: 0.75rem 1rem; border-bottom: 1px solid var(--color-border);">
              <div style="font-weight:600; font-size: var(--text-sm);">{{ current_user_nombre }}</div>
              <div style="font-size: var(--text-xs); color: var(--color-text-muted); text-transform:capitalize;">{{ current_user_rol }}</div>
            </div>

            <button id="btn-cambiar-contrasena"
                    class="user-menu__dropdown-item"
                    role="menuitem"
                    type="button">
              🔑 Cambiar contraseña
            </button>

            <div class="user-menu__dropdown-divider"></div>

            <form method="POST" action="{{ url_for('auth.logout') }}" style="margin:0;">
              <button type="submit"
                      class="user-menu__dropdown-item user-menu__dropdown-item--danger"
                      role="menuitem">
                🚪 Cerrar sesión
              </button>
            </form>
          </div>
        </div><!-- /user-menu -->

      </div><!-- /topbar__right -->
    </header><!-- /topbar -->

    <!-- Mensajes flash globales -->
    {% with messages = get_flashed_messages(with_categories=true) %}
      {% if messages %}
      <div style="padding: 0 2rem;">
        {% for category, message in messages %}
        <div class="alert alert--{{ 'error' if category == 'error' else category }}">
          {{ message }}
        </div>
        {% endfor %}
      </div>
      {% endif %}
    {% endwith %}

    <!-- Contenido de página -->
    <main id="main-content" class="content-area" role="main">
      {% block content %}{% endblock %}
    </main>

  </div><!-- /main-area -->

</div><!-- /app-layout -->

<!-- ══ MODAL: Cambiar contraseña ════════════════════════════ -->
<div id="modal-password" class="modal-backdrop" role="dialog" aria-modal="true" aria-labelledby="modal-password-title">
  <div class="modal">
    <div class="modal__header">
      <h2 id="modal-password-title" class="modal__title">Cambiar contraseña</h2>
      <button id="modal-password-close" class="modal__close" aria-label="Cerrar">✕</button>
    </div>

    <form method="POST" action="{{ url_for('auth.cambiar_contrasena') }}">
      <div class="modal__body">
        <div class="form-group">
          <label for="current_password" class="form-label">Contraseña actual</label>
          <input type="password" id="current_password" name="current_password"
                 class="form-input" autocomplete="current-password" required>
        </div>
        <div class="form-group">
          <label for="new_password" class="form-label">Nueva contraseña</label>
          <input type="password" id="new_password" name="new_password"
                 class="form-input" autocomplete="new-password"
                 minlength="8" required>
        </div>
        <div class="form-group">
          <label for="confirm_password" class="form-label">Confirmar nueva contraseña</label>
          <input type="password" id="confirm_password" name="confirm_password"
                 class="form-input" autocomplete="new-password"
                 minlength="8" required>
        </div>
      </div>
      <div class="modal__footer">
        <button type="button" class="btn btn--ghost" onclick="document.getElementById('modal-password').classList.remove('is-open')">
          Cancelar
        </button>
        <button type="submit" class="btn btn--primary">Guardar contraseña</button>
      </div>
    </form>

  </div>
</div><!-- /modal-password -->

{% block extra_scripts %}{% endblock %}
</body>
</html>
```

- [ ] **Step 2: Verificar que Flask puede cargar el template (no hay imports rotos)**

```powershell
python -c "
from app import create_app
app = create_app()
with app.test_request_context('/'):
    from flask import render_template, session
    session['user_id'] = 'x'
    session['rol'] = 'administrador'
    session['nombre'] = 'Test'
    session['modulos_visibles'] = ['general','hitos','encuestas','instalaciones']
    session['contratos_lista'] = [{'id':'c1','nombre':'Contrato A'}]
    session['contrato_activo_id'] = 'c1'
    print('base.html OK')
"
```

> Si lanza `BuildError` por rutas no registradas aún (dashboard.*), es esperado — se corrige en Fase 5.

- [ ] **Step 3: Correr suite de tests**

```powershell
python -m pytest tests/ -v --tb=short
```

Esperado: `31 passed, 0 failed`

- [ ] **Step 4: Commit**

```powershell
git add app/templates/base.html
git commit -m "feat: add complete app shell (sidebar, topbar, contract selector, password modal)"
```

---

## Verificación final de Fase 4

- [ ] **Suite completa sin regresiones**

```powershell
python -m pytest tests/ -v --tb=short
```

Esperado: `31 passed, 0 failed`

---

**Fase 4 completada. Continuar con Fase 5: Dashboard modules.**
