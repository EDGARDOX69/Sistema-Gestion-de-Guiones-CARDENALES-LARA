# Informe de pruebas — Itinerario

> **Nota (2026-11-10):** documento histórico, anterior a la reorganización de la
> suite. Los conteos y las rutas `tests/` están desactualizados. La versión
> vigente es `docs/pruebas/GUIA_MAESTRA_PRUEBAS.md`.

**Proyecto:** Itinerario — gestión operativa del Estadio Antonio Herrera Gutiérrez.
**Repositorio:** https://github.com/keiverzamudia/Itinerario
**Rama de trabajo:** `pruebas` / `exposicion/curso-ci`.
**Fecha de preparación:** 2026-11-05.
**Estado:** material preparado; ejecución pendiente en macOS.

> **Aviso de honestidad:** este informe no declara resultados que no se hayan ejecutado. La
> sesión de preparación se hizo en Windows, donde el `venv` es de macOS y MySQL no estaba
> disponible. Los resultados reales se completan en la Mac siguiendo `DEMO_RUNBOOK.md` y
> `EJECUTAR_EN_MAC.md`. Las celdas "PENDIENTE" se reemplazan con la salida real.

---

## 1. Resumen ejecutivo

Itinerario cuenta con una base de pruebas automatizadas sobre Flask, PyMySQL y Playwright. La
suite backend clona dos bases de datos de prueba (`estadio_db_test`, `seguridad_test`) desde los
dumps de la raíz y cubre autenticación, permisos, validaciones, notificaciones, EN VIVO, reportes
y PDFs. La suite E2E cubre el login real en navegador, incluyendo CAPTCHA.

**Fortalezas:**

- Aislamiento de datos: los tests no tocan las bases reales.
- Cobertura de reglas críticas de auth, permisos y EN VIVO.
- E2E con evidencia (trace, video, captura).
- Emails mockeados y usuarios únicos por prueba.

**Huecos:**

- Sin medición de cobertura integrada al repositorio.
- Sin análisis estático ni de seguridad en el flujo local.
- Sin pruebas de CRUD completos, IDOR, uploads, SocketIO ni concurrencia.
- CI preparado, pendiente de ejecutar en GitHub.

**Conclusión:** la suite es una base sólida para la exposición y para empezar CI. No es todavía
una suite exhaustiva de producción; el informe debe presentar ambos lados.

---

## 2. Alcance

### Incluido

- Pruebas de autenticación y sesión.
- Pruebas de permisos por rol.
- Pruebas de validaciones de modelos.
- Pruebas de notificaciones.
- Pruebas de vistas y lógica de EN VIVO.
- Pruebas de reportes, filtros, analytics y PDFs.
- Prueba E2E de login en navegador real.

### Excluido

- Carga y estrés.
- Seguridad ofensiva (pentest).
- Pruebas de accesibilidad completas.
- Compatibilidad multi-navegador más allá de Chromium.
- Pruebas de correo real (se mockea).
- Pruebas de SocketIO en tiempo real con múltiples clientes.

---

## 3. Entorno

### 3.1 Entorno de preparación (Windows)

| Elemento | Valor |
|---|---|
| SO | Windows 10/11 |
| Python global | 3.15 (scoop) |
| `venv` del repo | creado en macOS; no utilizable en Windows |
| MySQL | XAMPP instalado; puerto 3306 cerrado |
| pytest | no instalado en el Python global |
| ffmpeg | no instalado |
| Docker / gh / act | no disponibles |
| Node / npm | 26.9 / 12.0.2 |

**Consecuencia:** no se ejecutaron pruebas reales en esta sesión. No se inventan resultados.

### 3.2 Entorno objetivo (macOS)

| Elemento | Valor esperado |
|---|---|
| SO | macOS 13+ |
| Python | 3.12 |
| Entorno | `venv` local |
| MySQL | 8.x (Homebrew o XAMPP) |
| Navegador | Chromium de Playwright |
| CI | GitHub Actions, `ubuntu-latest` |

### 3.3 Variables de entorno

```dotenv
SECRET_KEY=<clave-generada>
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=
DB_NAME_ESTADIO=estadio_db
DB_NAME_SEGURIDAD=seguridad
```

`.env` no se versiona. `.env.example` documenta las variables.

---

## 4. Estrategia

| Nivel | Herramienta | Alcance | Datos |
|---|---|---|---|
| Unitario/validación | pytest | setters, validadores, helpers | en memoria |
| Integración backend | pytest + Flask test client | rutas, modelos, permisos | `*_test` clonadas |
| PDF/reportes | pytest + reportlab | generación y contenido | `*_test` |
| E2E | Playwright + Chromium | login real | bases reales en CI/local |

