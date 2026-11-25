"""Limpieza de artefactos que generan las pruebas de integracion.

Los PDFs de reportes y las imagenes de premios se escriben en carpetas
reales de ``app/static``. Este conftest borra solo lo que aparece durante
cada prueba, sin tocar archivos que ya existian antes de correrla.
"""

from pathlib import Path

import pytest

from app.config import PROJECT_ROOT


CARPETAS = (
    Path(PROJECT_ROOT) / 'app' / 'static' / 'reportes',
    Path(PROJECT_ROOT) / 'app' / 'static' / 'uploads' / 'premios',
)


def _foto():
    return {
        carpeta: set(carpeta.rglob('*')) if carpeta.exists() else set()
        for carpeta in CARPETAS
    }


@pytest.fixture(autouse=True)
def _limpiar_artefactos_generados():
    antes = _foto()
    yield
    for carpeta, previos in antes.items():
        if not carpeta.exists():
            continue
        rutas = sorted(carpeta.rglob('*'), key=lambda p: len(p.parts), reverse=True)
        for ruta in rutas:
            if ruta in previos:
                continue
            try:
                if ruta.is_file():
                    ruta.unlink()
                elif ruta.is_dir() and not any(ruta.iterdir()):
                    ruta.rmdir()
            except OSError:
                pass
