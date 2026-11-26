# Pipeline de pruebas — Gestión de Tareas y Asignación de Tareas

Diseño de las etapas de CI del módulo de tareas. El workflow es
`.github/workflows/tareas.yml`; la única fuente de verdad de los comandos es
`scripts/ci_tareas.py`, invocado también desde `scripts/ci_tareas.sh` y
`scripts/ci_tareas.ps1`. Así local y CI ejecutan exactamente lo mismo.

## 1. Principios

1. **Nunca contra las bases reales.** Todas las etapas con MySQL usan
   `estadio_db_test` / `seguridad_test`, clonadas por los fixtures desde
   `estadio_db.sql` y `seguridad.sql`. El orquestador comprueba que MySQL
   responda antes de ejecutar y falla con un mensaje claro si no está.
2. **Datos únicos.** Las bases se clonan una sola vez por sesión de pytest, no
   se truncan entre tests. Todo nombre/cédula lleva `uuid`; las aserciones
   comparan por id, nunca por totales globales.
3. **Multi-actor con caché limpia.** El `_contexto` autouse mantiene un app
   context vivo y Flask-Login cachea `g._login_user`. Al cambiar de actor,
   `g.pop('_login_user', None)` antes y después del login.
4. **Fallo temprano.** Las etapas se ejecutan en orden; si una falla, el
   orquestador se detiene y escribe `resumen.json`. `pip-audit` y `bandit`
   son informativos; `ruff` sí bloquea (igual que en `scripts/ci_local.sh`).
5. **Sin dependencias nuevas.** Se reutilizan pytest, pytest-cov,
   pytest-playwright, ruff, pip-audit y bandit, ya presentes en
   `requirements-dev.txt` / `test/interfaz/requirements.txt`.

## 2. Mapa de etapas

| # | Etapa | Comando | Gate | MySQL | Evidencia |
|---|-------|---------|------|-------|-----------|
| 1 | `unidad` | `python scripts/ci_tareas.py --etapas unidad` | Sí | No | `tareas/unidad.log` |
| 2 | `integracion` | `... --etapas integracion` | Sí | Sí | `tareas/integracion.log` |
| 3 | `api` | `... --etapas api` | Sí | Sí | `tareas/api.log` |
| 4 | `humo` | `... --etapas humo` | Sí | Sí | `tareas/humo.log` |
| 5 | `aceptacion` | `... --etapas aceptacion` | Sí | Sí | `tareas/aceptacion.log` |
| 6 | `interfaz` | `... --etapas interfaz` | Sí | Sí | `tareas/interfaz.log` |
| 7 | `calidad` | `... --etapas calidad` | Solo ruff | No | `tareas/calidad.log` |

Ejecutar todo: `python scripts/ci_tareas.py`. En Windows:
`.\scripts\ci_tareas.ps1`; en Git Bash: `./scripts/ci_tareas.sh`.

La etapa 6 fija `E2E=1` por sí misma, porque `fixtures_e2e.servidor` se niega
a correr sin esa variable. No se reutiliza el servidor de desarrollo: el
fixture levanta el suyo en `127.0.0.1:5002` contra las BDs de prueba y falla
si el puerto ya está ocupado.

## 3. Matriz de casos por etapa

