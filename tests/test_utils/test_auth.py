import pytest
from flask import Flask, session


def make_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'test-secret'
    app.config['TESTING'] = True

    # Stub para que url_for('auth.login') funcione en tests aislados
    from flask import Blueprint
    auth_bp = Blueprint('auth', __name__)

    @auth_bp.route('/login')
    def login():
        return 'login'

    app.register_blueprint(auth_bp)
    return app


def test_login_required_redirects_when_no_session():
    app = make_app()
    from app.utils.auth import login_required

    @app.route('/protected')
    @login_required
    def protected():
        return 'OK'

    with app.test_client() as c:
        resp = c.get('/protected')
        assert resp.status_code == 302
        assert '/login' in resp.headers['Location']


def test_login_required_allows_authenticated():
    app = make_app()
    from app.utils.auth import login_required

    @app.route('/protected')
    @login_required
    def protected():
        return 'OK'

    with app.test_client() as c:
        with c.session_transaction() as sess:
            sess['user_id'] = 'abc-123'
        resp = c.get('/protected')
        assert resp.status_code == 200
        assert resp.data == b'OK'


def test_role_required_allows_correct_role():
    app = make_app()
    from app.utils.auth import login_required, role_required

    @app.route('/admin')
    @login_required
    @role_required('administrador')
    def admin_only():
        return 'ADMIN'

    with app.test_client() as c:
        with c.session_transaction() as sess:
            sess['user_id'] = 'abc-123'
            sess['rol'] = 'administrador'
        resp = c.get('/admin')
        assert resp.status_code == 200


def test_role_required_returns_403_for_wrong_role():
    app = make_app()
    from app.utils.auth import login_required, role_required

    @app.route('/admin')
    @login_required
    @role_required('administrador')
    def admin_only():
        return 'ADMIN'

    with app.test_client() as c:
        with c.session_transaction() as sess:
            sess['user_id'] = 'abc-123'
            sess['rol'] = 'operativo'
        resp = c.get('/admin')
        assert resp.status_code == 403
