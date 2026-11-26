# python -m pytest test/unitarias/test_premio_unitaria.py -v

import pytest
from unittest.mock import MagicMock, call, patch
from app.model.premio_model import PremioModel


def test_validacion_datos_premio_exitosa():
    modelo = PremioModel()
    modelo.set_nombre("Camiseta Oficial")
    modelo.set_id_patrocinador(1)
    modelo.set_descripcion("Camiseta talla L edición especial")
    modelo.set_cantidad(10)
    assert modelo._validar_datos_premio() is True

def test_validacion_datos_premio_falla_sin_nombre_o_patrocinador():
    modelo = PremioModel()
    modelo.set_nombre("")
    modelo.set_id_patrocinador(None)
    assert modelo._validar_datos_premio() is False

def test_validacion_longitud_nombre_invalida():
    modelo = PremioModel()
    modelo.set_nombre("A")  # Mínimo 2 caracteres
    modelo.set_id_patrocinador(1)
    assert modelo._validar_datos_premio() is False

def test_set_cantidad_ajusta_minimo_a_uno():
    modelo = PremioModel()
    modelo.set_cantidad(-5)
    modelo.set_nombre("Gorra")
    modelo.set_id_patrocinador(2)
    assert modelo._validar_datos_premio() is True

def test_entregar_calcula_stock_y_cambia_estado_a_entregado():
    modelo = PremioModel()
    mock_db = MagicMock()
    mock_cursor = MagicMock()
    mock_db.cursor.return_value.__enter__.return_value = mock_cursor
    # Simula un premio con cantidad=5 y cantidad_entregada=3 (quedan 2)
    mock_cursor.fetchone.return_value = {"cantidad": 5, "cantidad_entregada": 3}
    mock_cursor.rowcount = 1

    with patch.object(modelo, "_get_db", return_value=mock_db):
        # Intentamos entregar 5, pero el modelo debe limitar al restante (2) y marcar 'entregado'
        resultado = modelo.entregar(premio_id=1, id_patrocinador=1, descripcion="Entrega final", entregado_por=1, cantidad_entregar=5)
        assert resultado is True
        args_update = mock_cursor.execute.call_args_list[1][0][1]
        assert args_update[0] == 5            # nueva_entregada = 3 + 2 = 5
        assert args_update[1] == "entregado"  # Estado cambia automáticamente

def _premio_valido():
    modelo = PremioModel()
    modelo.set_nombre("Camiseta Oficial")
    modelo.set_id_patrocinador(1)
    modelo.set_descripcion("Camiseta talla L edición especial")
    modelo.set_cantidad(10)
    return modelo

def _db_mock(monkeypatch, modelo, fila=None, filas=None, rowcount=1):
    db = MagicMock()
    cursor = db.cursor.return_value.__enter__.return_value
    cursor.fetchone.return_value = fila
    cursor.fetchall.return_value = [] if filas is None else filas
    cursor.rowcount = rowcount
    monkeypatch.setattr(modelo, "_get_db", lambda: db)
    return db, cursor


@pytest.mark.parametrize(
    "valor, esperado",
    [(0, 1), (-5, 1), ("abc", 1), (None, 1), ("7", 7), (3.9, 3)],
)
def test_set_cantidad_normaliza_valores_invalidos_y_numericos(valor, esperado):
    modelo = _premio_valido()
    modelo.set_cantidad(valor)
    assert getattr(modelo, "_PremioModel__cantidad") == esperado
    assert modelo._validar_datos_premio() is True

def test_validacion_rechaza_nombre_demasiado_largo():
    modelo = _premio_valido()
    modelo.set_nombre("x" * 51)
    assert modelo._validar_datos_premio() is False

@pytest.mark.parametrize("id_patrocinador", [0, -1, "abc", None])
def test_validacion_rechaza_patrocinador_invalido(id_patrocinador):
    modelo = _premio_valido()
    modelo.set_id_patrocinador(id_patrocinador)
    assert modelo._validar_datos_premio() is False


