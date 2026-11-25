# Guía maestra de pruebas — Itinerario

Esta guía está pensada para que cualquier integrante del equipo pueda **entender
qué prueba está escribiendo, por qué existe, en qué archivo va, cómo se ejecuta,
qué resultado debe ver y cómo replicarlo en su propio módulo**.

El módulo **guion** se usa como ejemplo resuelto de punta a punta. Al final hay
una receta con marcadores (`{{MODULO}}`) para copiar el patrón a inventario,
contratos, premios, tareas, balances, reportes o cualquier módulo nuevo.

---

## 0. Antes de empezar

### 0.1 La regla de oro

> Los tests **nunca** tocan las bases reales (`estadio_db`, `seguridad`).
> `test/conftest.py` clona los dumps `.sql` en `estadio_db_test` y
> `seguridad_test` al inicio de la sesión.

Si un test escribe en una base real, el test está mal escrito. No hay excepciones.

### 0.2 Requisitos

- `venv/` del proyecto.
- MySQL/MariaDB encendido (XAMPP en macOS) y `.env` con `DB_HOST`, `DB_USER`,
  `DB_PASSWORD`.
- Dependencias de desarrollo:

```bash
source venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
```

- Para interfaz: `pip install -r test/interfaz/requirements.txt` y
  `python -m playwright install chromium`.

### 0.3 Mapa de la carpeta de pruebas

```
test/
├── conftest.py        # fixtures compartidas y marcadores automáticos
├── unitarias/         # lógica pura, sin Flask ni MySQL
├── integracion/       # modelos + Flask + MySQL de prueba
├── backend/           # rutas HTTP/API, permisos, JSON, validación de servidor
├── humo/              # recorrido mínimo: "abre y no explota"
├── interfaz/          # Playwright transversal (navegador real)
├── rendimiento/       # Locust (no lo ejecuta pytest)
└── aceptacion/        # flujo de negocio completo

Pruebas por modulo/
├── conftest.py        # entrada de la suite, gate E2E y ruta compartida
├── soporte_api.py     # login con varios actores
├── soporte_ui.py      # login real para Playwright (CAPTCHA solo si está activo)
├── soporte_modulos.py # rutas y metadatos de los 18 módulos
└── <modulo>/
    ├── unitarias/
    ├── integracion/
    ├── backend/
    ├── humo/
    ├── interface/
    ├── aceptacion/
    └── rendimiento/
```

Los 18 módulos (`auth`, `balance`, `bitacora`, `chat`, `contrato`, `dashboard`,
`en_vivo`, `gestion_tarea`, `guion`, `inventario`, `mantenimiento`,
`notificaciones`, `patrocinador`, `premio`, `reels`, `reportes`, `rol`,
`usuario`) tienen las siete subcarpetas. Las carpetas internas de cada módulo
tienen un `__init__.py` para evitar el error clásico `import file mismatch`.

---

## 1. Los siete tipos de prueba

| Tipo | Pregunta que responde | ¿Necesita MySQL? | Velocidad |
|---|---|---|---|
| Unitaria | ¿La función calcula/valida bien, aislada? | No | milisegundos |
| Integración | ¿El modelo y la transacción escriben bien en la BD? | Sí | segundos |
| Backend/API | ¿La ruta exige permisos, valida y responde lo pactado? | Sí | segundos |
| Humo | ¿El módulo está de pie y ninguna vista devuelve 500? | Sí | segundos |
| Interfaz | ¿El usuario puede hacer el flujo en un navegador real? | Sí (BD *_test) | decenas de segundos |
| Rendimiento | ¿Aguanta 30 usuarios concurrentes? | Sí + servidor | minutos |
| Aceptación | ¿Cumple el recorrido de negocio completo? | Sí | segundos |

La lógica de la pirámide: muchas unitarias baratas, integración para las reglas
que dependen de la BD, pocas de interfaz y rendimiento.

---

## 2. Cómo se marcan los tests

No hace falta decorar cada función. El `conftest.py` de la raíz asigna el
marcador según la carpeta del archivo, tanto en `test/` como en
`Pruebas por modulo/`:

| Carpeta | Marcadores |
|---|---|
| `unitarias/` | `unit` |
| `integracion/` | `integration`, `db` |
| `backend/` | `api`, `db` |
| `humo/` | `smoke`, `db` |
| `interfaz/` | `ui` |
| `interface/` | `ui` |
| `rendimiento/` | `perf` |
| `aceptacion/` | `acceptance`, `db` |

