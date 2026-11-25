"""GU-UT — Pruebas unitarias del módulo guion (sin Flask ni MySQL).

Qué se prueba aquí y por qué:
- `_parsear_duracion`: convierte lo que escribe el operador ("min,seg" o
  minutos sueltos) a segundos. Un error aquí descuadra cronómetros y totales.
- `_validar_datos_guion_dict` / `_validar_datos_elemento`: son la última
  barrera del servidor antes del INSERT. Si se relajan, entran datos basura.

Estas pruebas no piden la fixture `app`, así que corren con `pytest -m unit`
sin MySQL levantado.
"""
import pytest

from app.model.guion_model import (
    ElementoGuionModel,
    GuionModel,
    _parsear_duracion,
)

pytestmark = pytest.mark.unit


# ---------------------------------------------------------------------------
# GU-UT-01 .. GU-UT-04 — _parsear_duracion
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    'entrada, esperado',
    [
        (None, 0),
        ('', 0),
        (0, 0),
        ('0,0', 0),
        ('1,30', 90),
        ('2,05', 125),
        ('1,', 60),
        (',30', 30),
        ('90', 5400),        # sin coma se interpreta como minutos
        (' 45 ', 2700),
        ('abc', 0),
    ],
)
def test_parsear_duracion_convierte_a_segundos(entrada, esperado):
    """GU-UT-01: contrato real de la conversión duración -> segundos."""
    assert _parsear_duracion(entrada) == esperado


def test_parsear_duracion_segundo_de_un_digito_se_rellena():
    """GU-UT-02: "2,5" se lee como 2 min 50 s (se rellena a dos dígitos)."""
    assert _parsear_duracion('2,5') == 170


def test_parsear_duracion_texto_basura_no_explota():
    """GU-UT-03: un valor inesperado devuelve 0, nunca lanza excepción."""
    assert _parsear_duracion('1:30') == 0


# ---------------------------------------------------------------------------
# GU-UT-04 .. GU-UT-06 — validación del guion
# ---------------------------------------------------------------------------

def test_guion_rechaza_nombre_vacio_o_corto():
    """GU-UT-04: el nombre es obligatorio y tiene mínimo 3 caracteres."""
    modelo = GuionModel()
    assert modelo._validar_datos_guion_dict({'nombre': '', 'fecha': '2026-01-01'}) is False
    assert modelo._validar_datos_guion_dict({'nombre': 'ab', 'fecha': '2026-01-01'}) is False


def test_guion_rechaza_nombre_demasiado_largo():
    """GU-UT-05: el máximo son 50 caracteres."""
    modelo = GuionModel()
    assert modelo._validar_datos_guion_dict({'nombre': 'x' * 51, 'fecha': '2026-01-01'}) is False
    assert modelo._validar_datos_guion_dict({'nombre': 'x' * 50, 'fecha': '2026-01-01'}) is True


def test_guion_rechaza_sin_fecha():
    """GU-UT-06: sin fecha no hay guion."""
    modelo = GuionModel()
    assert modelo._validar_datos_guion_dict({'nombre': 'Guion válido', 'fecha': None}) is False


def test_guion_valida_consetters_publicos():
    """GU-UT-07: la ruta de setters valida igual que la ruta de diccionario."""
    modelo = GuionModel()
    modelo.set_nombre('Show Viernes')
    modelo.set_fecha('2026-01-01')
    assert modelo._validar_datos_guion() is True

    modelo.set_nombre('ab')
    assert modelo._validar_datos_guion() is False
    assert modelo.tiene_errores()


# ---------------------------------------------------------------------------
# GU-UT-08 .. GU-UT-13 — validación de elementos
# ---------------------------------------------------------------------------

def _elemento(**cambios):
    modelo = ElementoGuionModel()
    modelo.set_guion_id(cambios.get('guion_id', 1))
    modelo.set_tipo(cambios.get('tipo', 'pregame'))
    modelo.set_contenido(cambios.get('contenido', 'Himno nacional'))
    modelo.set_hora(cambios.get('hora', '18:30:00'))
    modelo.set_inning(cambios.get('inning'))
    modelo.set_medio_inning(cambios.get('medio_inning'))
    modelo.set_duracion_estimada(cambios.get('duracion_estimada', 120))
    modelo.set_encargado(cambios.get('encargado', 'Keiver'))
    modelo.set_orden(cambios.get('orden', 1))
    return modelo


def test_elemento_exige_guion_tipo_y_contenido():
    """GU-UT-08: los tres campos base son obligatorios."""
    assert _elemento(guion_id=None)._validar_datos_elemento() is False
    assert _elemento(tipo=None)._validar_datos_elemento() is False
    assert _elemento(contenido=None)._validar_datos_elemento() is False


def test_elemento_exige_contenido_entre_5_y_500():
    """GU-UT-09: ni una palabra suelta ni un texto desmedido."""
    assert _elemento(contenido='Hola')._validar_datos_elemento() is False
    assert _elemento(contenido='x' * 501)._validar_datos_elemento() is False
    assert _elemento(contenido='12345')._validar_datos_elemento() is True
    assert _elemento(contenido='x' * 500)._validar_datos_elemento() is True


def test_pregame_exige_hora():
    """GU-UT-10: un pregame sin hora no se puede programar."""
    assert _elemento(tipo='pregame', hora=None)._validar_datos_elemento() is False
    assert _elemento(tipo='pregame', hora='18:30:00')._validar_datos_elemento() is True


def test_game_exige_inning_y_medio():
    """GU-UT-11: un game necesita inning y mitad (alta/baja)."""
    assert _elemento(tipo='game', inning=1, medio_inning=None)._validar_datos_elemento() is False
    assert _elemento(tipo='game', inning=None, medio_inning='alta')._validar_datos_elemento() is False
    assert _elemento(tipo='game', inning=1, medio_inning='alta')._validar_datos_elemento() is True


def test_elemento_acepta_inning_cero_como_invalido():
    """GU-UT-12: inning 0 se trata como ausente (no existe inning 0)."""
    assert _elemento(tipo='game', inning=0, medio_inning='alta')._validar_datos_elemento() is False


def test_modelo_no_restringe_el_enum_de_tipo():
    """GU-UT-13: el enum pregame/game lo valida el controlador, no el modelo.

    Se documenta el contrato real para que nadie asuma una validación que no
    existe en la capa de datos.
    """
    assert _elemento(tipo='otro')._validar_datos_elemento() is True
