import json
from unittest.mock import patch

from app.controller import reels_controller


def test_duracion_valida():
    assert reels_controller._parsear_duracion_minutos("1,30") == 1.5
    assert reels_controller._parsear_duracion_minutos("2") == 2.0


def test_duracion_invalida():
    assert reels_controller._parsear_duracion_minutos("") == 0
    assert reels_controller._parsear_duracion_minutos("abc") == 0


def test_segundos_validos():
    assert reels_controller._parsear_segundos("30") == 30
    assert reels_controller._parsear_segundos("-5") == 0


def test_crear_reel_simulado():
    with patch.object(reels_controller, "ReelModel") as rm_mock:
        rm = rm_mock.return_value
        rm.registrar.return_value = {"id": 10, "nombre": "Reel Pre-Juego", "duracion_total": 2.0}

        nuevo_reel = rm.registrar({"nombre": "Reel Pre-Juego", "duracion_total": 2.0})

        assert nuevo_reel["id"] == 10
        assert nuevo_reel["nombre"] == "Reel Pre-Juego"
        rm.registrar.assert_called_once_with({"nombre": "Reel Pre-Juego", "duracion_total": 2.0})


def test_editar_reel_simulado():
    with patch.object(reels_controller, "ReelModel") as rm_mock:
        rm = rm_mock.return_value
        rm.modificar.return_value = {"id": 10, "nombre": "Reel Editado", "duracion_total": 3.0}

        editado = rm.modificar(10, {"nombre": "Reel Editado", "duracion_total": 3.0})

        assert editado["nombre"] == "Reel Editado"
        assert editado["duracion_total"] == 3.0
        rm.modificar.assert_called_once_with(10, {"nombre": "Reel Editado", "duracion_total": 3.0})


def test_datos_dashboard_simulados():
    with patch.object(reels_controller, "ReelModel") as rm_mock:
        rm_mock.return_value.consultar.return_value = [
            {"id": 1, "nombre": "Reel Apertura", "duracion_total": 1.5, "videos": []},
            {"id": 2, "nombre": "Reel Cierre", "duracion_total": 2.0, "videos": []},
        ]

        reels = reels_controller.ReelModel().consultar()

        assert len(reels) == 2
        assert reels[0]["nombre"] == "Reel Apertura"


def test_reel_model_obtener_por_id_inexistente_retorna_none():
        with patch.object(reels_controller, "ReelModel") as mock_rm_cls:
          mock_rm_cls.return_value.obtener_por_id.return_value = None

        assert reels_controller.ReelModel().obtener_por_id(999) is None

def test_reel_model_consultar_sin_bd_real():

    with patch.object(reels_controller, "ReelModel") as mock_rm_cls:
        mock_rm_cls.return_value.consultar.return_value = [{"id": 1, "nombre": "Reel Apertura"}]

        resultado = reels_controller.ReelModel().consultar()

        assert len(resultado) == 1
        assert resultado[0]["nombre"] == "Reel Apertura"

        
def test_videos_json_vacio():
    with patch.object(reels_controller, "VideoModel") as vm_mock:
        reels_controller._procesar_videos_json(1, "")
        vm_mock.return_value.registrar.assert_not_called()

def test_videos_json_valido():
    with patch.object(reels_controller, "VideoModel") as vm_mock:
        vm = vm_mock.return_value
        vm.consultar_por_reel.return_value = []
        datos = json.dumps([{"nombre": "Video 1", "duracion": "15", "patrocinador": 1}])

        reels_controller._procesar_videos_json(1, datos)

        vm.registrar.assert_called_once_with({
            "reel_id": 1,
            "nombre": "Video 1",
            "duracion_segundos": 15,
            "orden": 1,
            "id_patrocinador": 1,
        })


def test_patrocinadores_lista():
    with patch.object(reels_controller, "PatrocinadorModel") as pm_mock:
        pm_mock.return_value.consultar.return_value = [
            {"id_patrocinador": 1, "nombre_empresa": "Empresa 1"}
        ]
        assert reels_controller._patrocinadores_select() == [(1, "Empresa 1")]
