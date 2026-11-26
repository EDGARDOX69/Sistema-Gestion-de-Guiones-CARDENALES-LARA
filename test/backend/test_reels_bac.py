from unittest.mock import patch

from app.controller import reels_controller


def test_cargar_panel_reels(client, superadmin):
    # Consulta la ruta principal del panel de reels con sesión iniciada
    with patch.object(reels_controller, "ReelModel") as rm_mock, \
         patch.object(reels_controller, "VideoModel") as vm_mock:
        rm_mock.return_value.consultar.return_value = []
        vm_mock.return_value.consultar_por_reel.return_value = []

        respuesta = client.get("/reels/")

        # Retorna código 200 al cargar la vista del panel
        assert respuesta.status_code == 200


def test_obtener_reels_json(client, superadmin):
    # Solicita los reels por POST para recibir respuesta en formato JSON
    with patch.object(reels_controller, "ReelModel") as rm_mock, \
         patch.object(reels_controller, "VideoModel") as vm_mock:
        rm_mock.return_value.consultar.return_value = [
            {"id": 1, "nombre": "Reel Apertura", "duracion_total": 2.0, "videos": []}
        ]
        vm_mock.return_value.consultar_por_reel.return_value = []

        respuesta = client.post("/reels/", data={"consultar": "1"})
        datos = respuesta.get_json()

        # Retorna estado 200 y la lista JSON con los reels simulados
        assert respuesta.status_code == 200
        assert isinstance(datos, list)
        assert len(datos) == 1


def test_cargar_formulario_crear_reel(client, superadmin):
    # Abre la pantalla para crear un nuevo reel
    with patch.object(reels_controller, "_patrocinadores_select", return_value=[]):
        respuesta = client.get("/reels/crear")

        # Retorna código 200 mostrando el formulario
        assert respuesta.status_code == 200


def test_rechazar_crear_reel_sin_nombre(client, superadmin):
    # Intenta guardar un reel con el nombre vacío
    with patch.object(reels_controller, "_patrocinadores_select", return_value=[]), \
         patch.object(reels_controller, "ReelModel") as rm_mock:
        respuesta = client.post(
            "/reels/crear",
            data={"nombre": "", "duracion_total": "1,00", "videos_json": "[]"},
        )

        # Retorna 200 (permanece en el formulario) y no llama a registrar
        assert respuesta.status_code == 200
        rm_mock.return_value.registrar.assert_not_called()


def test_crear_reel_redirige_al_panel(client, superadmin):
    # Envía un reel válido para registrarlo por la ruta
    with patch.object(reels_controller, "ReelModel") as rm_mock, \
         patch.object(reels_controller, "_procesar_videos_json"):
        rm_mock.return_value.registrar.return_value = {"id": 5, "nombre": "Reel Medio Tiempo"}

        respuesta = client.post(
            "/reels/crear",
            data={"nombre": "Reel Medio Tiempo", "duracion_total": "2,00", "videos_json": "[]"},
            follow_redirects=False,
        )

        # Retorna redirección 302 hacia /reels/
        assert respuesta.status_code == 302
        assert respuesta.headers["Location"].endswith("/reels/")


def test_ver_reel_inexistente_redirige(client, superadmin):
    # Consulta un reel con un ID que no existe
    with patch.object(reels_controller, "ReelModel") as rm_mock:
        rm_mock.return_value.obtener_por_id.return_value = None

        respuesta = client.get("/reels/ver/999", follow_redirects=False)

        # Retorna redirección 302 hacia el listado principal
        assert respuesta.status_code == 302
        assert respuesta.headers["Location"].endswith("/reels/")


def test_editar_reel_redirige_al_detalle(client, superadmin):
    # Envía datos válidos para actualizar un reel existente
    with patch.object(reels_controller, "ReelModel") as rm_mock, \
         patch.object(reels_controller, "_procesar_videos_json"):
        rm_mock.return_value.obtener_por_id.return_value = {"id": 2, "nombre": "Reel Viejo"}
        rm_mock.return_value.modificar.return_value = {"id": 2, "nombre": "Reel Nuevo"}

        respuesta = client.post(
            "/reels/editar/2",
            data={"nombre": "Reel Nuevo", "duracion_total": "1,50", "videos_json": "[]"},
            follow_redirects=False,
        )

        # Retorna redirección 302 hacia /reels/ver/2
        assert respuesta.status_code == 302
        assert respuesta.headers["Location"].endswith("/reels/ver/2")


def test_eliminar_reel_redirige_al_panel(client, superadmin):
    # Solicita eliminar un reel existente por su ID
    with patch.object(reels_controller, "ReelModel") as rm_mock:
        rm_mock.return_value.obtener_por_id.return_value = {"id": 3, "nombre": "Reel Borrar"}
        rm_mock.return_value.confirmar_eliminacion.return_value = True

        respuesta = client.post("/reels/eliminar/3", follow_redirects=False)

        # Retorna redirección 302 hacia /reels/
        assert respuesta.status_code == 302
        assert respuesta.headers["Location"].endswith("/reels/")