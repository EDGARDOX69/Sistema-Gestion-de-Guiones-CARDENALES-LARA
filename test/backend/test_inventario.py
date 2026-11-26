from unittest.mock import patch
import pytest

@patch('app.controller.inventario_controller.InventarioModel')
def test_backend_consultar_recursos_json(mock_inventario_model_cls, client, superadmin):
    """
    Backend Test 1: Verifica que la acción AJAX 'consultar' devuelva 
    la lista de recursos estructurada correctamente en JSON.
    """
    mock_instance = mock_inventario_model_cls.return_value
    mock_instance.consultar.return_value = [
        {
            'id': 1,
            'tipo_nombre': 'Electrónica',
            'nombre': 'Laptop HP',
            'descripcion': 'Core i5',
            'estado_id': 1,
            'estado_nombre': 'Disponible',
            'fecha_compra': '2026-02-01'
        }
    ]

    response = client.post('/inventario/', data={'consultar': '1'})

    assert response.status_code == 200
    json_data = response.get_json()
    assert isinstance(json_data, list)
    assert json_data[0]['Nombre_Activo'] == 'Laptop HP'
    assert json_data[0]['Estado_Activo'] == 'Disponible'

@patch('app.controller.inventario_controller.InventarioModel')
def test_backend_buscar_recurso_ajax(mock_inventario_model_cls, client, superadmin):
    """
    Backend Test 2: Comprueba que la acción 'buscar' por ID devuelva 
    el estado y los datos detallados del activo en formato JSON.
    """
    mock_instance = mock_inventario_model_cls.return_value
    mock_instance.buscar.return_value = {
        'id': 3,
        'tipo_id': 2,
        'estado_id': 1,
        'nombre': 'Proyector BenQ',
        'descripcion': 'Full HD',
        'fecha_compra': '2025-10-10',
        'estado_nombre': 'Disponible'
    }

    response = client.post('/inventario/', data={'buscar': '1', 'idActivo': '3'})

    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['status'] is True
    assert json_data['datos']['Nombre_Activo'] == 'Proyector BenQ'
    mock_instance.set_id_activo.assert_called_with('3')

@patch('app.controller.inventario_controller.InventarioModel')
def test_backend_ver_detalle_recurso_ruta(mock_inventario_model_cls, client, superadmin):
    """
    Backend Test 3 (Reemplazo): Valida que la ruta GET /ver/<id> cargue 
    exitosamente el recurso y sus asignaciones asociadas.
    """
    mock_instance = mock_inventario_model_cls.return_value
    mock_instance.buscar.return_value = {
        'id': 5,
        'nombre': 'Balón de Fútbol',
        'estado_id': 2
    }
    mock_instance.consultar_asignaciones.return_value = [
        {'id': 1, 'usuario_id': 2, 'fecha_devolucion_esperada': '2026-05-01'}
    ]

    response = client.get('/inventario/ver/5', follow_redirects=True)

    assert response.status_code == 200
    mock_instance.set_id_activo.assert_called_with(5)
    mock_instance.consultar_asignaciones.assert_called_once_with(recurso_id=5)

@patch('app.controller.inventario_controller.InventarioModel')
def test_backend_editar_recurso_ajax(mock_inventario_model_cls, client, superadmin):
    """
    Backend Test 4: Evalúa la actualización de un recurso 
    mediante la petición AJAX POST del dashboard principal.
    """
    mock_instance = mock_inventario_model_cls.return_value
    mock_instance.confirmar_modificacion.return_value = True

    response = client.post('/inventario/', data={
        'editar': '2',
        'id_tipo_activo': '1',
        'Nombre': 'Tablet Actualizada',
        'Descripcion': 'Android 14',
        'Fecha_adquisicion': '2026-03-01'
    })

    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['mensaje'] == "Recurso actualizado correctamente"
    mock_instance.confirmar_modificacion.assert_called_once_with('2')

@patch('app.controller.inventario_controller.InventarioModel')
def test_backend_eliminar_recurso_ajax(mock_inventario_model_cls, client, superadmin):
    """
    Backend Test 5: Simula la eliminación de un activo 
    a través del flujo AJAX con registro de bitácora incluido.
    """
    mock_instance = mock_inventario_model_cls.return_value
    mock_instance.buscar.return_value = {'id': 4, 'nombre': 'Cable HDMI'}
    mock_instance.confirmar_eliminacion.return_value = True

    response = client.post('/inventario/', data={
        'eliminar': '1',
        'idActivo': '4'
    })

    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['mensaje'] == "Recurso eliminado correctamente"
    mock_instance.confirmar_eliminacion.assert_called_once_with('4')

@patch('app.controller.inventario_controller.InventarioModel')
def test_backend_devolver_recurso_ruta(mock_inventario_model_cls, client, superadmin):
    """
    Backend Test 6: Comprueba el funcionamiento de la ruta dedicada 
    para procesar la devolución de un recurso asignado.
    """
    mock_instance = mock_inventario_model_cls.return_value
    mock_instance.obtener_asignacion.return_value = {
        'id': 15,
        'recurso_id': 2,
        'recurso_nombre': 'Laptop Lenovo',
        'fecha_devolucion_real': None
    }

    response = client.post('/inventario/devolver/15', follow_redirects=True)

    assert response.status_code == 200
    mock_instance.devolver_recurso.assert_called_once_with(15)
    mock_instance.cambiar_estado.assert_called_once_with(2, 1)
    assert 'Devolución procesada correctamente'.encode('utf-8') in response.data