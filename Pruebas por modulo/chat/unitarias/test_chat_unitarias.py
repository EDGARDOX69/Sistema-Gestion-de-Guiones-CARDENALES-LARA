from app.helpers.chat_knowledge import ChatKnowledge


def test_detecta_saludo():
    assert ChatKnowledge._detectar_intencion('hola')['tipo'] == 'saludo'


def test_detecta_guia_de_guion():
    intencion = ChatKnowledge._detectar_intencion('como crear un guion')
    assert intencion['tipo'] == 'guia'
    assert 'guiones' in intencion['modulos']