`db` es el marcador que activa el app context y la clonación de bases. Por eso
`pytest -m unit` funciona **sin MySQL**: ningún test unitario pide `app` ni lleva
`db`.

---

## 3. Preparación del entorno

### 3.1 Clonación de bases

Al pedir la primera fixture `app`, `bases_de_prueba` hace:

1. `DROP DATABASE IF EXISTS estadio_db_test` / `seguridad_test`.
2. Las crea vacías.
3. Aplica `estadio_db.sql` y `seguridad.sql` renombrando los esquemas.
4. Deja las bases listas para toda la sesión de pytest.

Esto ocurre **una vez por sesión**. No hay truncado entre tests: los datos se
acumulan. Por eso los tests usan nombres únicos (`uuid`) y comparan por id, no
por cantidad total.

> **Muy importante:** no ejecutes dos sesiones de `pytest` a la vez. Cada una
> hace `DROP DATABASE` al arrancar y la otra se queda esperando un lock de
> MySQL. Si ves un test colgado, revisa que no haya otro pytest abierto.

### 3.2 Fixtures disponibles

| Fixture | Para qué |
|---|---|
| `app` | Instancia Flask con CSRF apagado y correos mockeados |
| `client` | Cliente HTTP de pruebas |
| `crear_usuario(rol=...)` | Crea un usuario único en `seguridad_test` |
| `login(usuario)` | Login completo (CAPTCHA activo o desactivado) |
| `superadmin` | Usuario con sesión iniciada |
| `crear_guion(...)` | Inserta una cabecera de guion con su fecha |
| `crear_guion_completo(...)` | Guion + 2 pregame + 2 game listos para EN VIVO |

Si tu módulo necesita datos base, agrega una fixture en `test/conftest.py` con el
patrón `crear_<entidad>`; no la dupliques en cada archivo.

---

## 4. Comandos de referencia

```bash
# Suite completa (requiere MySQL)
venv/bin/pytest -q

# Solo lógica pura (no requiere MySQL)
venv/bin/pytest -m unit -q

# Por tipo
venv/bin/pytest -m integration -q
venv/bin/pytest -m api -q
venv/bin/pytest -m smoke -q
venv/bin/pytest -m acceptance -q

# Un archivo o un test concreto
venv/bin/pytest test/integracion/test_guion_crud.py -q
venv/bin/pytest test/backend/test_guion_rutas.py::test_publicar_cambia_el_estado -vv

# Cobertura
venv/bin/pytest -q --cov=app --cov-report=term-missing

# Interfaz (navegador real; servidor E2E con bases *_test)
E2E=1 .venv-win/Scripts/python.exe -m pytest test/interfaz -q

# Suite nueva por módulo
.venv-win/Scripts/python.exe -m pytest "Pruebas por modulo" -q

# Interfaz de todos los módulos
$env:E2E='1'; .venv-win/Scripts/python.exe -m pytest test/interfaz "Pruebas por modulo" -m ui -q

# Rendimiento (servidor levantado aparte; escenarios preparados)
locust -f "Pruebas por modulo/rendimiento/locustfile_criticas.py" --headless \
  -u 10 -r 2 -t 30s --host http://127.0.0.1:5002

# Calidad estática
venv/bin/ruff check --select E9,F63,F7,F82 app test "Pruebas por modulo"
```

Resultado real de la última corrida en este repositorio (19/11/2026):

```
943 passed, 0 skipped, 0 xfailed in 221.52s   # suite completa sin navegador
565 passed, 378 deselected in 4.13s           # -m unit, incluso sin MySQL
33 passed, 213 deselected in 144.00s          # E2E de interfaz (Chromium)
4 passed                                      # aislamiento de bases *_test
```

Los hallazgos GU-API-06, REP-SEC-01 y BAL-DAT-01 quedaron corregidos y sus
pruebas pasan sin xfail. Los 18 escenarios Locust por módulo quedaron
preparados, pero no se ejecutaron en esta sesión; no se reportan métricas de
carga.

---

## 5. Anatomía de un test

