document.addEventListener('DOMContentLoaded', () => {

  // ── Lucide icons ───────────────────────────────────────
  if (window.lucide) {
    lucide.createIcons();
    document.body.addEventListener('htmx:afterSettle', () => lucide.createIcons());
  }

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