**Principios:**

1. Cada prueba crea sus propios datos y usa identificadores únicos.
2. El orden de ejecución no debe importar.
3. Los emails nunca salen; se mockean.
4. El CAPTCHA no se desactiva: se lee de la sesión o del DOM.
5. Toda evidencia debe ser reproducible.

---

## 5. Inventario de suites

Conteo estático de funciones `def test_` (puede variar con parametrizaciones; el número real de
casos lo da `pytest --collect-only -q`).

| Archivo | Funciones | Qué cubre |
|---|---:|---|
| `tests/test_auth.py` | 9 | login, CAPTCHA, next seguro, reset, sesión única |
| `tests/test_permisos.py` | 4 | acceso por rol/permiso |
| `tests/test_validaciones.py` | 14 | setters y validadores |
| `tests/test_notificaciones.py` | 4 | creación, lectura, multi-asignación |
| `tests/test_envivo_vista.py` | 9 | estados, secuencia, permisos, timers |
| `tests/test_reportes_smoke.py` | 4 | humo de reportes |
| `tests/test_reportes_filtros.py` | 21 | filtros progresivos |
| `tests/test_reportes_campos.py` | 29 | campos y columnas |
| `tests/test_reportes_constructor.py` | 23 | constructor de reportes |
| `tests/test_reportes_definition.py` | 20 | definiciones |
| `tests/test_reportes_helpers.py` | 8 | helpers |
| `tests/test_reportes_pdf.py` | 5 | PDF básico |
| `tests/test_reportes_pdf_dinamico.py` | 36 | PDF dinámico |
| `tests/test_reportes_pdf_analytics_integration.py` | 19 | PDF + analytics |
| `tests/test_reportes_analytics.py` | 162 | analytics de reportes |
| `tests/test_reportes_module_analytics.py` | 72 | analytics por módulo |
| `tests/test_reportes_fase4g_integration.py` | 23 | integración fase 4G |
| `playwright/tests/test_login.py` | 8 | E2E de login (1 se salta sin `E2E_EMAIL`/`E2E_PASSWORD`) |

**Total estático:** 462 funciones backend + 8 E2E.

> El número puede cambiar si se agregan o eliminan pruebas. No usar este total como resultado de
> ejecución; usar la salida de pytest.

---

## 6. Casos críticos y criterio de aceptación

| ID | Caso | Nivel | Criterio |
|---|---|---|---|
| AUTH-01 | Login sin CAPTCHA | Integración | Rechaza y muestra CAPTCHA |
| AUTH-02 | CAPTCHA incorrecto | Integración | Rechaza |
| AUTH-03 | Credenciales inválidas | Integración | Mensaje de error |
| AUTH-04 | Login exitoso | Integración | 302 a `/dashboard` |
| AUTH-05 | `next` interno | Integración | Respeta destino |
| AUTH-06 | `next` externo | Integración | Bloquea y cae al panel |
| AUTH-07 | Usuario inactivo | Integración | Bloquea |
| AUTH-08 | Reset de contraseña | Integración | Flujo completo |
| AUTH-09 | Sesión única | Integración | Cierra la anterior |
| PERM-01 | Acceso sin permiso | Integración | 403/redirección |
| ENV-01 | Secuencia de estados | Integración | Sin saltos |
| ENV-02 | Retroceso | Integración | Reactiva estado anterior |
| ENV-03 | Un solo `en_vivo` | Integración | Invariante |
| NOT-01 | Notificación al asignar | Integración | Se crea y se emite |
| NOT-02 | Notificación al completar | Integración | Llega al creador |
| REP-01 | Reporte sin datos | Integración | No revienta |
| REP-02 | Filtros combinados | Integración | Respeta dependencias |
| REP-03 | PDF generado | Integración | Archivo válido y registrado |
| E2E-01 | Login real | E2E | Llega al dashboard (requiere `E2E_EMAIL`/`E2E_PASSWORD`) |

---

## 7. Comandos de ejecución

Ejecutar en macOS, dentro del repo y con el `venv` activo.

