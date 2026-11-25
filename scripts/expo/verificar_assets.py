#!/usr/bin/env python3
"""Verifica que el curso HTML, el video y los documentos de la exposición existan
y cumplan los mínimos. No modifica nada.

Uso: python scripts/expo/verificar_assets.py
Sale con código 1 si hay fallos.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent.parent
fallos: list[str] = []
ok: list[str] = []


def check(cond: bool, mensaje: str) -> None:
    if cond:
        ok.append(mensaje)
        print(f"[OK]   {mensaje}")
    else:
        fallos.append(mensaje)
        print(f"[FALLA] {mensaje}")


def words(path: Path) -> int:
    if not path.exists():
        return 0
    return len(re.findall(r"\S+", path.read_text(encoding="utf-8", errors="ignore")))


def ffprobe(path: Path) -> dict:
    try:
        out = subprocess.check_output([
            "ffprobe", "-v", "error", "-print_format", "json",
            "-show_format", "-show_streams", str(path),
        ], text=True)
        return json.loads(out)
    except Exception as exc:
        print(f"[AVISO] ffprobe no disponible o falló: {exc}")
        return {}


print("== Curso HTML ==")
html_candidates = [RAIZ / "curso" / "index.html", RAIZ / "curso" / "index-single.html"]
html = next((p for p in html_candidates if p.exists()), None)
check(html is not None, "curso/index.html o curso/index-single.html existe")
if html:
    texto = html.read_text(encoding="utf-8", errors="ignore")
    check(html.stat().st_size > 80_000, f"{html.name} pesa más de 80 KB ({html.stat().st_size/1024:.0f} KB)")
    check("localStorage" in texto, "el curso guarda progreso con localStorage")
    check(re.search(r"quiz|cuestionario", texto, re.I) is not None, "el curso incluye quizzes")
    check(re.search(r"examen|evaluaci", texto, re.I) is not None, "el curso incluye modo examen")
    check(re.search(r"Herramientas de ecosistema", texto, re.I) is not None,
          "el curso incluye el módulo de ecosistema")
    check(re.search(r"CI/CD|Integración Continua", texto, re.I) is not None,
          "el curso incluye el módulo de CI/CD")

print("\n== Video ==")
video = RAIZ / "video" / "exposicion.mp4"
check(video.exists(), "video/exposicion.mp4 existe")
if video.exists():
    meta = ffprobe(video)
    duracion = float(meta.get("format", {}).get("duration", 0) or 0)
    streams = meta.get("streams", [])
    check(duracion >= 1200, f"dura al menos 20 min (actual: {duracion/60:.1f} min)")
    check(any(s.get("codec_type") == "video" for s in streams), "tiene stream de video")
    check(any(s.get("codec_type") == "audio" for s in streams), "tiene stream de audio")
    check((RAIZ / "video" / "subtitulos.srt").exists(), "video/subtitulos.srt existe")
    check((RAIZ / "video" / "capitulos.txt").exists(), "video/capitulos.txt existe")
    check(video.stat().st_size < 100 * 1024 * 1024,
          f"pesa menos de 100 MB para GitHub (actual: {video.stat().st_size/1024/1024:.1f} MB)")

historia = RAIZ / "video" / "historia.mp4"
check(historia.exists(), "video/historia.mp4 existe")
if historia.exists():
    meta = ffprobe(historia)
    dur = float(meta.get("format", {}).get("duration", 0) or 0)
    streams = meta.get("streams", [])
    check(dur >= 300, f"la historia dura al menos 5 min (actual: {dur/60:.1f} min)")
    check(any(s.get("codec_type") == "video" for s in streams), "la historia tiene video")
    check(any(s.get("codec_type") == "audio" for s in streams), "la historia tiene audio")
    check((RAIZ / "video" / "historia.srt").exists(), "video/historia.srt existe")
    check((RAIZ / "video" / "historia_capitulos.txt").exists(),
          "video/historia_capitulos.txt existe")

print("\n== Documentos ==")
docs = {
    "docs/exposicion/GUION_EXPOSICION.md": 1200,
    "docs/exposicion/EVALUACION_SECCION.md": 1000,
    "docs/exposicion/PREGUNTAS_DEFENSA.md": 1000,
    "docs/exposicion/DEMO_RUNBOOK.md": 500,
    "docs/exposicion/INFORME_PRUEBAS.md": 300,
}
for rel, minimo in docs.items():
    p = RAIZ / rel
    check(p.exists(), f"{rel} existe")
    if p.exists():
        n = words(p)
        check(n >= minimo, f"{rel} tiene al menos {minimo} palabras (actual: {n})")

print("\n== CI y pruebas ==")
check((RAIZ / "pytest.ini").exists(), "pytest.ini existe")
check((RAIZ / "requirements-dev.txt").exists(), "requirements-dev.txt existe")
check((RAIZ / ".github" / "workflows" / "ci.yml").exists(), ".github/workflows/ci.yml existe")
ci = RAIZ / ".github" / "workflows" / "ci.yml"
if ci.exists():
    texto = ci.read_text(encoding="utf-8", errors="ignore")
    check("pytest" in texto, "el workflow ejecuta pytest")
    check("mysql" in texto.lower(), "el workflow usa MySQL")
    check("upload-artifact" in texto, "el workflow sube artefactos")

print("\n== Resumen ==")
print(f"OK: {len(ok)}  FALLOS: {len(fallos)}")
if fallos:
    print("\nPendientes:")
    for f in fallos:
        print(f" - {f}")
    sys.exit(1)
print("Todo verificado.")
