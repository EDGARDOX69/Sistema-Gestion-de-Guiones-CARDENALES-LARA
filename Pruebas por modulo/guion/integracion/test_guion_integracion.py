"""CP-GUI-INT-01: guardas de elementos y vista previa del guion."""

import uuid


def test_no_elimina_un_elemento_de_otro_guion(
    superadmin, client, db, crear_guion, crear_guion_completo
):
    guion_a = crear_guion_completo(nombre='Guion A')
    guion_b = crear_guion(nombre=f'Guion B {uuid.uuid4().hex[:8]}')

    with db.cursor() as cur:
        cur.execute(
            'SELECT id FROM elementos_guion WHERE guion_id = %s LIMIT 1',
            (guion_a,),
        )
        elemento_id = cur.fetchone()['id']

    respuesta = client.get(f'/guiones/eliminar-elemento/{guion_b}/{elemento_id}')
    assert respuesta.status_code == 302

    with db.cursor() as cur:
        cur.execute('SELECT COUNT(*) AS total FROM elementos_guion WHERE id = %s', (elemento_id,))
        assert cur.fetchone()['total'] == 1


def test_previsualizar_guion(superadmin, client, crear_guion):
    nombre = f'Guion Preview {uuid.uuid4().hex[:8]}'
    guion_id = crear_guion(nombre=nombre)

    respuesta = client.get(f'/guiones/previsualizar/{guion_id}')
    assert respuesta.status_code == 200
    assert nombre in respuesta.get_data(as_text=True)
