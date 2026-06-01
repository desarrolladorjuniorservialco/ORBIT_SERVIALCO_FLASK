from flask import render_template, redirect, url_for, request, session, flash
from app.auth import bp
from app.utils.supabase_client import get_auth_client, get_data_client
from app.utils.auth import login_required
from app.models.usuarios import get_usuario, get_modulos_visibles, get_contratos_by_user


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('dashboard.general'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()

        if not email or not password:
            flash('Email y contraseña son requeridos', 'error')
            return render_template('auth/login.html')

        # ── Usuario de prueba local (sin Supabase) ─────────────
        DEV_EMAIL = 'admin@orbit.local'
        DEV_PASSWORD = 'orbit1234'
        if email == DEV_EMAIL and password == DEV_PASSWORD:
            session.clear()
            session['user_id'] = 'dev-user-id'
            session['email'] = DEV_EMAIL
            session['nombre'] = 'Admin Local'
            session['rol'] = 'administrador'
            session['access_token'] = 'dev-token'
            session['refresh_token'] = 'dev-refresh'
            session['contratos_lista'] = [{'id': 'dev-contrato-id', 'nombre': 'Contrato Demo'}]
            session['contrato_activo_id'] = 'dev-contrato-id'
            session['modulos_visibles'] = ['general', 'hitos', 'encuestas', 'instalaciones']
            return redirect(url_for('dashboard.general'))
        # ───────────────────────────────────────────────────────

        try:
            auth_client = get_auth_client()
            resp = auth_client.auth.sign_in_with_password(
                {'email': email, 'password': password}
            )
            user_id = resp.user.id
            access_token = resp.session.access_token
            refresh_token = resp.session.refresh_token

            usuario = get_usuario(user_id)
            if not usuario or not usuario.get('activo'):
                flash('Usuario inactivo o no encontrado', 'error')
                return render_template('auth/login.html')

            rol = usuario['rol']
            contratos = get_contratos_by_user(user_id, rol)
            modulos = get_modulos_visibles(rol)

            session.clear()
            session['user_id'] = user_id
            session['email'] = email
            session['nombre'] = usuario['nombre_completo']
            session['rol'] = rol
            session['access_token'] = access_token
            session['refresh_token'] = refresh_token
            session['contratos_lista'] = contratos
            session['contrato_activo_id'] = contratos[0]['id'] if contratos else None
            session['modulos_visibles'] = modulos

            return redirect(url_for('dashboard.general'))

        except Exception:
            flash('Credenciales incorrectas', 'error')
            return render_template('auth/login.html')

    return render_template('auth/login.html')


@bp.route('/logout', methods=['POST'])
@login_required
def logout():
    try:
        auth_client = get_auth_client()
        auth_client.auth.set_session(
            session.get('access_token', ''),
            session.get('refresh_token', ''),
        )
        auth_client.auth.sign_out()
    except Exception:
        pass
    session.clear()
    return redirect(url_for('auth.login'))


@bp.route('/cambiar-contrasena', methods=['POST'])
@login_required
def cambiar_contrasena():
    current_password = request.form.get('current_password', '')
    new_password = request.form.get('new_password', '')
    confirm_password = request.form.get('confirm_password', '')
    redirect_to = request.referrer or url_for('dashboard.general')

    if new_password != confirm_password:
        flash('Las contraseñas nuevas no coinciden', 'error')
        return redirect(redirect_to)

    if len(new_password) < 8:
        flash('La contraseña debe tener al menos 8 caracteres', 'error')
        return redirect(redirect_to)

    try:
        auth_client = get_auth_client()
        auth_client.auth.sign_in_with_password(
            {'email': session['email'], 'password': current_password}
        )
        auth_client.auth.set_session(
            session['access_token'],
            session['refresh_token'],
        )
        auth_client.auth.update_user({'password': new_password})
        flash('Contraseña actualizada exitosamente', 'success')
    except Exception:
        flash('Contraseña actual incorrecta', 'error')

    return redirect(redirect_to)
