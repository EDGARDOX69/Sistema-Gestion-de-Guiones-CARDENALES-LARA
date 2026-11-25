from datetime import time
from app.model.en_vivo_model import EnVivoModel


def test_formato_de_evento_pregame():
    texto = EnVivoModel()._fmt_evento_log({
        'contenido': 'Himno Nacional',
        'tipo': 'pregame',
        'hora': time(18, 30),
        'inning': None,
        'medio_inning': None,
    }, 'completar')
    assert 'Himno Nacional' in texto
    assert 'completado' in texto
