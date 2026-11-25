"""Configuracion global de pytest para Itinerario.

Carga los fixtures compartidos y asigna marcadores automaticos segun la
subcarpeta del test. Vale tanto para ``test/`` como para
``Pruebas por modulo/``.
"""

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

pytest_plugins = ('fixtures_pruebas', 'fixtures_e2e')


_CARPETAS = {
    'unitarias': (pytest.mark.unit,),
    'integracion': (pytest.mark.integration, pytest.mark.db),
    'backend': (pytest.mark.api, pytest.mark.db),
    'humo': (pytest.mark.smoke, pytest.mark.db),
    'interface': (pytest.mark.ui,),
    'interfaz': (pytest.mark.ui,),
    'aceptacion': (pytest.mark.acceptance, pytest.mark.db),
    'rendimiento': (pytest.mark.perf,),
}


def pytest_collection_modifyitems(config, items):
    """Asigna el marcador del tipo de prueba segun la subcarpeta del archivo."""
    for item in items:
        partes = Path(str(item.fspath)).parts
        for carpeta, marcas in _CARPETAS.items():
            if carpeta in partes:
                for marca in marcas:
                    item.add_marker(marca)
                break