| Etapa | Caso | Qué protege | Origen |
|-------|------|-------------|--------|
| Unidad | Validaciones de `TareaModel` (nombre 3-50, instrucción 10-255) | Reglas puras sin BD | `test/unitarias/test_tarea_model_unit.py`, `test/unitarias/test_tareas_asignadas_model_unit.py`, `Pruebas por modulo/gestion_tarea/unitarias` |
| Integración | `PL-TAR-INT-01` Fallo al notificar revierte la asignación | Transacción compuesta estadio_db → seguridad | `test/integracion/test_tareas_pipeline_integridad.py` (nuevo) |
| Integración | `PL-TAR-INT-02` Usuario inactivo no recibe asignación ni notificación | `filtrar_ids_activos` | ídem (nuevo) |
| Integración | `PL-TAR-INT-03` Dedupe de multi-select + campo legacy + departamento | Una fila y una notificación por usuario | ídem (nuevo) |
| Integración | Multi-asignación, departamento, API de campana, anti-IDOR, notificación al creador | Flujo Tareas ↔ Notificaciones | `test/integracion/test_notificaciones.py` |
| Integración | Dueño vs. ajeno vs. supervisor al completar | Permisos en el flujo real | `Pruebas por modulo/gestion_tarea/integracion` |
| API | Sin sesión → 302/401; permisos → 403; entradas → 400/404 | Contrato HTTP y permisos | `test/backend/test_tareas_asignadas_backend.py` |
| API | Auto-completado sin auto-notificación; JSON vs. submit nativo | Reglas de `completar` | ídem |
| API | Contrato de `/consultar-asignaciones` y de `/notificaciones/api` | Claves y formatos | ídem + `Pruebas por modulo/notificaciones/backend` |
| Humo | `/gestion-tarea/` carga sin "Error interno" | Ruta crítica en segundos | `Pruebas por modulo/gestion_tarea/humo` |
| Aceptación | Alta → asignación → vista Mis Tareas → completado | Flujo de negocio de extremo a extremo con `test_client` | `test/aceptacion/test_tareas_asignadas.py`, `test/aceptacion/test_tarea_model.py` |
| Interfaz | Asignar desde el modal, ver seguimiento, recibir campana, completar, verificación en ambas vistas | UI real + SocketIO + persistencia | `test/interfaz/test_tareas_asignadas.py` |
| Interfaz | Modelo desde navegador y vistas por módulo | Regresión visual/funcional | `test/interfaz/test_tarea_model_interfaz.py`, carpetas `interface` por módulo |
| Calidad | `ruff --select E9,F63,F7,F82` sobre `app`, `test` y `Pruebas por modulo` | Errores sintácticos y nombres rotos | `scripts/ci_tareas.py` |
| Calidad | `pip-audit`, `bandit` | Vulnerabilidades (informativas) | ídem |

## 4. Gate de promoción

Una rama se considera lista cuando:

- Las etapas 1-6 terminan en `ok` (0 fallos, 0 errores de recolección).
- `ruff` termina sin errores E9/F63/F7/F82.
- `docs/pruebas/evidencias/tareas/resumen.json` marca `"final": "ok"`.
- No aparece ningún test que escriba en `estadio_db` o `seguridad` sin
  sufijo `_test` (ver `test/seguridad/test_aislamiento_bd.py`).

`pip-audit` y `bandit` se registran pero no bloquean: ese es el comportamiento
actual de `scripts/ci_local.sh` y cambiarlo queda fuera de este diseño.

## 5. Secuencia del flujo cubierto

```mermaid
flowchart LR
    A[Alta de tarea\nregistrar] --> B[Asignación\nmulti-select / depto]
    B --> C[Transacción única\nasignación + notificación]
    C --> D[Mis Tareas\nPendiente]
    C --> E[Campana\nnotificación]
    D --> F[Completar\nDueño o supervisor]
    F --> G[Notificación al creador\ntarea_completada]
    F --> H[Seguimiento\nCompletada]
    E --> I[/notificaciones/api\nleer / leer-todas]
```

Cada flecha tiene al menos una aserción en la matriz anterior. La flecha `C`
es la que refuerzan los tests nuevos: si el INSERT de la notificación falla,
no debe quedar la asignación a medias.

## 6. Puntos de atención

- `pytest.ini` fija `--base-url=http://127.0.0.1:5002`, opción registrada por
  `pytest-playwright`. El workflow la instala desde
  `test/interfaz/requirements.txt`; en local hay que tenerla instalada para
  cualquier etapa.
- Los dos pytest simultáneos se prohiben: el fixture de clonado hace
  `DROP DATABASE`/`CREATE DATABASE` sobre las BDs de prueba.
- No ejecutar dos sesiones del orquestador en paralelo por la misma razón.
- `scripts/ci_local.sh` y el workflow antiguo `pruebas.yml` (solo aceptación)
  siguen existiendo como pipeline general del proyecto; este pipeline es
  específico del módulo y no los reemplaza. El workflow antiguo está eliminado
  en el working tree; no se tocó ese cambio.
- Requisitos locales: MySQL encendido, `pytest-playwright` (por `--base-url`)
  y Chromium (`python -m playwright install chromium`). Para la etapa 7 se
  necesita `ruff`; `pip-audit` y `bandit` son opcionales.
- Las deudas conocidas del módulo (esquema `seguridad` escrito a mano en
  algunas consultas de `tarea_model`, presencia SocketIO en memoria) no se
  introducen en los tests nuevos: se usan los nombres de esquema de
  `DATABASE_CONFIG` y los actores se cambian limpiando la caché.

