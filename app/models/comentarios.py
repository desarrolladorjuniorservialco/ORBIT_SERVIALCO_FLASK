from app.utils.supabase_client import get_data_client

TIPOS_VALIDOS = ('global', 'encuesta', 'instalacion', 'hito')


def get_comentarios(
    contrato_id: str,
    tipo: str,
    referencia_id: str | None = None,
) -> list[dict]:
    client = get_data_client()
    query = (
        client.table('comentarios')
        .select('id, contenido, tipo, referencia_id, created_at, usuarios(nombre_completo)')
        .eq('contrato_id', contrato_id)
        .eq('tipo', tipo)
    )
    if referencia_id:
        query = query.eq('referencia_id', referencia_id)
    else:
        query = query.is_('referencia_id', 'null')

    resp = query.order('created_at').execute()
    return resp.data or []


def create_comentario(
    contrato_id: str,
    autor_id: str,
    tipo: str,
    contenido: str,
    referencia_id: str | None = None,
) -> dict:
    if tipo not in TIPOS_VALIDOS:
        raise ValueError(f'Tipo inválido: {tipo}. Permitidos: {TIPOS_VALIDOS}')
    client = get_data_client()
    payload = {
        'contrato_id': contrato_id,
        'autor_id': autor_id,
        'tipo': tipo,
        'contenido': contenido.strip(),
        'referencia_id': referencia_id,
    }
    resp = client.table('comentarios').insert(payload).execute()
    return resp.data[0] if resp.data else {}
