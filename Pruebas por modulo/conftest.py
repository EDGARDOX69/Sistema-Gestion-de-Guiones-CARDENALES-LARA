"""Suite organizada por modulo.

Los fixtures y los marcadores automaticos vienen del ``conftest.py`` de la
raiz. Las pruebas de interfaz solo se colectan con ``E2E=1``.
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

ACTIVO = os.getenv('E2E') == '1'
collect_ignore_glob = (
    [] if ACTIVO else [
        'interface/test_*.py',
        '*/interface/test_*.py',
        'interfaz/test_*.py',
        '*/interfaz/test_*.py',
    ]
)
