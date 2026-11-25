
# python -m pytest test/unitarias/test_balance_unitaria.py -v

import pytest
from unittest.mock import MagicMock
from app.model.balance_model import Pago  # Asegúrate de que la ruta coincida con la de tu proyecto

def test_validar_monto_positivo():
    """Prueba unitaria: Verifica que el sistema acepte montos válidos mayores a cero."""
    modelo = Pago()
    # Evaluamos la regla de validación de montos
    assert modelo.validar_monto(1500.50) == True

def test_validar_monto_negativo():
    """Prueba unitaria: Verifica que el sistema rechace montos negativos para evitar errores contables."""
    modelo = Pago()
    assert modelo.validar_monto(-200.00) == False

def test_validar_monto_cero():
    """Prueba unitaria: Verifica que el sistema rechace montos en cero."""
    modelo = Pago()
    assert modelo.validar_monto(0) == False

def test_get_total_pagado_by_contrato_mock(monkeypatch):
    """Prueba unitaria con Mock: Verifica el cálculo del total pagado simulando la respuesta de la BD."""
    modelo = Pago()
    
    # 1. Creamos un mock (simulador) para la conexión y el cursor de MySQL
    conexion_mock = MagicMock()
    cursor_mock = conexion_mock.cursor.return_value.__enter__.return_value
    
    # 2. Configuramos el mock para que devuelva un total simulado de 1000.0
    cursor_mock.fetchone.return_value = {"total": 1000.0}
    
    # 3. Interceptamos el método _get_db de la clase para que use nuestro mock en lugar de conectarse a MySQL
    monkeypatch.setattr(modelo, "_get_db", lambda: conexion_mock)
    
    # 4. Ejecutamos el método del modelo
    resultado = modelo.get_total_pagado_by_contrato(1)
    
    # 5. Aserciones para comprobar el comportamiento aislado
    assert resultado == 1000.0
    cursor_mock.execute.assert_called_once()

def _db_mock(monkeypatch, modelo, fila=None, filas=None, lastrowid=1):
    conexion = MagicMock()
    cursor = conexion.cursor.return_value.__enter__.return_value
    cursor.fetchone.return_value = fila
    cursor.fetchall.return_value = [] if filas is None else filas
    cursor.lastrowid = lastrowid
    monkeypatch.setattr(modelo, "_get_db", lambda: conexion)
    return conexion, cursor

@pytest.mark.parametrize("monto", ["abc", None, ""])
def test_validar_monto_rechaza_valores_no_numericos(monto):
    assert Pago().validar_monto(monto) is False

def test_registrar_pago_rechaza_monto_invalido_sin_consultar_bd(monkeypatch):
    modelo = Pago()
    monkeypatch.setattr(modelo, "_get_db", lambda: pytest.fail("No debió consultar la BD"))

    resultado = modelo.registrar_pago({
        'id_contrato': 1,
        'monto': -50,
        'tipo_pago': 'Efectivo',
        'fecha_pago': '2026-11-17',
        'hora_pago': '10:30',
    })

    assert resultado is None

def test_registrar_pago_inserta_y_devuelve_el_pago_creado(monkeypatch):
    modelo = Pago()
    conexion, cursor = _db_mock(monkeypatch, modelo, lastrowid=77)
    pago_creado = Pago(id_pago=77, id_contrato=3, monto=500)
    buscar = MagicMock(return_value=pago_creado)
    monkeypatch.setattr(modelo, "obtener_pago_por_id", buscar)

    resultado = modelo.registrar_pago({
        'id_contrato': 3,
        'monto': 500,
        'tipo_pago': 'Transferencia',
        'referencia': 'TRX-1',
        'fecha_pago': '2026-11-17',
        'hora_pago': '10:30',
    })

    sentencia, parametros = cursor.execute.call_args.args
    assert 'INSERT INTO pagos' in sentencia
    assert parametros == (3, 500, 'Transferencia', 'TRX-1', '2026-11-17', '10:30', None, None)
    buscar.assert_called_once_with(77)
    conexion.commit.assert_called_once_with()
    assert resultado is pago_creado

def test_registrar_pago_no_confirma_si_falla_la_insercion(monkeypatch):
    modelo = Pago()
    conexion, cursor = _db_mock(monkeypatch, modelo)
    cursor.execute.side_effect = RuntimeError('BD caída')

    resultado = modelo.registrar_pago({
        'id_contrato': 3,
        'monto': 500,
        'tipo_pago': 'Efectivo',
        'fecha_pago': '2026-11-17',
        'hora_pago': '10:30',
    })

    assert resultado is None
    conexion.commit.assert_not_called()

def test_get_total_pagado_general_mock(monkeypatch):
    modelo = Pago()
    _, cursor = _db_mock(monkeypatch, modelo, fila={"total": 3250.75})

    assert modelo.get_total_pagado_general() == 3250.75
    assert 'estado = 1' in cursor.execute.call_args.args[0]

def test_get_total_pagado_by_contrato_sin_filas_devuelve_cero(monkeypatch):
    modelo = Pago()
    _db_mock(monkeypatch, modelo, fila=None)

    assert modelo.get_total_pagado_by_contrato(99) == 0.0