## 7. Cómo añadir un caso

1. Coloca el archivo en la carpeta del tipo correspondiente dentro de `test/`
   o `Pruebas por modulo/`; los marcadores (`unit`, `integration`, `api`,
   `smoke`, `ui`, `acceptance`, `db`) se asignan solos por carpeta.
2. Usa datos con `uuid` y limpia lo que creates si el test sale del flujo
   normal de clonado.
3. Añade la ruta del archivo a la etapa que corresponda en `ETAPAS` de
   `scripts/ci_tareas.py` y una fila en la matriz de este documento.
4. Verifica con `python scripts/ci_tareas.py --etapas <etapa>` antes de
   abrir el PR.

## 8. Verificación local

Ejecución completa del orquestador (`python scripts/ci_tareas.py`), con MySQL
y Chromium disponibles:

| Etapa | Resultado |
|-------|-----------|
| Unitarias | 42 passed |
| Integración | 8 passed |
| Backend / API | 8 passed |
| Humo | 1 passed |
| Aceptación | 4 passed |
| Interfaz / E2E | 7 passed |
| Calidad | `ruff`: All checks passed; `pip-audit`/`bandit` informativos |

`docs/pruebas/evidencias/tareas/resumen.json` terminó con `"final": "ok"` y
código de salida 0. Los logs por etapa quedaron en esa misma carpeta.

## 9. Ajustes necesarios para que el gate sea estable

Al ejecutar las etapas de forma aislada (que es como corre CI) aparecieron
tres problemas que la suite completa enmascaraba por orden de ejecución:

1. `test/backend/test_tareas_asignadas_backend.py` parcheaba `tiene_permiso`
   sobre la instancia devuelta por el fixture, pero el `user_loader` crea una
   instancia nueva en cada request. Ahora se parchea `Usuario.tiene_permiso`
   (clase) con `monkeypatch`, que se revierte automáticamente al terminar.
2. `Pruebas por modulo/gestion_tarea/interface/test_gestion_tarea_interface.py`
   buscaba el botón de editar por nombre accesible `"Editar"`, pero el botón
   solo tiene icono y su nombre computable es el glifo. Se cambió por
   `button[title="Editar"]`.
3. `app/view/gestion_tarea/dashboard.html` no tenía `novalidate` en
   `#formAsignarTarea`, así que la validación nativa del `<select required>`
   impedía mostrar el mensaje propio de "Falta el destinatario". Se añadió el
   atributo, igual que ya tenían los formularios de alta y edición.

## 10. Ejecutarlo desde la extensión de GitHub Actions

El workflow tiene `workflow_dispatch` con un parámetro `etapas` (por defecto
`todas`), requerido para poder lanzarlo a mano.

1. Haz **commit y push** del workflow a `main`. La extensión oficial de GitHub
   Actions para VS Code (`GitHub.vscode-github-actions`) trabaja contra el
   repositorio remoto: no ejecuta un YAML que solo existe en local.
2. Abre `.github/workflows/tareas.yml` en VS Code y entra en el panel
   **GitHub Actions** de la barra de actividad.
3. Sobre `Pipeline de pruebas - Gestion de Tareas`, elige **Run workflow**
   (también disponible desde `Ctrl+Shift+P` → *GitHub Actions: Run Workflow*).
4. Selecciona la rama y el valor de `etapas`: `todas` (por defecto) o una sola
   etapa (`unidad`, `integracion`, `api`, `humo`, `aceptacion`, `interfaz`,
   `calidad`). Los pasos de las otras etapas se omiten; la instalación y la
   subida de evidencias siempre corren.
5. El run se crea en github.com. Los logs se consultan en el panel de
   *Workflow Runs* de la extensión o en la pestaña **Actions** del repositorio.

Equivalentes: en la web, **Actions → Pipeline de pruebas - Gestión de Tareas →
Run workflow**; por CLI, `gh workflow run tareas.yml -f etapas=unidad`.

Si lo que quieres es ejecutarlo sin GitHub, no uses la extensión: corre
`python scripts/ci_tareas.py --etapas unidad` (o `.ps1` / `.sh`). Las
extensiones que usan `act` requieren Docker y no reproducen exactamente el
runner (MySQL como servicio e instalación de Chromium con `--with-deps`).

