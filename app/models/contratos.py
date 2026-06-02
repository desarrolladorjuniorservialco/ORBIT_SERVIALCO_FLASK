from datetime import date
from app.utils.supabase_client import get_data_client


def get_contrato(contrato_id: str) -> dict | None:
    client = get_data_client()
    if client is None:
        return None
    resp = (
        client.table('contratos')
        .select('*')
        .eq('id', contrato_id)
        .single()
        .execute()
    )
    return resp.data


def calcular_progreso_tiempo(
    fecha_inicio: date,
    fecha_fin: date,
    hoy: date | None = None,
) -> float:
    if hoy is None:
        hoy = date.today()
    if hoy <= fecha_inicio:
        return 0.0
    if hoy >= fecha_fin:
        return 100.0
    total = (fecha_fin - fecha_inicio).days
    transcurrido = (hoy - fecha_inicio).days
    return round((transcurrido / total) * 100, 1)


def get_prorrogas_resumen(contrato_id: str) -> dict:
    client = get_data_client()
    if client is None:
        return {'count': 0, 'plazo_actual': None}
    resp = (
        client.table('contratos_prorrogas')
        .select('numero, fecha_fin')
        .eq('contrato_id', contrato_id)
        .order('numero')
        .execute()
    )
    rows = resp.data or []
    ultima = rows[-1] if rows else None
    return {
        'count': len(rows),
        'plazo_actual': ultima['fecha_fin'] if ultima else None,
    }


def get_adiciones_resumen(contrato_id: str) -> dict:
    client = get_data_client()
    if client is None:
        return {'count': 0, 'valor_actual': None}
    resp = (
        client.table('contratos_adiciones')
        .select('numero, valor_actual')
        .eq('contrato_id', contrato_id)
        .order('numero')
        .execute()
    )
    rows = resp.data or []
    ultima = rows[-1] if rows else None
    return {
        'count': len(rows),
        'valor_actual': ultima['valor_actual'] if ultima else None,
    }
