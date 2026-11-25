from app.model.patrocinador_model import PatrocinadorModel


def _modelo():
    modelo = PatrocinadorModel()
    modelo.set_nombre_empresa('Empresa Prueba')
    modelo.set_rif('J-12345678')
    modelo.set_tipo_contrato('1')
    modelo.set_encargado_id(1)
    modelo.set_email('contacto@empresa.com')
    return modelo


def test_patrocinador_valido():
    assert _modelo()._validar_datos_patrocinador() is True


def test_patrocinador_con_rif_invalido():
    modelo = _modelo()
    modelo.set_rif('123')
    assert modelo._validar_datos_patrocinador() is False
