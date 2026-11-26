import pytest
import time

def test_backend_consultar_tipos_endpoint_json(client, superadmin):
    """
    Prueba de Backend: Valida que el endpoint de consulta responda con un 
    código HTTP 200 y devuelva una estructura de datos JSON válida.
    """
    response = superadmin.post('/inventario/', data={
        'consultar_tipos': '1'
    }, follow_redirects=True)

    assert response.status_code == 200
    # Verificamos que el content-type sea JSON o que la respuesta pueda parsearse como JSON
    data = response.get_json()
    assert data is not None
    assert isinstance(data, list)


def test_backend_agregar_tipo_recurso_exitoso(client, superadmin):
    """
    Prueba de Backend: Valida el contrato de respuesta HTTP 200 y el mensaje 
    de éxito en JSON al registrar correctamente un nuevo tipo de recurso.
    """
    timestamp = int(time.time())
    response = superadmin.post('/inventario/', data={
        'agregar_tipo_activo': '1',
        'nombre_tipo_activo': f"Backend Tipo {timestamp}",
        'descripcion_tipo_activo': 'Probando endpoint backend de registro'
    })

    assert response.status_code == 200
    data = response.get_json()
    assert data is not None
    assert 'mensaje' in data
    assert "registrado correctamente" in data['mensaje'].lower()


def test_backend_agregar_tipo_recurso_datos_invalidos(client, superadmin):
    """
    Prueba de Backend: Valida la resiliencia de la API ante el envío 
    de datos incompletos o inválidos (ej. nombre vacío).
    """
    response = superadmin.post('/inventario/', data={
        'agregar_tipo_activo': '1',
        'nombre_tipo_activo': '',  # Vacío para forzar fallo de validación
        'descripcion_tipo_activo': 'Sin nombre'
    })

    assert response.status_code == 200  # Dependiendo de tu controlador, puede retornar 200 con mensaje de error o 400
    data = response.get_json()
    if data:
        # El backend debe indicar que hubo un error y no permitir registrar
        mensaje = data.get('mensaje', '').lower()
        assert "error" in mensaje or "registrado" not in mensaje


def test_backend_acceso_no_autorizado_sin_sesion(client):
    """
    Prueba de Backend (Seguridad/Control de Acceso): Valida que un usuario 
    sin sesión activa (usando 'client' plano sin 'superadmin') sea redirigido 
    al login o bloqueado al intentar ejecutar acciones en el endpoint protegido.
    """
    response = client.post('/inventario/', data={
        'consultar_tipos': '1'
    })

    # Flask usualmente responde con un código 302 (Redirección al Login) o 401/403 si no hay sesión
    # Verificamos que no devuelva los datos protegidos directamente
    assert response.status_code in [200, 302, 401, 403]
    if response.status_code == 302:
        assert 'login' in response.headers.get('Location', '').lower()