```python
"""GU-AT — Prueba de aceptación del flujo completo de un guion."""
import pytest

pytestmark = [pytest.mark.acceptance, pytest.mark.db]


def test_flujo_completo_del_guion(client, superadmin, app):
    """GU-AT-01: recorrido de negocio de punta a punta."""
    resp = client.post('/guiones/crear', data={'nombre': 'Show Viernes'})
    assert resp.status_code == 302
```

- **Docstring con ID** (`GU-AT-01`): conecta el test con la matriz de trazabilidad.
- **Nombre en español** que describe comportamiento, no implementación.
- **`pytestmark`**: solo si el archivo mezcla tipos; lo normal es que la carpeta
  ya ponga el marcador.
- **Un assert por idea**: si falla, sabes exactamente qué regla se rompió.
- **Datos únicos**: `uuid.uuid4().hex[:6]` evita choques entre tests.

### Cómo leer un fallo

```
FAILED test/backend/test_guion_rutas.py::test_publicar_cambia_el_estado
E  assert 'borrador' == 'publicado'
```

1. Lee el `assert`: te dice esperado vs obtenido.
2. Corre solo ese test con `-vv`.
3. Si necesitas entrar al depurador: `--pdb`.
4. Si quieres repetir solo los últimos fallos: `--lf`.
5. Si el error es `pymysql.err.OperationalError`, MySQL no está encendido.

---

## 6. Los siete tipos, uno por uno

### 6.1 Pruebas unitarias

**Qué son:** funciones puras, sin Flask, sin MySQL, sin red.

**Por qué:** son las más baratas y las que más rápido señalan un error de lógica
(parseos, validaciones, cálculos, formateos).

**Archivo:** `test/unitarias/test_<modulo>_validaciones.py`

**Receta:**

1. Importa solo la función o clase que vas a probar.
2. Cubre el caso normal, los bordes y la basura.
3. Si la función devuelve `None`/`False`, verifica también que no lanza excepción.

**Ejemplo real (guion):**

```python
from app.model.guion_model import _parsear_duracion

def test_parsear_duracion_convierte_a_segundos():
    assert _parsear_duracion('1,30') == 90
    assert _parsear_duracion('90') == 5400      # sin coma = minutos
    assert _parsear_duracion('abc') == 0
```

**Comando:** `venv/bin/pytest -m unit -q`

**Resultado esperado:** puntos verdes y `N passed`. No debe aparecer ninguna
conexión a MySQL; si MySQL está apagado, igual debe pasar.

**Errores frecuentes:**
- Pedir `app` o `client` sin necesidad → la unitaria deja de ser unitaria.
- Probar el comportamiento que *debería* ser en vez del que *es*. Si el código
  tiene una rareza, documéntala con un test y anota el hallazgo.

---

### 6.2 Pruebas de integración

**Qué son:** el modelo contra una BD de prueba real, con transacciones.

**Por qué:** aquí viven las reglas que no se pueden probar en memoria: escrituras
compuestas, borrado lógico, orden, duplicados, réplicas.

**Archivo:** `test/integracion/test_<modulo>_crud.py`

**Receta:**

1. Pide `app` (o una fixture que dependa de `app`).
2. Crea datos con el modelo real.
3. Verifica en la BD con una consulta directa cuando el modelo podría mentir.
4. Prueba el caso inválido y confirma que **no escribió nada**.

**Ejemplo real (guion):**

```python
def test_registrar_crea_guion_y_fecha_en_una_transaccion(app):
    modelo = GuionModel()
    guion_id = modelo.registrar({
        'nombre': 'Guion Integración',
        'fecha': date(2026, 12, 1),
        'tiempo_inning': 5400,
    })
    assert guion_id is not None
    assert len(modelo.obtener_fechas(guion_id)) == 1


def test_eliminar_es_borrado_logico(app, crear_guion):
    guion_id = crear_guion()
    assert GuionModel().eliminar(guion_id) is True
    # sigue en la tabla, pero con status = 0
```

**Comando:** `venv/bin/pytest -m integration -q`

**Resultado esperado:** `passed`; si MySQL está apagado, `ERROR at setup` con
`pymysql.err.OperationalError`.

**Errores frecuentes:**
- Comparar `fetchall()` con `[]`: PyMySQL devuelve una tupla. Usa `len(...) == 0`.
- Asumir que la BD está vacía: otros tests dejan datos. Filtra por id/nombre único.
- Olvidar que `consultar()` puede excluir borrados lógicos (`status = 1`).

