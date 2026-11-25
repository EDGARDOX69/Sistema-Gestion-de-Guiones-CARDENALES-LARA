---
name: tests-pytest
description: Bootstrap y convenciones de tests con pytest para Itinerario (Flask + PyMySQL). El proyecto no tenía tests. Use when adding tests, creating test fixtures, testing controllers/models/validators, or when the user says "test", "pytest", "pruebas", "cobertura".
---

# Tests — Itinerario

Estado inicial: cero tests. Objetivo: empezar por la lógica de mayor riesgo, no cubrir todo.

## Setup mínimo (primera vez)

1. `venv/bin/pip install -r requirements-dev.txt`
2. La estructura ya existe en `test/`: `unitarias/`, `integracion/`, `backend/`,
   `humo/`, `interfaz/`, `rendimiento/`, `aceptacion/`, con `test/conftest.py`
   como base compartida:
   - Fixture `app`: `create_app()` con config de prueba — **BD de test separada** (`estadio_db_test` / `seguridad_test`, clonar esquema desde `estadio_db.sql` + `seguridad.sql`), `TESTING=True`, `WTF_CSRF_ENABLED=False`.
   - Fixture `client`: `app.test_client()`.
   - Fixture `bases_de_prueba`: clona los `.sql`; solo se ejecuta si un test pide `app` o lleva el marcador `db`.
   - Fixtures de datos: `crear_usuario`, `login`, `superadmin`, `crear_guion`, `crear_guion_completo`.
3. Correr con `venv/bin/pytest -q`. Para lo que no necesita MySQL: `venv/bin/pytest -m unit -q`.

Nunca correr tests contra las BD reales. Nunca enviar correos reales: patchear `app/helpers/email_service.py`.

## Qué testear primero (prioridad = riesgo)

1. **Validaciones puras** (`ValidacionesMixin`, `_parsear_fecha`, `_ordenar_datos`): baratas, sin BD.
2. **Auth**: login correcto/fallido, CAPTCHA, sesión única, reset password.
3. **Permisos**: ruta sin permiso → 302/403; con permiso → 200.
4. **Escrituras compuestas** (contrato+pagos): fallo a propósito a mitad → nada quedó escrito.
5. **Reportes PDF**: bytes para cada módulo con datos mínimos → empieza con `%PDF-`.

## Convenciones

- Un archivo por módulo y tipo: `test/unitarias/test_<modulo>_validaciones.py`,
  `test/integracion/test_<modulo>_crud.py`, `test/backend/test_<modulo>_rutas.py`,
  `test/humo/test_<modulo>_humo.py`, `test/aceptacion/test_<modulo>_flujo_completo.py`.
- Nombres que describan comportamiento: `test_login_fallido_incrementa_intentos`.
- Sin frameworks extra ni factories: funciones simples + fixtures en `test/conftest.py`.
- Los marcadores (`unit`, `integration`, `api`, `smoke`, `ui`, `acceptance`, `db`)
  se asignan solos por carpeta en `test/conftest.py`; no hace falta decorar cada test.
- Regla de oro: toda regla de lógica NUEVA lleva al menos un test que falle si se rompe.

## Checklist

- [ ] ¿Los tests corren contra BD de test?
- [ ] ¿Pasó `venv/bin/pytest -q` sin errores?
- [ ] ¿El test fallaría si la lógica se rompe? (muta mentalmente una línea)
