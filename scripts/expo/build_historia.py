#!/usr/bin/env python3
"""Genera la voz y la línea de tiempo para el video-historia (Remotion)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
import video_pipeline as vp  # noqa: E402

FUENTE = RAIZ / "docs" / "exposicion" / "fuente" / "historia.json"
SALIDA = RAIZ / "video-remotion" / "public"
FPS = 30


def main() -> int:
    datos = json.loads(FUENTE.read_text(encoding="utf-8"))
    audio_dir = SALIDA / "audio"
    audio_dir.mkdir(parents=True, exist_ok=True)

    escenas = []
    cursor = 0.0
    for esc in datos["escenas"]:
        wav = audio_dir / f"{esc['id']}.wav"
        dur = vp.make_audio(esc["narracion"], wav, datos.get("voz", "Paulina"), "edge")
        total = dur + 0.6
        frases = []
        oraciones = vp.split_sentences(esc["narracion"])
        chars = sum(len(s) for s in oraciones) or 1
        t = 0.15
        for s in oraciones:
            share = len(s) / chars * dur
            frases.append({"texto": s, "inicio": round(t, 3), "fin": round(t + share, 3)})
            t += share
        escenas.append({
            "id": esc["id"],
            "titulo": esc["titulo"],
            "visual": esc["visual"],
            "audio": f"audio/{esc['id']}.wav",
            "duracion": round(total, 3),
            "inicio": round(cursor, 3),
            "frames": int(round(total * FPS)),
            "frases": frases,
        })
        cursor += total
        print(f"{esc['id']}: {total:5.1f}s  {esc['titulo']}")

    timeline = {
        "titulo": datos["titulo"],
        "subtitulo": datos.get("subtitulo", ""),
        "fps": FPS,
        "width": 1280,
        "height": 720,
        "duracion": round(cursor, 3),
        "escenas": escenas,
    }
    destino = SALIDA / "timeline.json"
    destino.write_text(json.dumps(timeline, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"\nOK: {destino}")
    print(f"Duración total: {cursor/60:.1f} min")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
