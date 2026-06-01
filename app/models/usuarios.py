from app.utils.supabase_client import get_data_client


def get_usuario(user_id: str) -> dict | None:
    client = get_data_client()
    if client is None:
        return None
    resp = (
        client.table('usuarios')
        .select('id, nombre_completo, rol, activo')
        .eq('id', user_id)
        .single()
        .execute()
    )
    return resp.data


def get_modulos_visibles(rol: str) -> list[str]:
    client = get_data_client()
    if client is None:
        return []
    resp = (
        client.table('rol_permisos')
        .select('modulo')
        .eq('rol', rol)
        .eq('visible', True)
        .execute()
    )
    return [row['modulo'] for row in (resp.data or [])]


def get_contratos_by_user(user_id: str, rol: str) -> list[dict]:
    client = get_data_client()
    if client is None:
        return []
    if rol == 'administrador':
        resp = client.table('contratos').select('id, nombre').execute()
        return resp.data or []
    resp = (
        client.table('usuarios_contratos')
        .select('contrato_id, contratos(id, nombre)')
        .eq('user_id', user_id)
        .execute()
    )
    return [row['contratos'] for row in (resp.data or []) if row.get('contratos')]