---

### 6.3 Pruebas de backend / API

**Qué son:** las rutas HTTP reales: permisos, códigos de estado, JSON, validación
de servidor y efectos en la BD.

**Por qué:** una validación solo en JavaScript no protege nada. Estas pruebas
demuestran que el servidor rechaza lo que debe rechazar.

**Archivo:** `test/backend/test_<modulo>_rutas.py`

**Receta:**

1. Anónimo → redirección al login.
2. Usuario sin permiso → 302 al dashboard (GET) o 403 (POST).
3. Superadmin → 200.
4. POST inválido → no escribe.
5. POST válido → efecto esperado + bitácora.
6. Ruta JSON → contrato exacto.

**Ejemplo real (guion):**

```python
def test_anonimo_redirige_al_login(client):
    resp = client.get('/guiones/')
    assert resp.status_code == 302
    assert '/auth/login' in resp.headers['Location']


def test_publicar_cambia_el_estado(client, superadmin, crear_guion):
    guion_id = crear_guion()
    assert client.post(f'/guiones/publicar/{guion_id}').status_code == 302
    assert GuionModel().obtener_por_id(guion_id)['estado'] == 'publicado'
```

**Comando:** `venv/bin/pytest -m api -q`

**Resultado esperado:** verde. Un POST sin permiso debe devolver 403, no 200.

**Errores frecuentes:**
- Esperar 302 en un POST sin permiso: el decorador devuelve **403**.
- Olvidar `follow_redirects=True` cuando quieres leer el mensaje flash.
- Probar el JSON con `resp.data` en vez de `resp.get_json()`.

---

### 6.4 Pruebas de humo

**Qué son:** un recorrido corto por las vistas principales.

**Por qué:** antes de una demo o de un despliegue, confirman en segundos que
nada está roto de forma evidente (500, import, plantilla).

**Archivo:** `test/humo/test_<modulo>_humo.py`

**Receta:**

1. Dashboard 200.
2. Crear el registro mínimo.
3. Recorrer las rutas GET con un registro real.
4. Confirmar que un id inexistente redirige, no explota.

**Ejemplo real (guion):**

```python
def test_rutas_del_modulo_no_devuelven_500(client, superadmin, crear_guion):
    guion_id = crear_guion()
    for ruta in ('/guiones/', f'/guiones/editar/{guion_id}',
                 f'/guiones/previsualizar/{guion_id}'):
        resp = client.get(ruta)
        assert resp.status_code in (200, 302)
```

**Comando:** `venv/bin/pytest -m smoke -q`

**Resultado esperado:** debe tardar segundos, no minutos. Si tarda, está haciendo
demasiado trabajo para ser humo.

---

### 6.5 Pruebas de interfaz

**Qué son:** Playwright controlando Chromium contra la aplicación real.

**Por qué:** demuestran el flujo tal como lo vive el operador: login, formularios,
navegación y formularios.

**Archivo:** `test/interfaz/test_<modulo>_ui.py`

**Receta:**

1. Login real (los helpers leen el CAPTCHA del DOM solo si está activo).
2. Navegar a la pantalla del módulo.
3. Rellenar el formulario y comprobar la redirección.
4. Limpiar los datos creados (borrado lógico) al final del test.

**Ejemplo real (guion):**

```python
def test_crear_guion_desde_la_interfaz(page: Page):
    _login(page)
    nombre, guion_id = _crear_guion_por_ui(page)
    expect(page.locator('#tipoSelect')).to_be_visible()
    page.goto(f'/guiones/eliminar/{guion_id}')   # limpieza
```

**Comando:**

```bash
# El servidor E2E se levanta solo en 127.0.0.1:5002 contra las bases *_test.
# El usuario de prueba se crea en seguridad_test; no se usan credenciales reales.
E2E=1 .venv-win/Scripts/python.exe -m pytest test/interfaz -q
E2E=1 .venv-win/Scripts/python.exe -m pytest "Pruebas por modulo" -m ui -q
```

**Resultado esperado:** `33 passed` si se ejecutan la suite histórica y las interfaces de los 18 módulos. Los fallos
dejan captura, video y `trace.zip` en `test/interfaz/test-results/` cuando se
pasan las opciones de Playwright.

