from app.utils.supabase_client import get_data_client

FORMULARIOS_GEO = [
    {'tabla': 'f01_encuestas',             'id_campo': 'id_encuesta',          'label': 'F01 Encuestas',       'key': 'f01', 'extras': 'municipio, estado'},
    {'tabla': 'f02_infraestructura',       'id_campo': 'id_infraestructura',   'label': 'F02 Infraestructura', 'key': 'f02', 'extras': 'municipio, estado'},
    {'tabla': 'f03_tss_nodos',             'id_campo': 'id_nodo',              'label': 'F03 TSS Nodos',       'key': 'f03', 'extras': 'municipio, estado'},
    {'tabla': 'f04_pruebas_maat',          'id_campo': 'id_maat',              'label': 'F04 MAAT',            'key': 'f04', 'extras': 'estado'},
    {'tabla': 'f06_enrutamiento',          'id_campo': 'id_enrutamiento',      'label': 'F06 Enrutamiento',    'key': 'f06', 'extras': 'estado'},
    {'tabla': 'f07_instalaciones_tendido', 'id_campo': 'id_control_operativo', 'label': 'F07 Tendido',         'key': 'f07', 'extras': 'municipio, estado'},
    {'tabla': 'f08_instalaciones_empalmes','id_campo': 'id_ficha_empalme',     'label': 'F08 Empalmes',        'key': 'f08', 'extras': 'departamento, estado'},
    {'tabla': 'f09_instalaciones_ont',     'id_campo': 'id_instalacion_ont',   'label': 'F09 ONT',             'key': 'f09', 'extras': 'tramo, estado'},
    {'tabla': 'f10_instalaciones_nap',     'id_campo': 'id_instalacion_nap',   'label': 'F10 NAP',             'key': 'f10', 'extras': 'tramo, estado'},
]


def get_geo_reportes(contrato_id: str) -> list[dict]:
    client = get_data_client()
    if client is None:
        return []

    result = []
    for f in FORMULARIOS_GEO:
        campos = f'id, {f["id_campo"]}, latitud, longitud, {f["extras"]}'
        try:
            resp = (
                client.table(f['tabla'])
                .select(campos)
                .eq('contrato_id', contrato_id)
                .execute()
            )
            for row in (resp.data or []):
                lat = row.get('latitud')
                lon = row.get('longitud')
                if lat is None or lon is None:
                    continue
                try:
                    lat, lon = float(lat), float(lon)
                except (TypeError, ValueError):
                    continue
                result.append({
                    'tipo_key':   f['key'],
                    'tipo_label': f['label'],
                    'ref':        str(row.get(f['id_campo']) or ''),
                    'lat':        lat,
                    'lon':        lon,
                    'municipio':  row.get('municipio') or row.get('departamento') or '',
                    'estado':     row.get('estado') or '',
                })
        except Exception:
            pass

    return result


def get_mf_bd(contrato_id: str) -> list[dict]:
    client = get_data_client()
    if client is None:
        return []
    resp = (
        client.table('mf_bd')
        .select('id_municipio, municipio_descripcion, mf_tipo, mf_codigo, meta_fisica_prog, meta_fisica_ejec')
        .eq('contrato_id', contrato_id)
        .order('id_municipio')
        .execute()
    )
    return resp.data or []


def get_mf_aux(contrato_id: str) -> list[dict]:
    client = get_data_client()
    if client is None:
        return []
    resp = (
        client.table('mf_aux')
        .select('codigo, descripcion')
        .eq('contrato_id', contrato_id)
        .execute()
    )
    return resp.data or []


def build_municipios(mf_bd_raw: list[dict]) -> list[dict]:
    municipios_dict: dict = {}
    for row in mf_bd_raw:
        key = row['id_municipio']
        if key not in municipios_dict:
            municipios_dict[key] = {
                'id':         key,
                'nombre':     row.get('municipio_descripcion') or f'Municipio {key}',
                'tipos':      [],
                'total_prog': 0.0,
                'total_ejec': 0.0,
            }
        prog = float(row.get('meta_fisica_prog') or 0)
        ejec = float(row.get('meta_fisica_ejec') or 0)
        municipios_dict[key]['tipos'].append({
            'mf_tipo':   row['mf_tipo'],
            'mf_codigo': row.get('mf_codigo') or '',
            'prog':      prog,
            'ejec':      ejec,
            'avance':    round((ejec / prog * 100) if prog > 0 else 0.0, 1),
        })
        municipios_dict[key]['total_prog'] += prog
        municipios_dict[key]['total_ejec'] += ejec

    result = []
    for m in municipios_dict.values():
        tp = m['total_prog']
        te = m['total_ejec']
        m['total_avance'] = round((te / tp * 100) if tp > 0 else 0.0, 1)
        result.append(m)
    return result
