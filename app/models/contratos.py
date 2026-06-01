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


def update_porcentaje_ejecutado(contrato_id: str, porcentaje: float) -> dict:
    client = get_data_client()
    if client is None:
        return {}
    resp = (
        client.table('contratos')
        .update({'porcentaje_ejecutado': porcentaje})
        .eq('id', contrato_id)
        .execute()
    )
    return resp.data[0] if resp.data else {}
