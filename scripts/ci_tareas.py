"""Orquestador del pipeline de pruebas del módulo de gestión de tareas.

Es la única fuente de verdad de las etapas: lo invocan el workflow de GitHub
Actions, ``scripts/ci_tareas.sh`` y ``scripts/ci_tareas.ps1``. Cada etapa
ejecuta pytest contra ``estadio_db_test`` / ``seguridad_test`` y deja su log
en ``docs/pruebas/evidencias/tareas/``.

Uso::

    python scripts/ci_tareas.py                       # todas las etapas
    python scripts/ci_tareas.py --etapas unidad api  # solo algunas
    python scripts/ci_tareas.py --etapas interfaz    # E2E (E2E=1 automático)

Regla dura: nunca se ejecuta pytest contra las bases reales. Las etapas que
necesitan MySQL comprueban primero que el servidor responda y fallan con un
mensaje claro antes de tocar nada.
"""
from __future__ import annotations

import argparse
import json
import os
import socket
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
EVIDENCIAS = RAIZ / 'docs' / 'pruebas' / 'evidencias' / 'tareas'


def _pytest(*args):
    return [sys.executable, '-m', 'pytest', '-q', *args]


# Una etapa = lista de comandos. `opcional` no rompe el pipeline (auditorías).
ETAPAS = {
    'unidad': {
        'titulo': '1. Unitarias (sin MySQL)',
        'mysql': False,
        'comandos': [
            _pytest(
                'test/unitarias/test_tarea_model_unit.py',
                'test/unitarias/test_tareas_asignadas_model_unit.py',
                'Pruebas por modulo/gestion_tarea/unitarias',
                'Pruebas por modulo/notificaciones/unitarias',
            ),
        ],
    },
    'integracion': {
        'titulo': '2. Integración (BD de prueba)',
        'mysql': True,
        'comandos': [
            _pytest(
                'test/integracion/test_notificaciones.py',
                'test/integracion/test_tareas_pipeline_integridad.py',
                'Pruebas por modulo/gestion_tarea/integracion',
            ),
        ],
    },
    'api': {
        'titulo': '3. Backend / API (rutas y contratos)',
        'mysql': True,
        'comandos': [
            _pytest(
                'test/backend/test_tareas_asignadas_backend.py',
                'Pruebas por modulo/notificaciones/backend',
            ),
        ],
    },
    'humo': {
        'titulo': '4. Humo (rutas críticas, segundos)',
        'mysql': True,
        'comandos': [
            _pytest('Pruebas por modulo/gestion_tarea/humo'),
        ],
    },
    'aceptacion': {
        'titulo': '5. Aceptación (flujo de negocio completo)',
        'mysql': True,
        'comandos': [
            _pytest(
                'test/aceptacion/test_tareas_asignadas.py',
                'test/aceptacion/test_tarea_model.py',
            ),
        ],
    },
    'interfaz': {
        'titulo': '6. Interfaz / E2E (Playwright + SocketIO)',
        'mysql': True,
        'entorno': {'E2E': '1', 'PYTHONIOENCODING': 'utf-8'},
        'comandos': [
            _pytest(
                'test/interfaz/test_tareas_asignadas.py',
                'test/interfaz/test_tarea_model_interfaz.py',
                'Pruebas por modulo/gestion_tarea/interface',
                'Pruebas por modulo/notificaciones/interface',
            ),
        ],
    },
    'calidad': {
        'titulo': '7. Calidad (ruff bloquea; auditorías informativas)',
        'mysql': False,
        'comandos': [
            {
                'argv': [sys.executable, '-m', 'ruff', 'check', '--select',
                         'E9,F63,F7,F82', 'app', 'test', 'Pruebas por modulo'],
            },
            {
                'argv': [sys.executable, '-m', 'pip_audit', '-r', 'requirements.txt'],
                'opcional': True,
            },
            {
                'argv': [sys.executable, '-m', 'bandit', '-r', 'app', '-q'],
                'opcional': True,
            },
        ],
    },
}


