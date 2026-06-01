from datetime import date
from flask import render_template, session, abort
from app.dashboard import bp
from app.utils.auth import login_required
from app.models.contratos import get_contrato, calcular_progreso_tiempo
from app.models.hitos import get_hitos


@bp.route('/dashboard/general')
@login_required
def general():
    if 'general' not in session.get('modulos_visibles', []):
        abort(403)

    contrato_id = session.get('contrato_activo_id')
    contrato = get_contrato(contrato_id) if contrato_id else None

    progreso_tiempo = 0.0
    if contrato and contrato.get('fecha_inicio') and contrato.get('fecha_fin'):
        inicio = date.fromisoformat(str(contrato['fecha_inicio']))
        fin = date.fromisoformat(str(contrato['fecha_fin']))
        progreso_tiempo = calcular_progreso_tiempo(inicio, fin)

    progreso_ejecutado = float(contrato.get('porcentaje_ejecutado', 0)) if contrato else 0.0

    return render_template(
        'dashboard/general.html',
        contrato=contrato,
        progreso_tiempo=progreso_tiempo,
        progreso_ejecutado=progreso_ejecutado,
    )


@bp.route('/dashboard/hitos')
@login_required
def hitos():
    if 'hitos' not in session.get('modulos_visibles', []):
        abort(403)

    contrato_id = session.get('contrato_activo_id')
    hitos_list = get_hitos(contrato_id) if contrato_id else []

    return render_template('dashboard/hitos.html', hitos=hitos_list)


@bp.route('/dashboard/encuestas')
@login_required
def encuestas():
    if 'encuestas' not in session.get('modulos_visibles', []):
        abort(403)
    return render_template('dashboard/encuestas.html')


@bp.route('/dashboard/instalaciones')
@login_required
def instalaciones():
    if 'instalaciones' not in session.get('modulos_visibles', []):
        abort(403)
    return render_template('dashboard/instalaciones.html')