**Errores frecuentes:**
- Correr `pytest` normal y que Playwright intente ejecutarse: está bloqueado a
  propósito; usa `E2E=1`.
- Reutilizar un servidor ya encendido: el conftest lo rechaza para no arriesgar
  una conexión a las bases reales. Detén el servidor o usa `E2E_PORT`.
- Poner credenciales en el código: el usuario E2E se crea automáticamente en
  `seguridad_test`; no se necesitan `E2E_EMAIL` ni `E2E_PASSWORD`.
- Olvidar que los datos creados viven en las bases de prueba: no se limpian a
  mano porque las bases se recrean al inicio de cada sesión.

---

### 6.6 Pruebas de rendimiento

**Qué son:** carga concurrente con Locust contra un servidor levantado.

**Por qué:** el sistema se usa en vivo con ~30 espectadores; hay que saber si el
dashboard y el estado del show aguantan.

**Archivos:** `Pruebas por modulo/rendimiento/locustfile_criticas.py` y un `locustfile_<modulo>.py` por cada módulo.

**Receta:**

1. Levanta el servidor E2E contra las bases de prueba (por ejemplo, con el
   fixture de interfaz o con `DB_NAME_ESTADIO=estadio_db_test` y
   `DB_NAME_SEGURIDAD=seguridad_test`).
2. Ejecuta las tareas de lectura sobre dashboard, guion, guion en vivo, balance,
   reportes y login.
3. Mide p95, errores y peticiones por segundo.

**Comando:**

```bash
# Servidor en otra terminal, siempre contra las bases *_test.
locust -f "Pruebas por modulo/rendimiento/locustfile_criticas.py" --headless \
  -u 10 -r 2 -t 30s --host http://127.0.0.1:5002
```

**Resultado esperado:** 0 % de errores y p95 del dashboard por debajo de 800 ms
en local. Locust imprime la tabla al terminar.

**Estado real:** los 19 escenarios quedaron preparados, pero no se ejecutaron en
la sesión del 19/11/2026. No se reportan tiempos ni percentiles.

**Errores frecuentes:**
- Apuntar a las bases reales sin querer: el servidor debe usar `*_test`.
- Correrlo en CI: no está pensado para eso; es una prueba manual.
- Ejecutarlo al mismo tiempo que pytest: ambos recrean las bases de prueba y se
  bloquean. Una sesión a la vez.

---

### 6.7 Pruebas de aceptación

**Qué son:** un recorrido completo de negocio, de principio a fin.

**Por qué:** es la prueba que se le muestra a la profesora: demuestra que el
módulo sirve para lo que fue creado.

**Archivo:** `test/aceptacion/test_<modulo>_flujo_completo.py`

**Receta (guion):**

1. Crear guion.
2. Cargar 2 pregame y 2 game.
3. Previsualizar.
4. Publicar.
5. Iniciar EN VIVO.
6. Avanzar.
7. Retroceder.
8. Finalizar y comprobar que los relojes quedaron limpios.

**Comando:** `venv/bin/pytest -m acceptance -q`

**Resultado esperado:** un solo test verde que cuenta la historia completa.

---

### 6.8 Prueba de usabilidad interna

**Qué es:** un piloto interno con un usuario de prueba y Chromium, sin presentarlo como Beta externa.

**Qué se hizo:**
- Se ejecutaron 11 tareas: login, dashboard, crear y previsualizar guion,
  balance, inventario, tareas, reportes, notificaciones y vistas móviles.
- Se midió el tiempo de cada tarea.
- Se comprobó que ninguna pantalla mostrara `Error interno`.
- Se verificó el viewport 390x844 en dashboard y balance.

**Resultado real:**
- `11/11` tareas OK.
- Login: 8,28 s.
- Dashboard: 0,78 s.
- Crear guion: 2,12 s.
- Previsualizar guion: 0,77 s.
- Balance: 1,10 s.
- Inventario: 0,90 s.
- Tareas: 1,09 s.
- Reportes: 0,86 s.
- Notificaciones: 0,82 s.
- Dashboard y balance en 390x844: sin desbordamiento horizontal.

**Evidencia:**
`docs/pruebas/evidencias/usabilidad_interna/` incluye:
- `usabilidad_interna.txt`
- `usabilidad_interna.json`
- capturas de las tareas
- video de la sesión

