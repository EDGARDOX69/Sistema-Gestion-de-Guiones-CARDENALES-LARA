import pytest
from unittest.mock import patch

@patch('app.controller.inventario_controller.TipoRecursoModel')
@patch('app.controller.inventario_controller.InventarioModel')
def test_consultar_tipos_recurso(mock_inventario_model, mock_tipo_model, client):
    """Prueba unitaria para listar tipos de recursos (consultar_tipos)."""
    instance_tipo = mock_tipo_model.return_value
    instance_tipo.consultar.return_value = [
        {'id': 1, 'nombre': 'Equipos de Computación', 'descripcion': 'Laptops y PCs'},
        {'id': 2, 'nombre': 'Mobiliario', 'descripcion': 'Sillas y escritorios'}
    ]

    response = client.post('/inventario/', data={'consultar_tipos': '1'})
    
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) == 2
    assert data[0]['id_tipo_activo'] == 1
    assert data[0]['Nombre'] == 'Equipos de Computación'

@patch('app.controller.inventario_controller.TipoRecursoModel')
@patch('app.controller.inventario_controller.InventarioModel')
def test_agregar_tipo_recurso(mock_inventario_model, mock_tipo_model, client):
    """Prueba unitaria para registrar un tipo de recurso."""
    instance_tipo = mock_tipo_model.return_value
    instance_tipo.confirmar_registro.return_value = True

    response = client.post('/inventario/', data={
        'agregar_tipo_activo': '1',
        'nombre_tipo_activo': 'Redes y Conectividad',
        'descripcion_tipo_activo': 'Routers y switches'
    })

    assert response.status_code == 200
    data = response.get_json()
    assert data['mensaje'] == "Tipo de recurso registrado correctamente"
    instance_tipo.set_nombre_tipo.assert_called_with('Redes y Conectividad')
    instance_tipo.confirmar_registro.assert_called_once()

@patch('app.controller.inventario_controller.TipoRecursoModel')
@patch('app.controller.inventario_controller.InventarioModel')
def test_editar_tipo_recurso(mock_inventario_model, mock_tipo_model, client):
    """Prueba unitaria para editar un tipo de recurso."""
    instance_tipo = mock_tipo_model.return_value
    instance_tipo.confirmar_modificacion.return_value = True

    response = client.post('/inventario/', data={
        'editar_tipo_activo': '3',
        'nombre_tipo_activo': 'Equipos Médicos Actualizados',
        'descripcion_tipo_activo': 'Instrumentos'
    })

    assert response.status_code == 200
    data = response.get_json()
    assert data['mensaje'] == "Tipo de recurso actualizado correctamente"
    instance_tipo.set_id_tipo.assert_called_with('3')
    instance_tipo.confirmar_modificacion.assert_called_with('3')

@patch('app.controller.inventario_controller.TipoRecursoModel')
@patch('app.controller.inventario_controller.InventarioModel')
def test_eliminar_tipo_recurso(mock_inventario_model, mock_tipo_model, client):
    """Prueba unitaria para eliminar un tipo de recurso."""
    instance_tipo = mock_tipo_model.return_value
    instance_tipo.buscar_tipo.return_value = {'id': 3, 'nombre': 'Equipos Obsoletos', 'descripcion': '...'}
    instance_tipo.confirmar_eliminacion.return_value = True

    response = client.post('/inventario/', data={
        'eliminar_tipo_activo': '3'
    })

    assert response.status_code == 200
    data = response.get_json()
    assert data['mensaje'] == "Tipo de recurso eliminado correctamente"
    instance_tipo.confirmar_eliminacion.assert_called_with('3')