from unittest.mock import patch

@patch('app.controller.inventario_controller.InventarioModel')
def test_dashboard_get(mock_inventario_model_cls, client, superadmin):
    """Prueba unitaria: Verifica que la vista principal del inventario cargue los tipos de activos."""
    mock_instance = mock_inventario_model_cls.return_value
    mock_instance.obtener_tipos.return_value = [
        {'id': 1, 'nombre': 'Equipamiento', 'descripcion': 'Equipos deportivos'}
    ]

    response = client.get('/inventario/')

    assert response.status_code == 200
    mock_instance.obtener_tipos.assert_called_once()

@patch('app.controller.inventario_controller.InventarioModel')
def test_verificar_nombre_ajax(mock_inventario_model_cls, client, superadmin):
    """Prueba unitaria: Petición AJAX POST para verificar si un nombre de activo ya existe."""
    mock_instance = mock_inventario_model_cls.return_value
    mock_instance.verificar_nombre.return_value = True

    response = client.post(
        '/inventario/',
        data={'verificar_nombre': 'Arco de Fútbol'}
    )

    assert response.status_code == 200
    json_data = response.get_json()

    assert json_data['existe'] is True
    mock_instance.verificar_nombre.assert_called_once_with('Arco de Fútbol')

@patch('app.controller.inventario_controller.InventarioModel')
def test_asignar_recurso_exitoso(mock_inventario_model_cls, client, superadmin):
    """Prueba unitaria: Flujo de asignación exitosa de un recurso a un usuario."""
    mock_instance = mock_inventario_model_cls.return_value

    mock_instance.buscar.return_value = {
        'id': 1,
        'nombre': 'Balón Official',
        'estado_id': 1,
        'tipo_id': 1
    }
    mock_instance.obtener_asignacion_activa.return_value = None
    mock_instance.registrar_asignacion.return_value = {'id': 10, 'recurso_id': 1}
    mock_instance.obtener_usuarios.return_value = [{'id': 5, 'nombre': 'Admin'}]
    response = client.post(
        '/inventario/asignar/1',
        data={
            'usuario_id': '5',
            'fecha_devolucion_esperada': '2026-12-31',
            'notas': 'Prueba de asignación'
        },
        follow_redirects=True
    )
    assert response.status_code == 200
    mock_instance.registrar_asignacion.assert_called_once()
    mock_instance.cambiar_estado.assert_called_once_with(1, 2)

@patch('app.controller.inventario_controller.InventarioModel')
def test_asignar_recurso_no_disponible(mock_inventario_model_cls, client, superadmin):
    """Prueba unitaria: Falla si se intenta asignar un recurso que ya está ocupado."""
    mock_instance = mock_inventario_model_cls.return_value

    mock_instance.buscar.return_value = {
        'id': 1,
        'nombre': 'Balón Official',
        'estado_id': 2,
        'tipo_id': 1
    }
    mock_instance.obtener_usuarios.return_value = []
    response = client.post(
        '/inventario/asignar/1',
        data={
            'usuario_id': '5',
            'fecha_devolucion_esperada': '2026-12-31'
        },
        follow_redirects=True
    )

    assert response.status_code == 200
    assert 'El recurso no está disponible para asignación'.encode('utf-8') in response.data
    mock_instance.registrar_asignacion.assert_not_called()

@patch('app.controller.inventario_controller.InventarioModel')
def test_registrar_recurso_ajax(mock_inventario_model_cls, client, superadmin):
    """Prueba unitaria: Registro exitoso de un activo mediante la petición AJAX POST en la raíz."""
    mock_instance = mock_inventario_model_cls.return_value
    mock_instance.confirmar_registro.return_value = True

    response = client.post(
        '/inventario/',
        data={
            'registrar': '1',
            'id_tipo_activo': '1',
            'Nombre': 'Laptop Lenovo',
            'Descripcion': 'Core i7, 16GB RAM',
            'Fecha_adquisicion': '2026-01-15'
        }
    )

    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['mensaje'] == "Activo registrado correctamente"
    mock_instance.confirmar_registro.assert_called_once()

@patch('app.controller.inventario_controller.InventarioModel')
def test_devolver_recurso_exitoso(mock_inventario_model_cls, client, superadmin):
    """Prueba unitaria: Proceso de devolución de un recurso asignado."""
    mock_instance = mock_inventario_model_cls.return_value

    # Simulamos que la asignación existe y aún no ha sido devuelta
    mock_instance.obtener_asignacion.return_value = {
        'id': 10,
        'recurso_id': 1,
        'recurso_nombre': 'Proyector Epson',
        'fecha_devolucion_real': None
    }

    response = client.post(
        '/inventario/devolver/10',
        follow_redirects=True
    )

    assert response.status_code == 200
    mock_instance.devolver_recurso.assert_called_once_with(10)
    mock_instance.cambiar_estado.assert_called_once_with(1, 1)
    assert 'Devolución procesada correctamente'.encode('utf-8') in response.data
TEST
@patch('app.controller.inventario_controller.InventarioModel')
def test_crear_recurso_tradicional(mock_inventario_model_cls, client, superadmin):
    """Prueba unitaria: Creación de un recurso mediante la ruta tradicional /inventario/crear."""
    mock_instance = mock_inventario_model_cls.return_value
    mock_instance.confirmar_registro.return_value = True

    response = client.post(
        '/inventario/crear',
        data={
            'nombre': 'Tablet Gráfica',
            'descripcion': 'Wacom Intuos Pro',
            'tipo_id': '2',
            'fecha_compra': '2026-05-10',
            'costo': '150.00'
        },
        follow_redirects=True
    )

    assert response.status_code == 200
    mock_instance.confirmar_registro.assert_called_once()
    assert 'Recurso creado exitosamente'.encode('utf-8') in response.data