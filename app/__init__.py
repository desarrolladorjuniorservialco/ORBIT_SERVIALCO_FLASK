from flask import Flask
from config import Config


def create_app(config_object=None):
    app = Flask(__name__)

    if isinstance(config_object, dict):
        app.config.from_object(Config)
        app.config.update(config_object)
    else:
        app.config.from_object(config_object or Config)

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp)

    # Ruta raíz — redirige según sesión
    from flask import session, redirect, url_for

    @app.route('/')
    def index():
        if 'user_id' in session:
            return redirect(url_for('dashboard.general'))
        return redirect(url_for('auth.login'))

    # Context processor — datos disponibles en todos los templates
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

    return app
