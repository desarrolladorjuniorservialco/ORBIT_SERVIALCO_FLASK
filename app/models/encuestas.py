from app.utils.supabase_client import get_data_client


def get_encuestas(
    contrato_id: str,
    page: int = 1,
    per_page: int = 25,
    filtros: dict | None = None,
) -> tuple[list[dict], int]:
    client = get_data_client()
    if client is None:
        return [], 0
    offset = (page - 1) * per_page

    query = (
        client.table('encuestas')
        .select('*', count='exact')
        .eq('contrato_id', contrato_id)
    )

    if filtros:
        for campo, valor in filtros.items():
            if valor:
                query = query.ilike(campo, f'%{valor}%')

    resp = query.range(offset, offset + per_page - 1).execute()
    return resp.data or [], resp.count or 0


def delete_encuesta(encuesta_id: str) -> bool:
    client = get_data_client()
    if client is None:
        return False
    resp = client.table('encuestas').delete().eq('id', encuesta_id).execute()
    return bool(resp.data)
