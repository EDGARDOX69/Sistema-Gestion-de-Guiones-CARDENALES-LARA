#!/usr/bin/env bash
# Pipeline local equivalente al CI de GitHub Actions.
# Requiere MySQL encendido para la suite completa (unitarias no lo necesitan).
# Uso: ./scripts/ci_local.sh
set -euo pipefail

RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$RAIZ"

if [[ -f venv/bin/activate ]]; then
  # shellcheck disable=SC1091
  source venv/bin/activate
fi

EVIDENCIAS="docs/pruebas/evidencias"
mkdir -p "$EVIDENCIAS"/{tests,coverage,e2e,ci}

echo "== 1/6 pytest + cobertura =="
pytest -q \
  --junitxml="$EVIDENCIAS/tests/junit.xml" \
  --cov=app \
  --cov-report=term-missing \
  --cov-report=html:"$EVIDENCIAS/coverage/html" \
  --cov-report=xml:"$EVIDENCIAS/coverage/coverage.xml" \
  | tee "$EVIDENCIAS/tests/pytest.log"

echo "== 2/6 ruff (errores reales) =="
ruff check --select E9,F63,F7,F82 app test "Pruebas por modulo" | tee "$EVIDENCIAS/ci/ruff.log"

echo "== 3/6 pip-audit (informativo) =="
pip-audit -r requirements.txt | tee "$EVIDENCIAS/ci/pip-audit.log" || true

echo "== 4/6 bandit (informativo) =="
bandit -r app -q | tee "$EVIDENCIAS/ci/bandit.log" || true

echo "== 5/6 Playwright E2E =="
if [[ -d test/interfaz ]]; then
  E2E=1 pytest -q test/interfaz "Pruebas por modulo" -m ui | tee "$EVIDENCIAS/e2e/playwright.log" || true
else
  echo "test/interfaz/ no encontrado; se omite E2E"
fi

echo "== 6/6 resumen =="
echo "Evidencias en: $EVIDENCIAS"
ls -R "$EVIDENCIAS" | head -n 60
