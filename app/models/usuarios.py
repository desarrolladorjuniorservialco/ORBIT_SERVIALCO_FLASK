from app.utils.supabase_client import get_data_client

_MODULOS_POR_ROL = {
    'admin':        ['general', 'hitos', 'encuestas_sociodemograficas', 'infraestructura',
                     'tss_nodos', 'enrutamiento', 'tendido', 'empalme',
                     'instalaciones_ont', 'instalaciones_nap'],
    'encargado':    ['general', 'hitos', 'encuestas_sociodemograficas', 'infraestructura',
                     'tss_nodos', 'enrutamiento', 'tendido', 'empalme',
                     'instalaciones_ont', 'instalaciones_nap'],
    'supervisión':  ['general', 'hitos', 'encuestas_sociodemograficas', 'infraestructura',
                     'tss_nodos', 'enrutamiento', 'tendido', 'empalme',
                     'instalaciones_ont', 'instalaciones_nap'],
    'operativo':    ['general', 'hitos', 'encuestas_sociodemograficas', 'infraestructura',
                     'tss_nodos', 'enrutamiento', 'tendido', 'empalme',
                     'instalaciones_ont', 'instalaciones_nap'],
    'visualizador': ['general', 'hitos', 'encuestas_sociodemograficas', 'infraestructura',
                     'tss_nodos', 'enrutamiento', 'tendido', 'empalme',
                     'instalaciones_ont', 'instalaciones_nap'],
}


def get_usuario(user_id: str) -> dict | None:
    client = get_data_client()
    if client is None:
        return None
    resp = (
        client.table('perfiles')
        .select('id, nombre, rol, activo')
        .eq('id', user_id)
        .single()
        .execute()
    )
    return resp.data


def get_modulos_visibles(rol: str) -> list[str]:
    return _MODULOS_POR_ROL.get(rol, [])


def get_contratos_by_user(user_id: str, rol: str) -> list[dict]:
    client = get_data_client()
    if client is None:
        return []
    if rol == 'admin':
        resp = client.table('contratos').select('id, nombre').execute()
        return resp.data or []
    resp = (
        client.table('perfiles')
        .select('contrato_id, contratos(id, nombre)')
        .eq('id', user_id)
        .single()
        .execute()
    )
    if resp.data and resp.data.get('contratos'):
        return [resp.data['contratos']]
    return []
