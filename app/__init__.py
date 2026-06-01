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

    from app.api import bp as api_bp
    app.register_blueprint(api_bp)

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