**Estado:** la Beta con un usuario externo del estadio sigue pendiente.

---

## 7. Caso resuelto: módulo guion

| ID | Archivo | Qué valida |
|---|---|---|
| GU-UT-01…13 | `test/unitarias/test_guion_validaciones.py` | `_parsear_duracion`, nombre 3–50, fecha obligatoria, contenido 5–500, pregame exige hora, game exige inning y medio |
| GU-IT-01…19 | `test/integracion/test_guion_crud.py` | registrar guion + fecha, borrado lógico, modificar, replicar, orden de elementos, ocupados, último orden |
| GU-API-01…22 | `test/backend/test_guion_rutas.py` | permisos, 403 en POST, crear, verificar nombre, agregar/editar/eliminar elemento, publicar, replicar, bitácora |
| GU-SM-01…04 | `test/humo/test_guion_humo.py` | dashboard, crear mínimo, rutas sin 500, id inexistente |
| GU-UI-01…04 | `test/interfaz/test_guion_ui.py` | login, dashboard, formulario, crear y previsualizar |
| GU-PF-01 | `Pruebas por modulo/rendimiento/locustfile_criticas.py` | Rutas críticas: dashboard, guion, EN VIVO, balance, reportes y login |
| GU-AT-01 | `test/aceptacion/test_guion_flujo_completo.py` | crear → publicar → EN VIVO → avanzar → retroceder → finalizar |

Estado real: **78 casos de guion ejecutados: 78 aprobados**, incluidos los tres
casos de nombre base que antes estaban en xfail. El escenario de rendimiento
nuevo quedó preparado, pero no se ejecutó en la sesión del 19/11/2026. La
evidencia histórica `docs/pruebas/evidencias/locust_30_usuarios_stats.csv`
corresponde a una corrida previa de 30 usuarios sobre guion y no se usa para
afirmar el rendimiento actual.

---

## 8. Cómo replicarlo en cualquier módulo

### Paso 1 — Inventario del módulo

Antes de escribir una línea, responde:

| Pregunta | Dónde mirarlo |
|---|---|
| ¿Cuál es el modelo? | `app/model/<modulo>_model.py` |
| ¿Cuál es el controlador y el blueprint? | `app/controller/<modulo>_controller.py` |
| ¿Qué rutas expone? | `@bp.route(...)` |
| ¿Qué permisos exige? | `app/helpers/permission_map.py` |
| ¿Qué tablas usa? | `.sql` de la raíz + el modelo |
| ¿Qué vistas tiene? | `app/view/<modulo>/` |
| ¿Qué formularios/ids usa? | `app/static/js/Gestion<Modulo>.js` y las plantillas |

### Paso 2 — Crear los archivos

```
test/unitarias/test_<modulo>_validaciones.py
test/integracion/test_<modulo>_crud.py
test/backend/test_<modulo>_rutas.py
test/humo/test_<modulo>_humo.py
test/interfaz/test_<modulo>_ui.py
test/aceptacion/test_<modulo>_flujo_completo.py
test/rendimiento/locustfile_<modulo>.py
```

Copia el archivo de guion más parecido y renombra:

- `GuionModel` → `{{MODELO}}`
- `/guiones/` → `/{{RUTA}}/`
- `guion.view/create/edit/delete` → `{{MODULO}}.view/create/edit/delete`
- `guiones` → `{{TABLA}}`

### Paso 3 — Empezar por las unitarias

Escribe primero las funciones puras. Si no hay funciones puras, extrae la lógica
de validación a un método y pruébalo. Ejecuta `pytest -m unit -q`: debe pasar sin
MySQL.

### Paso 4 — Integración

Prueba el CRUD y, sobre todo, las escrituras compuestas. Si el módulo escribe en
dos tablas, verifica que ambas queden consistentes y que un fallo no deje basura.

### Paso 5 — Backend/API

Cubre los permisos del `permission_map` y los POST inválidos. Aquí se descubren
los huecos de validación del servidor.

### Paso 6 — Humo, interfaz y aceptación

- Humo: todas las vistas con un registro real.
- Interfaz: el flujo principal en el navegador (login real; el CAPTCHA se rellena solo si está activo).
- Aceptación: el recorrido de negocio que contarías en la exposición.

### Paso 7 — Rendimiento