def _mysql_disponible():
    host = os.getenv('DB_HOST', 'localhost')
    try:
        with socket.create_connection((host, 3306), timeout=3):
            return True
    except OSError:
        return False


def _argv(comando):
    return comando if isinstance(comando, list) else comando['argv']


def _ejecutar(comando, entorno, nombre):
    argv = _argv(comando)
    opcional = comando.get('opcional', False) if isinstance(comando, dict) else False
    ruta_log = EVIDENCIAS / f'{nombre}.log'
    EVIDENCIAS.mkdir(parents=True, exist_ok=True)
    print(f'  $ {" ".join(argv)}', flush=True)
    try:
        proceso = subprocess.Popen(
            argv,
            cwd=RAIZ,
            env=entorno,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding='utf-8',
            errors='replace',
            bufsize=1,
        )
    except FileNotFoundError:
        mensaje = f'Herramienta no instalada: {argv[0]}'
        ruta_log.write_text(mensaje + '\n', encoding='utf-8')
        if opcional:
            print(f'  OMITIDA (informativa): {mensaje}', flush=True)
            return 'omitida'
        print(f'  FALLO: {mensaje}', flush=True)
        return 'fallo'
    with ruta_log.open('w', encoding='utf-8') as log:
        for linea in proceso.stdout:
            log.write(linea)
            print(linea, end='', flush=True)
        codigo = proceso.wait()
    if codigo == 0:
        print('  OK', flush=True)
        return 'ok'
    if opcional:
        print(f'  INFORMATIVA (código {codigo}); no bloquea', flush=True)
        return 'informativa'
    print(f'  FALLO (código {codigo}); ver {ruta_log.relative_to(RAIZ)}', flush=True)
    return 'fallo'


def ejecutar_etapas(nombres):
    EVIDENCIAS.mkdir(parents=True, exist_ok=True)
    entorno = os.environ.copy()
    entorno.setdefault('CAPTCHA_ENABLED', '0')
    entorno.setdefault('SECRET_KEY', 'clave-de-pipeline')

    resultados = []
    for nombre in nombres:
        etapa = ETAPAS[nombre]
        print(f'\n== {etapa["titulo"]} ==', flush=True)
        if etapa.get('mysql') and not _mysql_disponible():
            print('  FALLO: MySQL no responde. Inicia MySQL antes de esta etapa.', flush=True)
            resultados.append({'etapa': nombre, 'estado': 'fallo', 'motivo': 'mysql no disponible'})
            break
        env_etapa = {**entorno, **etapa.get('entorno', {})}
        estados = [_ejecutar(comando, env_etapa, nombre)
                   for comando in etapa['comandos']]
        estado = 'fallo' if 'fallo' in estados else 'ok'
        resultados.append({'etapa': nombre, 'estado': estado, 'comandos': estados})
        if estado == 'fallo':
            break

    resumen = {
        'fecha': datetime.now(timezone.utc).isoformat(),
        'resultados': resultados,
        'final': 'ok' if len(resultados) == len(nombres)
        and all(r['estado'] == 'ok' for r in resultados) else 'fallo',
    }
    (EVIDENCIAS / 'resumen.json').write_text(
        json.dumps(resumen, indent=2, ensure_ascii=False) + '\n', encoding='utf-8'
    )
    print(f'\nResultado: {resumen["final"].upper()} — {EVIDENCIAS.relative_to(RAIZ)}', flush=True)
    return 0 if resumen['final'] == 'ok' else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        '--etapas', nargs='+', choices=list(ETAPAS), default=list(ETAPAS),
        help='Etapas a ejecutar, en orden. Por defecto todas.',
    )
    args = parser.parse_args()
    return ejecutar_etapas(args.etapas)


if __name__ == '__main__':
    sys.exit(main())
