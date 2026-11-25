from app.model.rol_model import PERMISOS_CATALOGO, PERMISOS_POR_ROL


def test_permiso_de_reportes_en_catalogo():
    codigos = {permiso['codigo'] for permiso in PERMISOS_CATALOGO}
    assert 'reportes.view' in codigos


def test_administrador_recibe_permiso_de_reportes():
    assert 'reportes.view' in PERMISOS_POR_ROL['Administrador']
