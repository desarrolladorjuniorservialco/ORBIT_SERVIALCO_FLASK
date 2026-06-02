import math
from flask import request, session, render_template, make_response, abort, url_for, jsonify
from app.api import bp
from app.utils.auth import login_required, role_required
from app.models.comentarios import get_comentarios as get_comentarios_db
from app.models.comentarios import create_comentario as create_comentario_db
from app.models.encuestas import get_encuestas as get_encuestas_db
from app.models.encuestas import delete_encuesta as delete_encuesta_db
from app.models.instalaciones import get_instalaciones as get_instalaciones_db
from app.models.instalaciones import delete_instalacion as delete_instalacion_db
from app.models.hitos import update_estado_hito as update_estado_hito_db
from app.models.mapa_hitos import get_geo_reportes as get_geo_reportes_db

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


# ── Geo: reportes con coordenadas ──────────────────────────

@bp.route('/geo-reportes', methods=['GET'])
@login_required
def get_geo_reportes():
    contrato_id = session.get('contrato_activo_id')
    if not contrato_id:
        return jsonify([])
    return jsonify(get_geo_reportes_db(contrato_id))