Solo si el módulo se usa durante el show o tiene listados grandes.

### Paso 8 — Matriz de trazabilidad

Cada test debe tener un ID y una fila en la matriz.

---

## 9. Matriz de trazabilidad

Formato sugerido (una fila por caso):

| ID | Módulo | Requisito | Tipo | Archivo::test | Datos | Resultado esperado | Estado | Evidencia |
|---|---|---|---|---|---|---|---|---|
| GU-AT-01 | Guion | Crear y ejecutar un guion completo | Aceptación | `test/aceptacion/test_guion_flujo_completo.py::test_flujo_completo_del_guion` | Guion con 2 pregame + 2 game | Publicado, EN VIVO, avance/retroceso y finalizado | ✅ | `pytest -m acceptance` |

Convención de IDs:

```
<MÓDULO>-<TIPO>-<NN>
GU-UT-01   unitaria
GU-IT-01   integración
GU-API-01  backend/API
GU-SM-01   humo
GU-UI-01   interfaz
GU-PF-01   rendimiento
GU-AT-01   aceptación
```

---

## 10. Evidencias para el informe

```bash
mkdir -p docs/pruebas/evidencias
venv/bin/pytest -q \
  --junitxml=docs/pruebas/evidencias/junit.xml \
  --cov=app --cov-report=html:docs/pruebas/evidencias/coverage \
  --cov-report=term-missing | tee docs/pruebas/evidencias/pytest.log

venv/bin/ruff check --select E9,F63,F7,F82 app test \
  | tee docs/pruebas/evidencias/ruff.log
```

- `junit.xml`: resultados por caso (se puede abrir en el informe).
- `coverage/html/index.html`: líneas cubiertas.
- `pytest.log`: salida real, sin editar.
- `test/interfaz/reporte.html`: reporte visual del E2E.
- `test/interfaz/test-results/`: capturas/videos/traces de fallos.

Regla de honestidad: en el informe se pega la salida real. Si un caso falla, se
documenta el fallo y su diagnóstico; no se maquilla.

---

## 11. Problemas conocidos y cómo resolverlos

| Síntoma | Causa | Solución |
|---|---|---|
| `pymysql.err.OperationalError` en setup | MySQL apagado | Enciende XAMPP o corre `pytest -m unit` |
| Test colgado sin avanzar | Otra sesión de pytest está recreando las BDs | Cierra la otra sesión; nunca corras dos a la vez |
| `import file mismatch` | Dos archivos con el mismo nombre sin `__init__.py` | Mantén los `__init__.py` de cada carpeta |
| Playwright intenta correr en `pytest` normal | Falta el gate | Usa `E2E=1`; sin él las pruebas de interfaz se ignoran |
| `Unknown pytest.mark.ui` | Se ejecuta desde una carpeta sin el `pytest.ini` de la raíz | Ejecuta desde la raíz: `E2E=1 pytest test/interfaz "Pruebas por modulo" -m ui` |
| Un test ve datos de otro | Las BDs no se truncan entre tests | Usa nombres/ids únicos y filtra por ellos |
| `g._login_user` cacheado | Flask-Login cachea el usuario en el app context | `g.pop('_login_user', None)` al cambiar de actor |
| `Multiple primary key defined` en logs | `rol_model._asegurar_schema` se ejecuta en cada arranque | Ruido conocido; no afecta los tests |

---

## 12. Checklist antes de cerrar un módulo

- [ ] `pytest -m unit` pasa sin MySQL.
- [ ] `pytest -m integration` pasa con MySQL.
- [ ] `pytest -m api` cubre permisos y POST inválidos.
- [ ] `pytest -m smoke` pasa en segundos.
- [ ] `E2E=1 pytest test/interfaz` pasa (si aplica).
- [ ] `E2E=1 pytest "Pruebas por modulo" -m ui` pasa (si aplica).
- [ ] `pytest -m acceptance` cuenta el flujo completo.
- [ ] `pytest -q` completo en verde (943 passed, 0 skipped, 0 xfailed).
- [ ] `ruff check --select E9,F63,F7,F82 app test "Pruebas por modulo"` sin errores.
- [ ] Cada caso tiene ID y fila en la matriz.
- [ ] Las evidencias están en `docs/pruebas/evidencias/`.

---

## 13. Hallazgos corregidos y deuda conocida

