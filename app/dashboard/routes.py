from datetime import date
from flask import render_template, session, abort
from app.dashboard import bp
from app.utils.auth import login_required
from app.models.contratos import (
    get_contrato,
    calcular_progreso_tiempo,
    get_prorrogas_resumen,
    get_adiciones_resumen,
)
from app.models.hitos import get_hitos


@bp.route('/dashboard/general')
@login_required
def general():
    if 'general' not in session.get('modulos_visibles', []):
        abort(403)

    contrato_id = session.get('contrato_activo_id')
    contrato = get_contrato(contrato_id) if contrato_id else None
    prorrogas = get_prorrogas_resumen(contrato_id) if contrato_id else {'count': 0, 'plazo_actual': None}
    adiciones = get_adiciones_resumen(contrato_id) if contrato_id else {'count': 0, 'valor_actual': None}

    progreso_tiempo = 0.0
    if contrato and contrato.get('fecha_inicio'):
        fecha_limite = contrato.get('plazo_actual') or contrato.get('fecha_fin')
        if fecha_limite:
            inicio = date.fromisoformat(str(contrato['fecha_inicio']))
            fin = date.fromisoformat(str(fecha_limite))
            progreso_tiempo = calcular_progreso_tiempo(inicio, fin)

    return render_template(
        'dashboard/general.html',
        contrato=contrato,
        prorrogas=prorrogas,
        adiciones=adiciones,
        progreso_tiempo=progreso_tiempo,
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


# ── Levantamiento ──────────────────────────────────────────

@bp.route('/dashboard/levantamiento/encuestas')
@login_required
def encuestas_sociodemograficas():
    if 'encuestas_sociodemograficas' not in session.get('modulos_visibles', []):
        abort(403)
    return render_template('dashboard/encuestas_sociodemograficas.html')


@bp.route('/dashboard/levantamiento/infraestructura')
@login_required
def infraestructura():
    if 'infraestructura' not in session.get('modulos_visibles', []):
        abort(403)
    return render_template('dashboard/infraestructura.html')


@bp.route('/dashboard/levantamiento/tss-nodos')
@login_required
def tss_nodos():
    if 'tss_nodos' not in session.get('modulos_visibles', []):
        abort(403)
    return render_template('dashboard/tss_nodos.html')


# ── Instalaciones (detalle) ────────────────────────────────

@bp.route('/dashboard/instalaciones/enrutamiento')
@login_required
def enrutamiento():
    if 'enrutamiento' not in session.get('modulos_visibles', []):
        abort(403)
    return render_template('dashboard/enrutamiento.html')


@bp.route('/dashboard/instalaciones/tendido')
@login_required
def tendido():
    if 'tendido' not in session.get('modulos_visibles', []):
        abort(403)
    return render_template('dashboard/tendido.html')


@bp.route('/dashboard/instalaciones/empalme')
@login_required
def empalme():
    if 'empalme' not in session.get('modulos_visibles', []):
        abort(403)
    return render_template('dashboard/empalme.html')


@bp.route('/dashboard/instalaciones/ont')
@login_required
def instalaciones_ont():
    if 'instalaciones_ont' not in session.get('modulos_visibles', []):
        abort(403)
    return render_template('dashboard/instalaciones_ont.html')


@bp.route('/dashboard/instalaciones/nap')
@login_required
def instalaciones_nap():
    if 'instalaciones_nap' not in session.get('modulos_visibles', []):
        abort(403)
    return render_template('dashboard/instalaciones_nap.html')