def test_validacion_rechaza_descripcion_demasiado_larga():
    modelo = _premio_valido()
    modelo.set_descripcion("x" * 501)
    assert modelo._validar_datos_premio() is False


def test_validacion_limpia_errores_entre_llamadas():
    modelo = PremioModel()
    modelo.set_nombre("")
    modelo.set_id_patrocinador(None)
    assert modelo._validar_datos_premio() is False
    assert modelo.tiene_errores()

    modelo.set_nombre("Gorra")
    modelo.set_id_patrocinador(1)
    assert modelo._validar_datos_premio() is True
    assert modelo.get_errores() == []


def test_registrar_inserta_con_estado_y_valores_por_defecto(monkeypatch):
    modelo = _premio_valido()
    _, cursor = _db_mock(monkeypatch, modelo, rowcount=1)

    assert modelo.confirmar_registro() is True

    sentencia, parametros = cursor.execute.call_args.args
    assert "INSERT INTO premios" in sentencia
    assert "'pendiente'" in sentencia
    assert "FALSE" in sentencia
    assert parametros[0] == "Camiseta Oficial"
    assert parametros[1] == 1
    assert parametros[2] == "Camiseta talla L edición especial"
    assert parametros[5] == "default-premio.png"
    assert parametros[6] == 10


def test_registrar_no_consulta_bd_si_la_validacion_falla(monkeypatch):
    modelo = PremioModel()
    monkeypatch.setattr(modelo, "_get_db", lambda: pytest.fail("No debió consultar la BD"))
    assert modelo.confirmar_registro() is False


def test_registrar_devuelve_false_si_no_inserta_filas(monkeypatch):
    modelo = _premio_valido()
    _, cursor = _db_mock(monkeypatch, modelo, rowcount=0)
    assert modelo.confirmar_registro() is False
    cursor.execute.assert_called_once()


def test_registrar_devuelve_false_si_la_bd_falla(monkeypatch):
    modelo = _premio_valido()
    _, cursor = _db_mock(monkeypatch, modelo)
    cursor.execute.side_effect = RuntimeError("BD caída")
    assert modelo.confirmar_registro() is False


def test_consultar_filtra_por_estado_y_ordena(monkeypatch):
    modelo = PremioModel()
    filas = [{"id": 1, "estado": "entregado"}]
    _, cursor = _db_mock(monkeypatch, modelo, filas=filas)

    assert modelo.consultar(estado="entregado") == filas

    sentencia, parametros = cursor.execute.call_args.args
    assert "estatus = FALSE" in sentencia
    assert "AND estado = %s" in sentencia
    assert "ORDER BY fecha_creacion DESC, hora_creacion DESC" in sentencia
    assert parametros == ["entregado"]


def test_consultar_sin_filtro_no_envia_parametros(monkeypatch):
    modelo = PremioModel()
    _, cursor = _db_mock(monkeypatch, modelo)
    assert modelo.consultar() == []
    assert cursor.execute.call_args.args[1] == []


def test_consultar_devuelve_lista_vacia_si_la_bd_falla(monkeypatch):
    modelo = PremioModel()
    _, cursor = _db_mock(monkeypatch, modelo)
    cursor.execute.side_effect = RuntimeError("BD caída")
    assert modelo.consultar() == []


def test_contar_respeta_filtro_y_devuelve_total(monkeypatch):
    modelo = PremioModel()
    _, cursor = _db_mock(monkeypatch, modelo, fila={"total": 7})

    assert modelo.contar(estado="pendiente") == 7

    sentencia, parametros = cursor.execute.call_args.args
    assert "COUNT(*) as total" in sentencia
    assert "estatus = FALSE" in sentencia
    assert parametros == ["pendiente"]


def test_contar_sin_fila_devuelve_cero(monkeypatch):
    modelo = PremioModel()
    _db_mock(monkeypatch, modelo, fila=None)
    assert modelo.contar() == 0


