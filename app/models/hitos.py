from app.utils.supabase_client import get_data_client

ESTADOS_VALIDOS = ('pendiente', 'en_revision', 'aprobado')


def get_hitos(contrato_id: str) -> list[dict]:
    client = get_data_client()
    if client is None:
        return []
    resp = (
        client.table('hitos')
        .select('id, nombre, descripcion, fecha_limite, estado, archivo_url')
        .eq('contrato_id', contrato_id)
        .order('fecha_limite')
        .execute()
    )
    return resp.data or []


def update_estado_hito(hito_id: str, estado: str) -> dict:
    if estado not in ESTADOS_VALIDOS:
        raise ValueError(f'Estado inválido: {estado}. Valores permitidos: {ESTADOS_VALIDOS}')
    client = get_data_client()
    if client is None:
        return {}
    resp = (
        client.table('hitos')
        .update({'estado': estado})
        .eq('id', hito_id)
        .execute()
    )
    return resp.data[0] if resp.data else {}
