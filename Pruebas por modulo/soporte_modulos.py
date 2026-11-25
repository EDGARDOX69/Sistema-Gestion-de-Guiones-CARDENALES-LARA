"""Rutas y metadatos compartidos por las pruebas de cada modulo."""

MODULOS = {
    'auth': {'ruta': '/auth/login', 'publica': True},
    'balance': {'ruta': '/balance/', 'publica': False},
    'bitacora': {'ruta': '/bitacora/', 'publica': False},
    'chat': {'ruta': '/asistente/', 'publica': False},
    'contrato': {'ruta': '/contratos/', 'publica': False},
    'dashboard': {'ruta': '/dashboard', 'publica': False},
    'en_vivo': {'ruta': '/en-vivo/', 'publica': False},
    'gestion_tarea': {'ruta': '/gestion-tarea/', 'publica': False},
    'guion': {'ruta': '/guiones/', 'publica': False},
    'inventario': {'ruta': '/inventario/', 'publica': False},
    'mantenimiento': {'ruta': '/mantenimiento/', 'publica': False},
    'notificaciones': {'ruta': '/notificaciones/api', 'publica': False},
    'patrocinador': {'ruta': '/patrocinador/', 'publica': False},
    'premio': {'ruta': '/premio/', 'publica': False},
    'reels': {'ruta': '/reels/', 'publica': False},
    'reportes': {'ruta': '/reportes/', 'publica': False},
    'rol': {'ruta': '/roles/', 'publica': False},
    'usuario': {'ruta': '/usuarios/', 'publica': False},
}

RUTA_INTERFAZ = {
    **{modulo: datos['ruta'] for modulo, datos in MODULOS.items()},
    'notificaciones': '/dashboard',
}


def ruta(modulo):
    return MODULOS[modulo]['ruta']


def es_publica(modulo):
    return MODULOS[modulo]['publica']