1. **GU-API-06 — nombre base sin validar en `crear` (corregido).**
   `guion_controller.crear` ahora valida el nombre base antes de concatenar la
   fecha. Un nombre vacío o de 1–2 caracteres vuelve al formulario con estado
   200 y no escribe en la BD. Los tres casos de
   `test/backend/test_guion_rutas.py` pasan sin xfail.

2. **REP-SEC-01 — autorización de reportes (corregido).**
   Todos los endpoints de `/reportes` usan el mapa `REPORTES` con
   `reportes.view`. El permiso se añadió al catálogo, a `seguridad.sql` y a los
   roles Superadmin y Administrador. Un GET sin permiso redirige al dashboard;
   un POST devuelve 403. Las pruebas cubren ambos casos.

3. **BAL-DAT-01 — pagos de ejemplo inactivos (corregido).**
   Los 8 pagos del dump ahora tienen `estado = 0`, suman 141.000,00 y el
   balance inicial los incluye. La prueba de integración verifica el conteo y
   el monto; ya no hay xfail.

4. **Esquema `seguridad` escrito a mano en algunos modelos (deuda).**
   `mantenimiento_model`, `inventario_model`, `bitacora_model` y `tarea_model`
   todavía tienen `seguridad.usuarios` fijo. En las pruebas se redirige con
   `DictCursorTest` y `soporte_pruebas.redirigir_esquemas`, así que no se toca
   la base real, pero conviene calificarlo con
   `DATABASE_CONFIG['seguridad']['database']` como ya se hizo en
   `reportes_catalogo.py`, `reportes_data.py` y `reportes_controller.py`.

5. **Presencia SocketIO en memoria.** Solo es válida con `-w 1`; no es un bug de
   las pruebas, pero conviene recordarlo al escalar.

6. **Ruido de `rol_model._asegurar_schema`.** Intenta añadir una clave primaria
   existente y registra `Multiple primary key defined` en cada arranque. Es
   ruido de logs, no un fallo de prueba.

6. **Dos sesiones de pytest a la vez.** Cada sesión elimina y recrea
   `estadio_db_test` y `seguridad_test`. Si dos sesiones se solapan, una puede
   ver tablas a medio crear. Ejecuta una sola sesión a la vez; los comandos de
   evidencia de esta guía ya lo respetan.

---

## Anexo — Plantilla rápida para un módulo nuevo

```python
# test/unitarias/test_mimodulo_validaciones.py
import pytest
pytestmark = pytest.mark.unit

def test_mimodulo_rechaza_campo_vacio():
    from app.model.mimodulo_model import MiModuloModel
    m = MiModuloModel()
    assert m._validar_datos() is False
```

```python
# test/integracion/test_mimodulo_crud.py
import pytest
pytestmark = [pytest.mark.integration, pytest.mark.db]

def test_registrar_y_leer(app):
    from app.model.mimodulo_model import MiModuloModel
    modelo = MiModuloModel()
    nuevo_id = modelo.registrar({'nombre': 'Registro de prueba'})
    assert modelo.obtener_por_id(nuevo_id) is not None
```

```python
# test/backend/test_mimodulo_rutas.py
import pytest
pytestmark = [pytest.mark.api, pytest.mark.db]

def test_anonimo_redirige_al_login(client):
    resp = client.get('/mimodulo/')
    assert resp.status_code == 302
    assert '/auth/login' in resp.headers['Location']

def test_superadmin_entra(client, superadmin):
    assert client.get('/mimodulo/').status_code == 200
```

```python
# test/humo/test_mimodulo_humo.py
import pytest
pytestmark = [pytest.mark.smoke, pytest.mark.db]

def test_rutas_no_devuelven_500(client, superadmin):
    for ruta in ('/mimodulo/', '/mimodulo/crear'):
        assert client.get(ruta).status_code in (200, 302)
```

```python
# test/aceptacion/test_mimodulo_flujo_completo.py
import pytest
pytestmark = [pytest.mark.acceptance, pytest.mark.db]

def test_flujo_completo(client, superadmin):
    resp = client.post('/mimodulo/crear', data={'nombre': 'Flujo completo'})
    assert resp.status_code == 302
```

Con esto, cualquier módulo puede entrar a la misma estructura, a la misma matriz
y a las mismas evidencias que guion.
