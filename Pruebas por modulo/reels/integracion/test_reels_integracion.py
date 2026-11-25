"""CP-REE-INT-01: reels y sus videos."""

import json
import uuid


def _videos(*nombres):
    return json.dumps([
        {'nombre': nombre, 'duracion': 30 + i, 'patrocinador': None}
        for i, nombre in enumerate(nombres)
    ])


def test_crear_editar_y_eliminar_reel(superadmin, client, db):
    nombre = f'Reel {uuid.uuid4().hex[:8]}'

    respuesta = client.post('/reels/crear', data={
        'nombre': nombre,
        'duracion_total': '2,30',
        'videos_json': _videos('Video A', 'Video B'),
    })
    assert respuesta.status_code == 302

    with db.cursor() as cur:
        cur.execute('SELECT * FROM reels WHERE nombre = %s', (nombre,))
        reel = cur.fetchone()
    assert reel is not None
    assert float(reel['duracion_total']) == 2.5

    with db.cursor() as cur:
        cur.execute(
            'SELECT nombre, orden FROM videos WHERE reel_id = %s ORDER BY orden',
            (reel['id'],),
        )
        videos = cur.fetchall()
    assert [v['nombre'] for v in videos] == ['Video A', 'Video B']

    respuesta = client.post(f'/reels/editar/{reel["id"]}', data={
        'nombre': f'{nombre} editado',
        'duracion_total': '3',
        'videos_json': _videos('Video C'),
    })
    assert respuesta.status_code == 302

    with db.cursor() as cur:
        cur.execute('SELECT nombre FROM videos WHERE reel_id = %s', (reel['id'],))
        assert [v['nombre'] for v in cur.fetchall()] == ['Video C']

    respuesta = client.post(f'/reels/eliminar/{reel["id"]}')
    assert respuesta.status_code == 302

    with db.cursor() as cur:
        cur.execute('SELECT COUNT(*) AS total FROM reels WHERE id = %s', (reel['id'],))
        assert cur.fetchone()['total'] == 0
        cur.execute('SELECT COUNT(*) AS total FROM videos WHERE reel_id = %s', (reel['id'],))
        assert cur.fetchone()['total'] == 0


def test_agregar_video_a_reel_existente(superadmin, client, db):
    nombre = f'Reel {uuid.uuid4().hex[:8]}'
    client.post('/reels/crear', data={'nombre': nombre, 'duracion_total': '1'})

    with db.cursor() as cur:
        cur.execute('SELECT id FROM reels WHERE nombre = %s', (nombre,))
        reel_id = cur.fetchone()['id']

    respuesta = client.post(f'/reels/{reel_id}/agregar-video', data={
        'nombre': 'Video agregado',
        'duracion_segundos': '45',
        'orden': '1',
    })
    assert respuesta.status_code == 302

    with db.cursor() as cur:
        cur.execute(
            'SELECT nombre, duracion_segundos FROM videos WHERE reel_id = %s',
            (reel_id,),
        )
        video = cur.fetchone()
    assert video['nombre'] == 'Video agregado'
    assert video['duracion_segundos'] == 45
