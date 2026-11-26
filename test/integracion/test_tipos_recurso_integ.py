import pytest
import time

def test_integracion_agregar_tipo_recurso(client, superadmin):
    """
    Prueba de integración: Verifica que al enviar un nuevo tipo de recurso 
    desde el controlador, este se guarde correctamente en la base de datos MySQL.
    """
    timestamp = int(time.time())
    nombre_prueba = f"Tipo Test {timestamp}"
    desc_prueba = "Descripción para prueba de integración"

    response = superadmin.post('/inventario/', data={
        'agregar_tipo_activo': '1',
        'nombre_tipo_activo': nombre_prueba,
        'descripcion_tipo_activo': desc_prueba
    })

    assert response.status_code == 200
    data = response.get_json()
    assert data is not None
    assert "registrado correctamente" in data.get('mensaje', '').lower()


def test_integracion_consultar_tipos_recurso(client, superadmin):
    """
    Prueba de integración: Verifica que el sistema (y los selectores/listas 
    desplegables del módulo) detecten y listen los tipos de recursos desde la BD.
    """
    response = superadmin.post('/inventario/', data={
        'consultar_tipos': '1'
    })

    assert response.status_code == 200
    tipos_lista = response.get_json()
    assert isinstance(tipos_lista, list)
    if len(tipos_lista) > 0:
        assert 'id_tipo_activo' in tipos_lista[0]
        assert 'Nombre' in tipos_lista[0]


def test_integracion_editar_tipo_recurso(client, superadmin):
    """
    Prueba de integración: Crea un registro temporal único, lo edita y verifica 
    que la BD persista el cambio exitosamente.
    """
    timestamp = int(time.time())
    nombre_original = f"Tipo Para Editar {timestamp}"
    
    # 1. Creamos un tipo exclusivo para editarlo
    superadmin.post('/inventario/', data={
        'agregar_tipo_activo': '1',
        'nombre_tipo_activo': nombre_original,
        'descripcion_tipo_activo': 'Temporal para editar'
    })

    # 2. Consultamos para obtener su ID exacto
    response_consultar = superadmin.post('/inventario/', data={'consultar_tipos': '1'})
    tipos_lista = response_consultar.get_json()
    tipo_creado = next((t for t in tipos_lista if t.get('Nombre') == nombre_original), None)
    
    if tipo_creado:
        id_existente = tipo_creado['id_tipo_activo']
        nombre_modificado = f"Tipo Modificado {timestamp}"
        
        response_editar = superadmin.post('/inventario/', data={
            'editar_tipo_activo': str(id_existente),
            'nombre_tipo_activo': nombre_modificado,
            'descripcion_tipo_activo': "Actualizado en prueba de integración"
        })

        assert response_editar.status_code == 200
        data_editar = response_editar.get_json()
        assert "actualizado correctamente" in data_editar.get('mensaje', '').lower()
    else:
        pytest.fail("No se pudo preparar el registro temporal para la edición.")

def test_integracion_eliminar_tipo_recurso(client, superadmin):
    """
    Prueba de integración: Verifica que se pueda realizar el borrado físico de un 
    tipo de recurso en la BD (creándolo previamente con nombre único sin recursos asociados).
    """
    timestamp = int(time.time())
    nombre_para_borrar = f"Tipo Limpio {timestamp}"
    
    superadmin.post('/inventario/', data={
        'agregar_tipo_activo': '1',
        'nombre_tipo_activo': nombre_para_borrar,
        'descripcion_tipo_activo': 'Temporal sin hijos para borrado físico'
    })

    response_consultar = superadmin.post('/inventario/', data={'consultar_tipos': '1'})
    tipos_lista = response_consultar.get_json()
    
    tipo_creado = next((t for t in tipos_lista if t.get('Nombre') == nombre_para_borrar), None)
    
    if tipo_creado:
        id_a_borrar = tipo_creado['id_tipo_activo']
        
        response_eliminar = superadmin.post('/inventario/', data={
            'eliminar_tipo_activo': str(id_a_borrar)
        })

        assert response_eliminar.status_code == 200
        data = response_eliminar.get_json()
        assert "eliminado correctamente" in data.get('mensaje', '').lower()
    else:
        pytest.fail("No se pudo preparar el tipo temporal para la prueba de eliminación.")