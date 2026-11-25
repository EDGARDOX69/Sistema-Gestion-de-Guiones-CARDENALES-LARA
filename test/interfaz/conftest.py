"""Activa las pruebas de interfaz solo cuando se pide explicitamente.

El servidor y las credenciales E2E se cargan desde ``fixtures_e2e.py`` a
traves del ``conftest.py`` de la raiz.
"""

import os

ACTIVO = os.getenv('E2E') == '1'
collect_ignore_glob = [] if ACTIVO else ['test_*.py']