def test_contar_devuelve_cero_si_la_bd_falla(monkeypatch):
    modelo = PremioModel()
    _, cursor = _db_mock(monkeypatch, modelo)
    cursor.execute.side_effect = RuntimeError("BD caída")
    assert modelo.contar() == 0


def test_modificar_actualiza_campos_base(monkeypatch):
    modelo = _premio_valido()
    _, cursor = _db_mock(monkeypatch, modelo, rowcount=1)

    assert modelo.confirmar_modificacion(12) is True

    sentencia, parametros = cursor.execute.call_args.args
    assert sentencia == (
        "UPDATE premios SET nombre = %s, id_patrocinador = %s, "
        "descripcion = %s, cantidad = %s WHERE id = %s"
    )
    assert parametros == [
        "Camiseta Oficial", 1, "Camiseta talla L edición especial", 10, 12
    ]


def test_modificar_incluye_foto_solo_cuando_se_proporciona(monkeypatch):
    modelo = _premio_valido()
    modelo.set_foto("nueva-foto.png")
    _, cursor = _db_mock(monkeypatch, modelo)

    assert modelo.confirmar_modificacion(4) is True

    sentencia, parametros = cursor.execute.call_args.args
    assert "foto = %s" in sentencia
    assert parametros[-2:] == ["nueva-foto.png", 4]


def test_modificar_no_consulta_bd_si_la_validacion_falla(monkeypatch):
    modelo = PremioModel()
    monkeypatch.setattr(modelo, "_get_db", lambda: pytest.fail("No debió consultar la BD"))
    assert modelo.confirmar_modificacion(1) is False


def test_modificar_devuelve_false_si_la_bd_falla(monkeypatch):
    modelo = _premio_valido()
    _, cursor = _db_mock(monkeypatch, modelo)
    cursor.execute.side_effect = RuntimeError("BD caída")
    assert modelo.confirmar_modificacion(1) is False


def test_eliminar_hace_baja_logica(monkeypatch):
    modelo = PremioModel()
    _, cursor = _db_mock(monkeypatch, modelo)

    assert modelo.confirmar_eliminacion(9) is True

    sentencia, parametros = cursor.execute.call_args.args
    assert sentencia == "UPDATE premios SET estatus = TRUE WHERE id = %s"
    assert parametros == (9,)


def test_eliminar_devuelve_false_si_la_bd_falla(monkeypatch):
    modelo = PremioModel()
    _, cursor = _db_mock(monkeypatch, modelo)
    cursor.execute.side_effect = RuntimeError("BD caída")
    assert modelo.confirmar_eliminacion(9) is False


def test_obtener_premios_pendientes_filtra_stock_y_orden(monkeypatch):
    modelo = PremioModel()
    filas = [{"id": 2, "nombre": "Gorra"}]
    _, cursor = _db_mock(monkeypatch, modelo, filas=filas)

    assert modelo.obtener_premios_pendientes() == filas

    sentencia = cursor.execute.call_args.args[0]
    assert "LEFT JOIN patrocinadores" in sentencia
    assert "p.estado = 'pendiente'" in sentencia
    assert "p.cantidad_entregada < p.cantidad" in sentencia
    assert "ORDER BY p.fecha_creacion DESC" in sentencia


def test_obtener_premios_entregados_resuelve_el_nombre_del_usuario(monkeypatch):
    modelo = PremioModel()
    filas = [
        {"id": 1, "entregado_por": 3},
        {"id": 2, "entregado_por": None},
        {"id": 3, "entregado_por": 8},
    ]
    _, cursor = _db_mock(monkeypatch, modelo, filas=filas)

    usuario = MagicMock()
    usuario.nombre = "Ana Pérez"
    usuario_model = MagicMock()
    usuario_model.obtener_por_id.side_effect = [usuario, None]
    monkeypatch.setattr("app.model.auth_model.UsuarioModel", lambda: usuario_model)

    resultado = modelo.obtener_premios_entregados()

    assert [p["usuario_nombre"] for p in resultado] == ["Ana Pérez", "—", "—"]
    assert usuario_model.obtener_por_id.call_args_list == [call(3), call(8)]
    assert "LIMIT 100" in cursor.execute.call_args.args[0]