def test_get_total_pagado_by_contrato_error_devuelve_cero(monkeypatch):
    modelo = Pago()
    monkeypatch.setattr(modelo, "_get_db", lambda: (_ for _ in ()).throw(RuntimeError('BD caída')))

    assert modelo.get_total_pagado_by_contrato(1) == 0.0

def test_obtener_historial_pagos_aplica_filtros_y_mapea_filas(monkeypatch):
    modelo = Pago()
    fila = {
        'id_pago': 12,
        'monto': 450.5,
        'tipo_pago': 'Cheque',
        'nombre_patrocinador': 'ACME',
        'id_patrocinador': 7,
    }
    _, cursor = _db_mock(monkeypatch, modelo, filas=[fila])

    pagos = modelo.obtener_historial_pagos(
        limit=25,
        fecha_inicio='2026-01-01',
        fecha_fin='2026-11-17',
        tipo_pago='Cheque',
    )

    sentencia, parametros = cursor.execute.call_args.args
    assert 'p.fecha_pago >= %s' in sentencia
    assert 'p.fecha_pago <= %s' in sentencia
    assert 'p.tipo_pago = %s' in sentencia
    assert parametros == ['2026-01-01', '2026-11-17', 'Cheque', 25]
    assert isinstance(pagos[0], Pago)
    assert pagos[0].id_pago == 12
    assert pagos[0].monto == 450.5
    assert pagos[0].nombre_patrocinador == 'ACME'
    assert pagos[0].id_patrocinador == 7

def test_obtener_pago_por_id_mapea_campos_del_join(monkeypatch):
    modelo = Pago()
    fila = {'id_pago': 4, 'id_contrato': 2, 'monto': 1200,
            'nombre_patrocinador': 'Sin patrocinador'}
    _, cursor = _db_mock(monkeypatch, modelo, fila=fila)

    pago = modelo.obtener_pago_por_id(4)

    assert cursor.execute.call_args.args[1] == (4,)
    assert pago.id_pago == 4
    assert pago.id_contrato == 2
    assert pago.monto == 1200
    assert pago.nombre_patrocinador == 'Sin patrocinador'

def test_modificar_pago_rechaza_monto_invalido_sin_consultar_bd(monkeypatch):
    modelo = Pago()
    monkeypatch.setattr(modelo, "_get_db", lambda: pytest.fail("No debió consultar la BD"))

    assert modelo.modificar_pago(5, {'monto': 'abc'}) is None

def test_modificar_pago_actualiza_solo_campos_enviados_y_confirma(monkeypatch):
    modelo = Pago()
    pago = Pago(id_pago=5, monto=100)
    monkeypatch.setattr(modelo, "obtener_pago_por_id", lambda id_pago: pago)
    conexion, cursor = _db_mock(monkeypatch, modelo)

    resultado = modelo.modificar_pago(5, {'monto': 200, 'descripcion': 'Ajuste'})

    sentencia, parametros = cursor.execute.call_args.args
    assert sentencia == 'UPDATE pagos SET monto = %s, Descripcion = %s WHERE id_pago = %s'
    assert parametros == [200, 'Ajuste', 5]
    conexion.commit.assert_called_once_with()
    assert resultado is pago


def test_modificar_pago_sin_campos_editables_no_escribe(monkeypatch):
    modelo = Pago()
    pago = Pago(id_pago=5)
    monkeypatch.setattr(modelo, "obtener_pago_por_id", lambda id_pago: pago)
    monkeypatch.setattr(modelo, "_get_db", lambda: pytest.fail("No debió consultar la BD"))

    assert modelo.modificar_pago(5, {'registrado_por': 9}) is pago


def test_modificar_pago_pago_inexistente_devuelve_none(monkeypatch):
    modelo = Pago()
    monkeypatch.setattr(modelo, "obtener_pago_por_id", lambda id_pago: None)

    assert modelo.modificar_pago(99, {'monto': 100}) is None


def test_eliminar_pago_hace_baja_logica_y_confirma(monkeypatch):
    modelo = Pago()
    pago = Pago(id_pago=8)
    monkeypatch.setattr(modelo, "obtener_pago_por_id", lambda id_pago: pago)
    conexion, cursor = _db_mock(monkeypatch, modelo)

    resultado = modelo.eliminar_pago(8)

    sentencia, parametros = cursor.execute.call_args.args
    assert sentencia == 'UPDATE pagos SET estado = 1 WHERE id_pago = %s'
    assert parametros == (8,)
    conexion.commit.assert_called_once_with()
    assert resultado is pago


def test_eliminar_pago_inexistente_no_escribe(monkeypatch):
    modelo = Pago()
    monkeypatch.setattr(modelo, "obtener_pago_por_id", lambda id_pago: None)
    monkeypatch.setattr(modelo, "_get_db", lambda: pytest.fail("No debió consultar la BD"))

    assert modelo.eliminar_pago(99) is None


def test_obtener_top_contratos_respeta_limite_y_estado(monkeypatch):
    modelo = Pago()
    filas = [{'id_contrato': 3, 'total_pagos': 4, 'nombre_patrocinador': 'ACME'}]
    _, cursor = _db_mock(monkeypatch, modelo, filas=filas)

    assert modelo.obtener_top_contratos(limit=3) == filas
    sentencia, parametros = cursor.execute.call_args.args
    assert 'p.estado = 0' in sentencia
    assert parametros == (3,)
