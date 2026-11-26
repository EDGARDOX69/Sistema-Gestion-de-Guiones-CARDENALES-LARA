#!/usr/bin/env bash
# Envoltorio local del orquestador multiplataforma scripts/ci_tareas.py.
# Uso: ./scripts/ci_tareas.sh [nombre etapa ...]
set -euo pipefail

RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$RAIZ"

if [[ -f venv/bin/python ]]; then
  PY=venv/bin/python
elif [[ -f venv/Scripts/python.exe ]]; then
  PY=venv/Scripts/python.exe
else
  PY=python3
fi

exec "$PY" scripts/ci_tareas.py "$@"