```bash
source venv/bin/activate

# 1. Suite completa
pytest -q

# 2. Con cobertura y XML
pytest -q \
  --cov=app \
  --cov-report=term-missing \
  --cov-report=html \
  --cov-report=xml \
  --junitxml=junit.xml

# 3. Conteo real de casos
pytest --collect-only -q | tail -n 5

# 4. E2E
cd playwright && pytest -q && cd ..

# 5. Lint
ruff check --select E9,F63,F7,F82 app tests

# 6. Seguridad (informativo)
pip-audit -r requirements.txt
bandit -r app -q

# 7. Pipeline local completo
./scripts/ci_local.sh
```

Requisito para E2E: MySQL corriendo y las bases reales importadas:

```bash
mysql -u root < estadio_db.sql
mysql -u root < seguridad.sql
```

---

## 8. Resultados de ejecución

> Resultados de la ejecución real en la Mac (2026-11-05).

### 8.1 Suite backend

| Métrica | Valor |
|---|---|
| Fecha/hora | 2026-11-05 19:17 (hora local) |
| Commit | `690076f` (rama `pruebas`, con cambios sin commitear) |
| Python | 3.15.2 (el runbook pedía 3.12; no estaba instalado y no hay Homebrew) |
| MySQL | MariaDB 10.4.28 (XAMPP, puerto 3306) |
| Casos recolectados | 652 |
| Passed | 652 |
| Failed | 0 |
| Errors | 0 |
| Skipped | 0 |
| Duración | 51,46 s |
| Código de salida | 0 |

### 8.2 Cobertura

| Métrica | Valor |
|---|---|
| Cobertura total | 52,75 % (4.992/9.463 líneas) |
| `app/controller` | 35,1 % (946/2.694) |
| `app/model` | 42,3 % (1.455/3.436) |
| `app/helpers` | 77,7 % (2.443/3.144) |
| Módulos críticos | `auth_controller` 61,8 % · `en_vivo_controller` 72,0 % · `reportes_controller` 66,4 % · `en_vivo_model` 51,8 % · `tarea_model` 53,2 % · `usuario_model` 29,3 % |
| Umbral acordado | Sin umbral formal; el baseline citado en el runbook era ~30 % y se supera |

### 8.3 E2E

| Métrica | Valor |
|---|---|
| Casos | 8 (1 skip sin credenciales) |
| Passed | 7 |
| Failed | 0 |
| Skipped | 1 |
| Duración | 7,16 s |
| Navegador | Chromium (Playwright 1.64.0) |
| Evidencia | `docs/exposicion/evidencias/e2e/playwright.log` y `playwright/reporte.html` |

### 8.4 Análisis estático y seguridad

| Herramienta | Resultado | Acción |
|---|---|---|
| `ruff` | 0 errores tras corregir 1 hallazgo F821 (`TableStyle` sin importar en `constructor_report.py`) | Corregido y verificado con `tests/test_reportes_constructor.py` (23 passed) |
| `pip-audit` | 3 vulnerabilidades en 2 paquetes: `werkzeug` 3.1.8 (PYSEC-2026-4312 → 3.1.9) y `python-socketio` 5.16.1 (PYSEC-2026-3042 → 5.16.2) | Documentado; actualización de parches pendiente de autorización |
| `bandit` | 0 altas, 16 medias, 2 bajas en 13.490 líneas (mayoría B608: SQL construido con f-strings sobre listas blancas) | Documentado; revisar caso por caso antes de convertirlo en gate |

### 8.5 Curso HTML y video

| Artefacto | Resultado |
|---|---|
| `curso/index.html` | 231 KB, 15 módulos, 30 preguntas de examen, 128 flashcards, 44 preguntas de defensa |
| Verificación en Chromium | Navegación, tema claro/oscuro, progreso persistente, autoevaluación, flashcards, modo defensa y examen funcionando |
| `video/historia.mp4` | Historia cinematográfica de 10 escenas: 7,3 min (439,9 s), 29,8 MB, 1280×720, H.264 + AAC, voz neuronal Edge (Salome), subtítulos `historia.srt` |
| `video/exposicion.mp4` | Versión larga de estudio: 26,4 min (1.584,8 s), 1280×720, H.264 + AAC + subtítulos `mov_text`, 44,9 MB |
| Capítulos y subtítulos | 10 escenas en `historia_capitulos.txt`; 12 capítulos en la versión larga (`capitulos.txt`) |
| `video/historia.html` | Reproductor de la historia: 10 escenas, 29 preguntas de repaso, notas y progreso |
| `video/index.html` | Reproductor de la versión larga: 12 capítulos, 40 preguntas, notas y progreso |
| Motor | Remotion (React) con springs, coreografía escalonada, grano y viñeta; proyecto en `video-remotion/` |
| Evidencia | `docs/exposicion/evidencias/video/ffprobe_historia.json`, `contact-sheet-historia.jpg`, `historia-player.log`, `06-historia-player.png` |

