#!/usr/bin/env python3
"""Genera subtítulos SRT y capítulos a partir de la línea de tiempo de la historia."""
from __future__ import annotations

import json
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
TIMELINE = RAIZ / "video-remotion" / "public" / "timeline.json"
SALIDA = RAIZ / "video"


def srt_time(seconds: float) -> str:
    ms = int(round(seconds * 1000))
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def main() -> int:
    datos = json.loads(TIMELINE.read_text(encoding="utf-8"))
    lineas: list[str] = []
    n = 0
    capitulos: list[str] = []
    for esc in datos["escenas"]:
        inicio = esc["inicio"]
        fin = inicio + esc["duracion"]
        capitulos.append(f"{srt_time(inicio)[:-4]} - {srt_time(fin)[:-4]}  {esc['titulo']}")
        for frase in esc.get("frases", []):
            n += 1
            lineas += [
                str(n),
                f"{srt_time(inicio + frase['inicio'])} --> {srt_time(inicio + frase['fin'])}",
                frase["texto"],
                "",
            ]
    SALIDA.mkdir(parents=True, exist_ok=True)
    srt = SALIDA / "historia.srt"
    srt.write_text("\n".join(lineas), encoding="utf-8")
    caps = SALIDA / "historia_capitulos.txt"
    caps.write_text("\n".join(capitulos) + "\n", encoding="utf-8")
    print(f"OK: {srt} ({n} subtítulos)")
    print(f"OK: {caps} ({len(capitulos)} capítulos)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
