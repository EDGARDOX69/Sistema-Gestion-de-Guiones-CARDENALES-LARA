import json

from app.controller import reels_controller
from app.model.reels_model import ReelModel, VideoModel


def test_guardar_y_listar_reel():
    # Guarda un reel nuevo en la base de datos y verifica que aparezca en el listado
    modelo = ReelModel()
    creado = modelo.registrar({
        "nombre": "Reel Apertura",
        "duracion_total": 2.5,
    })

    # Retorna el registro creado con su ID asignado
    assert creado is not None
    reel_id = creado["id"] if isinstance(creado, dict) else creado.id
    assert reel_id is not None

    listado = modelo.consultar()
    ids = [r["id"] if isinstance(r, dict) else r.id for r in listado]
    assert reel_id in ids


def test_buscar_reel_existente():
    # Registra un reel y comprueba que se pueda consultar por su ID
    modelo = ReelModel()
    creado = modelo.registrar({
        "nombre": "Reel Detalle",
        "duracion_total": 1.5,
    })
    reel_id = creado["id"] if isinstance(creado, dict) else creado.id

    # Retorna el diccionario u objeto del reel encontrado
    encontrado = modelo.obtener_por_id(reel_id)
    assert encontrado is not None
    nombre = encontrado["nombre"] if isinstance(encontrado, dict) else encontrado.nombre
    assert nombre == "Reel Detalle"


def test_buscar_reel_que_no_existe():
    # Al consultar un ID inexistente debe retornar None
    modelo = ReelModel()
    assert modelo.obtener_por_id(999999) is None


def test_actualizar_datos_de_reel():
    # Modifica el nombre y la duración de un reel ya guardado en la base de datos
    modelo = ReelModel()
    creado = modelo.registrar({
        "nombre": "Reel Original",
        "duracion_total": 1.0,
    })
    reel_id = creado["id"] if isinstance(creado, dict) else creado.id

    modelo.modificar(reel_id, {
        "nombre": "Reel Actualizado",
        "duracion_total": 3.0,
    })

    # Retorna el reel con los nuevos valores guardados
    actualizado = modelo.obtener_por_id(reel_id)
    nombre = actualizado["nombre"] if isinstance(actualizado, dict) else actualizado.nombre
    assert nombre == "Reel Actualizado"


def test_eliminar_reel():
    # Elimina un reel y verifica que ya no salga en la lista de activos
    modelo = ReelModel()
    creado = modelo.registrar({
        "nombre": "Reel Temporal",
        "duracion_total": 1.5,
    })
    reel_id = creado["id"] if isinstance(creado, dict) else creado.id

    modelo.confirmar_eliminacion(reel_id)

    # El listado activo ya no debe incluir el ID eliminado
    listado = modelo.consultar()
    ids_activos = [r["id"] if isinstance(r, dict) else r.id for r in listado]
    assert reel_id not in ids_activos


def test_agregar_video_a_un_reel():
    # Crea un reel, le asocia un video y verifica que quede vinculado en la BD
    reel_model = ReelModel()
    video_model = VideoModel()

    reel = reel_model.registrar({"nombre": "Reel Con Video", "duracion_total": 2.0})
    reel_id = reel["id"] if isinstance(reel, dict) else reel.id

    # Retorna el video registrado dentro del reel
    video = video_model.registrar({
        "reel_id": reel_id,
        "nombre": "Spot Comercial 1",
        "duracion_segundos": 20,
        "orden": 1,
        "id_patrocinador": None,
    })
    assert video is not None

    # Retorna la lista de videos asociados a ese reel
    videos = video_model.consultar_por_reel(reel_id)
    assert len(videos) >= 1


def test_quitar_video_de_un_reel():
    # Elimina un video específico y verifica que desaparezca del reel
    reel_model = ReelModel()
    video_model = VideoModel()

    reel = reel_model.registrar({"nombre": "Reel Quitar Video", "duracion_total": 2.0})
    reel_id = reel["id"] if isinstance(reel, dict) else reel.id

    video = video_model.registrar({
        "reel_id": reel_id,
        "nombre": "Spot Borrable",
        "duracion_segundos": 15,
        "orden": 1,
        "id_patrocinador": None,
    })
    video_id = video["id"] if isinstance(video, dict) else video.id

    video_model.eliminar(video_id)

    # La consulta del reel ya no debe traer ese video
    videos_restantes = video_model.consultar_por_reel(reel_id)
    ids_videos = [v["id"] if isinstance(v, dict) else v.id for v in videos_restantes]
    assert video_id not in ids_videos


def test_guardar_lista_videos_desde_json():
    # Verifica que el controlador guarde varios videos desde JSON en la BD real
    reel_model = ReelModel()
    video_model = VideoModel()

    reel = reel_model.registrar({"nombre": "Reel Varios Videos", "duracion_total": 2.0})
    reel_id = reel["id"] if isinstance(reel, dict) else reel.id

    payload = json.dumps([
        {"nombre": "Video 1", "duracion": "10", "patrocinador": None},
        {"nombre": "Video 2", "duracion": "25", "patrocinador": None},
    ])

    reels_controller._procesar_videos_json(reel_id, payload)

    # Retorna los 2 videos insertados en la base de datos para ese reel
    videos = video_model.consultar_por_reel(reel_id)
    assert len(videos) == 2


def test_crear_reel_completo_desde_formulario(client, superadmin):
    # Envía los datos por la ruta POST /reels/crear y verifica que se guarden en MySQL
    respuesta = client.post(
        "/reels/crear",
        data={
            "nombre": "Reel Desde Formulario",
            "duracion_total": "1,30",
            "videos_json": "[]",
        },
        follow_redirects=False,
    )

    # Retorna redirección (302) hacia el listado principal al guardar con éxito
    assert respuesta.status_code == 302
    assert respuesta.headers["Location"].endswith("/reels/")

    nombres = [
        r["nombre"] if isinstance(r, dict) else r.nombre
        for r in ReelModel().consultar()
    ]
    assert "Reel Desde Formulario" in nombres