---

## 9. Defectos encontrados

| ID | Título | Severidad | Estado | Evidencia |
|---|---|---|---|---|
| DEF-01 | `TableStyle` usado sin importar en `app/helpers/generators/constructor_report.py:94` (F821 de ruff). Se dispararía al construir un reporte con tabla de cómputo | Media | Corregido | `docs/exposicion/evidencias/ci/ruff.log` |
| DEF-02 | `werkzeug` 3.1.8 y `python-socketio` 5.16.1 con vulnerabilidades conocidas | Media | Abierto | `docs/exposicion/evidencias/ci/pip-audit.log` |
| DEF-03 | 16 hallazgos medios de bandit (B608, SQL con f-strings) | Baja | Abierto (revisión) | `docs/exposicion/evidencias/ci/bandit.log` |

Plantilla para completar:

| Campo | Contenido |
|---|---|
| Título | |
| Ambiente | |
| Pasos | |
| Esperado | |
| Obtenido | |
| Severidad | |
| Prioridad | |
| Evidencia | |

---

## 10. Evidencias

Guardar en `docs/exposicion/evidencias/`:

```
evidencias/
  tests/
    pytest.log
    junit.xml
  coverage/
    html/
    coverage.xml
  e2e/
    playwright.log
    test-results/
    reporte.html
  ci/
    ruff.log
    pip-audit.log
    bandit.log
  verificacion.log
```

Checklist:

- [x] `pytest -q` verde.
- [x] `junit.xml` generado.
- [x] `htmlcov/index.html` generado.
- [x] `coverage.xml` generado.
- [x] E2E verde o con trace del fallo.
- [x] `ruff` ejecutado.
- [x] `pip-audit` ejecutado.
- [x] `bandit` ejecutado.
- [ ] Captura de GitHub Actions verde (no se hizo push).
- [ ] Captura de GitHub Actions rojo (fallo controlado; no se hizo push).

---

## 11. Riesgos y limitaciones

| Riesgo | Impacto | Mitigación |
|---|---|---|
| `venv` creado en otro SO | No ejecuta | Recrear con Python 3.12 en la Mac |
| MySQL no disponible | Bloquea tests | `brew services start mysql` o XAMPP |
| Base real usada por E2E | Datos | Importar dumps en local; no usar producción |
| Cobertura baja | Riesgo no visible | Agregar pytest-cov y priorizar módulos críticos |
| Tests acoplados a datos | Fragilidad | Builders y datos únicos |
| E2E lento | Feedback tardío | Separar PR de nightly |
| SocketIO en memoria | No escala a varios workers | Mantener `-w 1` o backend de mensajes |
| CI con `|| true` en seguridad | No bloquea | Convertir en gate cuando el ruido esté controlado |

---

## 12. Conclusiones

1. La suite backend es una base real y aislada: **652 pruebas verdes** contra `*_test`.
2. El E2E de login cubre el flujo público con evidencia: **7 passed + 1 skip** en Chromium.
3. La cobertura medida es **52,75 %**, por encima del baseline (~30 %); `controller` y `model` son las áreas con más hueco.
4. El análisis estático encontró un defecto real (DEF-01) que quedó corregido, y dos frentes abiertos (parches de dependencias y revisión de hallazgos de bandit).
5. El pipeline de CI está definido en `.github/workflows/ci.yml`, pero **no se ejecutó en GitHub** porque no se hizo push (decisión del usuario).

---

## 13. Anexo. Checklist para completar el informe

- [x] Recrear `venv` (se usó Python 3.15.2; 3.12 no estaba disponible).
- [x] Instalar `requirements.txt`, `requirements-dev.txt` y `playwright/requirements.txt`.
- [x] Configurar `.env`.
- [x] Arrancar MySQL (MariaDB de XAMPP).
- [x] Importar `estadio_db.sql` y `seguridad.sql` para E2E.
- [x] Correr `pytest -q`.
- [x] Correr cobertura y JUnit XML.
- [x] Correr E2E.
- [x] Correr `ruff`, `pip-audit`, `bandit`.
- [x] Completar tablas de la sección 8.
- [x] Guardar evidencias.
- [x] Revisar que no haya datos reales ni secretos en las capturas (revisado; los logs no contienen `.env`).
- [ ] Actualizar `CHECKLIST.md` con el resultado real (opcional, fuera de esta ejecución).