def test_obtener_premios_entregados_devuelve_lista_vacia_si_la_bd_falla(monkeypatch):
    modelo = PremioModel()
    _, cursor = _db_mock(monkeypatch, modelo)
    cursor.execute.side_effect = RuntimeError("BD caída")
    assert modelo.obtener_premios_entregados() == []


def test_obtener_patrocinadores_activos_ordenados(monkeypatch):
    modelo = PremioModel()
    filas = [{"id_patrocinador": 2, "nombre_empresa": "ACME"}]
    _, cursor = _db_mock(monkeypatch, modelo, filas=filas)

    assert modelo.obtener_patrocinadores() == filas

    sentencia = cursor.execute.call_args.args[0]
    assert "WHERE estado = 1" in sentencia
    assert "ORDER BY nombre_empresa" in sentencia


def test_obtener_para_api_devuelve_el_premio(monkeypatch):
    modelo = PremioModel()
    fila = {"id": 5, "nombre": "Pelota", "cantidad": 4}
    _, cursor = _db_mock(monkeypatch, modelo, fila=fila)

    assert modelo.obtener_para_api(5) == fila

    sentencia, parametros = cursor.execute.call_args.args
    assert "estatus = FALSE" in sentencia
    assert parametros == (5,)


def test_obtener_para_api_inexistente_devuelve_none(monkeypatch):
    modelo = PremioModel()
    _db_mock(monkeypatch, modelo, fila=None)
    assert modelo.obtener_para_api(99) is None


def test_entregar_rechaza_premio_inexistente(monkeypatch):
    modelo = PremioModel()
    _, cursor = _db_mock(monkeypatch, modelo, fila=None)

    assert modelo.entregar(99) is False
    assert len(cursor.execute.call_args_list) == 1


def test_entregar_rechaza_cuando_no_queda_stock(monkeypatch):
    modelo = PremioModel()
    _, cursor = _db_mock(monkeypatch, modelo, fila={"cantidad": 2, "cantidad_entregada": 2})

    assert modelo.entregar(1, cantidad_entregar=1) is False
    assert len(cursor.execute.call_args_list) == 1


def test_entregar_parcial_mantiene_estado_pendiente(monkeypatch):
    modelo = PremioModel()
    _, cursor = _db_mock(
        monkeypatch, modelo, fila={"cantidad": 5, "cantidad_entregada": 1}, rowcount=1
    )

    assert modelo.entregar(
        premio_id=4,
        id_patrocinador=7,
        descripcion="Entrega parcial",
        entregado_por=9,
        cantidad_entregar=2,
    ) is True

    parametros = cursor.execute.call_args_list[1][0][1]
    assert parametros[0] == 3
    assert parametros[1] == "pendiente"
    assert parametros[3] == 7
    assert parametros[4] == "Entrega parcial"
    assert parametros[5] == 9
    assert parametros[6] == 4


@pytest.mark.parametrize("cantidad_entregar", ["abc", None])
def test_entregar_rechaza_cantidad_no_numerica(monkeypatch, cantidad_entregar):
    modelo = PremioModel()
    _, cursor = _db_mock(monkeypatch, modelo, fila={"cantidad": 5, "cantidad_entregada": 1})

    assert modelo.entregar(1, cantidad_entregar=cantidad_entregar) is False
    assert len(cursor.execute.call_args_list) == 1


def test_entregar_devuelve_false_si_la_bd_falla(monkeypatch):
    modelo = PremioModel()
    _, cursor = _db_mock(monkeypatch, modelo)
    cursor.execute.side_effect = RuntimeError("BD caída")
    assert modelo.entregar(1) is False
