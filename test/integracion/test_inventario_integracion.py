
import pytest
from app.model.inventario_model import InventarioModel


def test_inventario_model_conexion_y_tipos(app):
    """Verifica que el modelo pueda conectarse a la BD y obtener tipos de recursos."""
    with app.app_context():
        model = InventarioModel()
        tipos = model.obtener_tipos()

        assert isinstance(tipos, list)

def test_verificar_nombre_recurso_db(app):
    """Valida la consulta real en la base de datos para nombres duplicados."""
    with app.app_context():
        model = InventarioModel()

        existe = model.verificar_nombre("ActivoFicticioPrueba12345")

        assert isinstance(existe, bool)
        assert existe is False

def test_flujo_crear_y_consultar_recurso_integracion(app, client, superadmin):
    """
    Prueba de integración:
    Inicia sesión como Superadmin, crea un recurso mediante POST
    y verifica la respuesta del sistema.
    """
    with app.app_context():
        model = InventarioModel()
        tipos = model.obtener_tipos()

        if not tipos:
            pytest.skip(
                "No hay tipos de recurso en la base de datos de prueba."
            )
        tipo_id_prueba = tipos[0]['id']
    response = client.post('/inventario/crear', data={
        'nombre': 'Test Balón Integration',
        'descripcion': 'Balón de prueba para integración de sistema',
        'tipo_id': tipo_id_prueba,
        'fecha_compra': '2026-01-01',
        'costo': '150.00'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Recurso creado exitosamente' in response.data

def test_consultar_asignaciones_endpoint(app, client, superadmin):
    """
    Prueba de integración:
    Verifica que un Superadmin pueda acceder a la gestión de asignaciones.
    """
    response = client.get(
        '/inventario/gestion-asignaciones',
        follow_redirects=True
    )

    assert response.status_code == 200

    def test_ver_detalle_recurso_integracion(app, client, superadmin):

     """
    Prueba de integración:
    Verifica que el sistema permita ver el detalle y las asignaciones de un recurso.
    Se utiliza un ID genérico o se busca uno existente para asegurar la prueba.
    """
    with app.app_context():
        model = InventarioModel()
        recursos = model.consultar()
        
        if not recursos:
            pytest.skip("No hay recursos en la base de datos para probar el detalle.")
        
        recurso_id = recursos[0]['id']

    response = client.get(
        f'/inventario/ver/{recurso_id}',
        follow_redirects=True
    )

    assert response.status_code == 200

def test_asignar_recurso_vista_integracion(app, client, superadmin):
    """
    Prueba de integración:
    Verifica que el formulario de asignación de un recurso cargue correctamente 
    con los datos del recurso y la lista de usuarios.
    """
    with app.app_context():
        model = InventarioModel()
        recursos = model.consultar()
        
        if not recursos:
            pytest.skip("No hay recursos disponibles para probar la vista de asignación.")
        
        recurso_id = recursos[0]['id']

    response = client.get(
        f'/inventario/asignar/{recurso_id}',
        follow_redirects=True
    )

    assert response.status_code == 200

def test_eliminar_recurso_vista_integracion(app, client, superadmin):
    """
    Prueba de integración:
    Verifica que la vista previa para dar de baja/eliminar un recurso 
    cargue correctamente su información de dependencias y asignaciones.
    """
    with app.app_context():
        model = InventarioModel()
        recursos = model.consultar()
        
        if not recursos:
            pytest.skip("No hay recursos para probar la vista de eliminación.")
        
        recurso_id = recursos[0]['id']

    response = client.get(
        f'/inventario/eliminar/{recurso_id}',
        follow_redirects=True
    )

    assert response.status_code == 200

    
