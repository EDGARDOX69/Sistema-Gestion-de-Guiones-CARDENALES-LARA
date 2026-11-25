#!/usr/bin/env python3
"""Genera un video MP4 narrado a partir de un guion JSON.

Entrada (docs/exposicion/fuente/video.json):
{
  "titulo": "...",
  "voz": "Paulina",
  "capitulos": [
    {"id": "01", "titulo": "Introduccion",
     "slides": [{"titulo": "...", "bullets": ["..."],
                 "narracion": "...", "diagrama": "pipeline"}]}
  ]
}

Requisitos:
  - Python 3.10+
  - Pillow: pip install pillow
  - ffmpeg en PATH
  - macOS: comando `say` (voz offline). Alternativa: pip install edge-tts

Uso:
  python scripts/expo/video_pipeline.py \
    --guion docs/exposicion/fuente/video.json \
    --salida video --voz Paulina
"""
from __future__ import annotations

import argparse
import asyncio
import json
import math
import os
import re
import shutil
import subprocess
import sys
from functools import lru_cache
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W, H = 1280, 720
BG = (10, 14, 20)
BG_2 = (17, 24, 33)
PANEL = (23, 31, 43)
ACCENT = (56, 189, 248)
ACCENT_2 = (245, 158, 11)
TEXT = (240, 244, 248)
MUTED = (139, 152, 170)
GREEN = (52, 211, 153)
RED = (248, 113, 113)

FONT_CANDIDATES: dict[str, list[tuple[str, int]]] = {
    "regular": [
        ("/System/Library/Fonts/HelveticaNeue.ttc", 0),
        ("/System/Library/Fonts/Supplemental/Arial.ttf", 0),
        ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 0),
        ("C:/Windows/Fonts/arial.ttf", 0),
    ],
    "bold": [
        ("/System/Library/Fonts/HelveticaNeue.ttc", 1),
        ("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 0),
        ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 0),
        ("C:/Windows/Fonts/arialbd.ttf", 0),
    ],
    "display": [
        ("/System/Library/Fonts/Supplemental/DIN Alternate Bold.ttf", 0),
        ("/System/Library/Fonts/HelveticaNeue.ttc", 1),
        ("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 0),
    ],
    "medium": [
        ("/System/Library/Fonts/Avenir Next.ttc", 5),
        ("/System/Library/Fonts/HelveticaNeue.ttc", 0),
        ("/System/Library/Fonts/Supplemental/Arial.ttf", 0),
    ],
    "mono": [
        ("/System/Library/Fonts/Menlo.ttc", 0),
        ("/System/Library/Fonts/Supplemental/Courier New.ttf", 0),
        ("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 0),
    ],
}


def eprint(*args: object) -> None:
    print(*args, file=sys.stderr)


@lru_cache(maxsize=256)
def font(size: int, kind: str = "regular") -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for path, index in FONT_CANDIDATES.get(kind, FONT_CANDIDATES["regular"]):
        if not os.path.exists(path):
            continue
        try:
            return ImageFont.truetype(path, size, index=index)
        except (OSError, ValueError):
            continue
    return ImageFont.load_default()


def mix(c1: tuple[int, int, int], c2: tuple[int, int, int], t: float) -> tuple[int, int, int]:
    """Interpola dos colores. t=0 → c1, t=1 → c2."""
    t = max(0.0, min(1.0, t))
    return tuple(int(round(a + (b - a) * t)) for a, b in zip(c1, c2))  # type: ignore[return-value]


def wrap_text(draw: ImageDraw.ImageDraw, text: str, fnt, max_width: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if draw.textlength(candidate, font=fnt) <= max_width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def rounded(draw: ImageDraw.ImageDraw, box, radius: int, fill, outline=None, width: int = 1) -> None:
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def _clamp01(x: float) -> float:
    return 0.0 if x < 0.0 else 1.0 if x > 1.0 else x


def _ease_out(p: float) -> float:
    p = _clamp01(p)
    return 1.0 - (1.0 - p) ** 3


def _ease_in_out(p: float) -> float:
    p = _clamp01(p)
    return p * p * (3.0 - 2.0 * p)


def _arrow(draw: ImageDraw.ImageDraw, x1: float, y1: float, x2: float, y2: float,
           color: tuple[int, int, int], width: int = 2) -> None:
    draw.line((x1, y1, x2, y2), fill=color, width=width)
    draw.polygon([(x2, y2), (x2 - 7, y2 - 4), (x2 - 7, y2 + 4)], fill=color)


def _check_icon(draw: ImageDraw.ImageDraw, cx: float, cy: float, color: tuple[int, int, int],
                size: int = 10) -> None:
    draw.line((cx - size * 0.7, cy, cx - size * 0.15, cy + size * 0.55), fill=color, width=3)
    draw.line((cx - size * 0.15, cy + size * 0.55, cx + size * 0.8, cy - size * 0.6), fill=color, width=3)


def _node(draw: ImageDraw.ImageDraw, box: tuple[float, float, float, float], label: str,
          ratio: float, accent: tuple[int, int, int] = ACCENT) -> None:
    ratio = _clamp01(ratio)
    fill = mix(BG_2, accent, 0.10 * ratio)
    outline = mix(mix(BG_2, MUTED, 0.28), accent, ratio)
    rounded(draw, box, 10, fill, outline, 1)
    fnt = font(15, "bold")
    tw = draw.textlength(label, font=fnt)
    draw.text(((box[0] + box[2]) / 2 - tw / 2, (box[1] + box[3]) / 2 - 9), label,
              font=fnt, fill=mix(MUTED, TEXT, ratio))


def draw_diagram(draw: ImageDraw.ImageDraw, kind: str, box: tuple[int, int, int, int],
                 stage: float = 99.0, p: float = 1.0, t: float = 0.0) -> None:
    x0, y0, x1, y1 = box
    cw, ch = x1 - x0, y1 - y0
    rounded(draw, box, 18, BG_2, mix(BG_2, MUTED, 0.22), 1)
    draw.text((x0 + 24, y0 + 18), "ESQUEMA", font=font(10, "display"), fill=MUTED)
    kind = (kind or "").lower()
    if kind in ("", "none"):
        return

    if kind in ("pipeline", "ci"):
        labels = ["Plan", "Diseño", "Ejecutar", "CI", "CD"] if kind == "pipeline" \
            else ["Push", "PR", "Checks", "Merge"]
        n = len(labels)
        gap = 14
        nw = (cw - 48 - gap * (n - 1)) / n
        nh = 62
        ny = y0 + ch / 2 - nh / 2 + 8
        for i, label in enumerate(labels):
            bx = x0 + 24 + i * (nw + gap)
            r = _clamp01(stage - i)
            _node(draw, (bx, ny, bx + nw, ny + nh), label, r)
            if i < n - 1:
                r2 = _clamp01(stage - (i + 1))
                _arrow(draw, bx + nw + 2, ny + nh / 2, bx + nw + gap - 3, ny + nh / 2,
                       mix(mix(BG_2, MUTED, 0.28), ACCENT, r2), 1)
        active_w = max(8.0, (cw - 48) * _clamp01(stage / n))
        dot_x = x0 + 24 + ((t * 110) % active_w)
        draw.ellipse((dot_x - 4, ny + nh / 2 - 4, dot_x + 4, ny + nh / 2 + 4), fill=ACCENT)
        return

    if kind == "pyramid":
        cx = (x0 + x1) / 2
        layers = [("E2E", 0.42), ("Integración", 0.68), ("Unitarias", 0.94)]
        top0 = y0 + (ch - 3 * 54) / 2 + 8
        for i, (label, width_ratio) in enumerate(layers):
            r = _clamp01(stage - (2 - i))
            w = cw * width_ratio
            top = top0 + 54 * i
            bx = cx - w / 2
            rounded(draw, (bx, top, bx + w, top + 46), 8,
                    mix(PANEL, ACCENT, 0.10 * r), mix(mix(BG_2, MUTED, 0.25), ACCENT, r), 1)
            fnt = font(16, "bold")
            tw = draw.textlength(label, font=fnt)
            draw.text((cx - tw / 2, top + 13), label, font=fnt, fill=mix(MUTED, TEXT, r))
        return

    if kind == "taxonomy":
        items = ["Runner y ejecución", "Datos y aislamiento", "Análisis estático",
                 "Cobertura", "Seguridad", "Reporte y orquestación"]
        row_h = (ch - 58) / len(items)
        for i, item in enumerate(items):
            r = _clamp01(stage - i)
            ry = y0 + 44 + i * row_h
            draw.line((x0 + 24, ry + row_h, x1 - 24, ry + row_h), fill=mix(BG_2, MUTED, 0.14), width=1)
            draw.ellipse((x0 + 24, ry + row_h / 2 - 4, x0 + 32, ry + row_h / 2 + 4),
                         fill=mix(mix(BG_2, MUTED, 0.35), ACCENT, r))
            draw.text((x0 + 44, ry + row_h / 2 - 10), item, font=font(15, "bold"),
                      fill=mix(MUTED, TEXT, r))
        return

    if kind == "gates":
        labels = [("Lint", "errores reales"), ("Tests", "652 pruebas"), ("E2E", "navegador real")]
        row_h = (ch - 58) / len(labels)
        for i, (label, sub) in enumerate(labels):
            r = _clamp01(stage - i)
            ry = y0 + 44 + i * row_h
            draw.line((x0 + 24, ry + row_h, x1 - 24, ry + row_h), fill=mix(BG_2, MUTED, 0.14), width=1)
            draw.ellipse((x0 + 26, ry + row_h / 2 - 13, x0 + 52, ry + row_h / 2 + 13),
                         outline=mix(mix(BG_2, MUTED, 0.3), GREEN, r), width=1)
            if r > 0.55:
                _check_icon(draw, x0 + 39, ry + row_h / 2, GREEN, 9)
            draw.text((x0 + 68, ry + row_h / 2 - 17), label, font=font(17, "bold"),
                      fill=mix(MUTED, TEXT, r))
            draw.text((x0 + 68, ry + row_h / 2 + 4), sub, font=font(12, "medium"), fill=MUTED)
        return

    if kind == "deploy":
        items = [("Blue-green", "dos entornos y cambio de tráfico"),
                 ("Canary", "porcentaje pequeño con métricas"),
                 ("Rolling", "reemplazo gradual sin downtime")]
        row_h = (ch - 58) / len(items)
        for i, (label, sub) in enumerate(items):
            r = _clamp01(stage - i)
            ry = y0 + 44 + i * row_h
            draw.line((x0 + 24, ry + row_h, x1 - 24, ry + row_h), fill=mix(BG_2, MUTED, 0.14), width=1)
            draw.rectangle((x0 + 24, ry + 12, x0 + 28, ry + row_h - 10),
                           fill=mix(mix(BG_2, MUTED, 0.3), ACCENT, r))
            draw.text((x0 + 44, ry + row_h / 2 - 18), label, font=font(17, "bold"),
                      fill=mix(MUTED, TEXT, r))
            draw.text((x0 + 44, ry + row_h / 2 + 4), sub, font=font(12, "medium"), fill=MUTED)
        return

    if kind == "metrics":
        q = _ease_out(p)
        stats = [(f"{int(652 * q)}", "pruebas backend", "0 fallos", GREEN),
                 (f"{52.75 * q:.2f}".replace(".", ",") + " %", "cobertura de líneas",
                  "4.992 de 9.463", ACCENT),
                 ("7 + 1" if q > 0.55 else f"{int(8 * q)}", "E2E en Chromium",
                  "1 omitida sin credenciales", ACCENT)]
        row_h = (ch - 74) / 3
        for i, (value, label, sub, color) in enumerate(stats):
            ry = y0 + 38 + i * row_h
            draw.line((x0 + 24, ry + row_h - 6, x1 - 24, ry + row_h - 6),
                      fill=mix(BG_2, MUTED, 0.14), width=1)
            draw.text((x0 + 24, ry + 10), value, font=font(38, "display"),
                      fill=mix(MUTED, color, min(1.0, q * 1.5)))
            if q > 0.3:
                a = _clamp01((q - 0.3) / 0.4)
                draw.text((x0 + 190, ry + 14), label, font=font(15, "bold"),
                          fill=mix(BG_2, TEXT, a))
                draw.text((x0 + 190, ry + 38), sub, font=font(12, "medium"),
                          fill=mix(BG_2, MUTED, a))
        bar_y = y1 - 30
        draw.rectangle((x0 + 24, bar_y, x1 - 24, bar_y + 5), fill=PANEL)
        draw.rectangle((x0 + 24, bar_y, x0 + 24 + (cw - 48) * 0.5275 * q, bar_y + 5), fill=ACCENT)
        draw.text((x0 + 24, bar_y + 12), "medido el 2026-11-05 / MariaDB 10.4 / Python 3.15.2",
                  font=font(10, "medium"), fill=MUTED)
        return

    if kind == "terminal":
        tx0, ty0, tx1, ty1 = x0 + 24, y0 + 44, x1 - 24, y1 - 24
        rounded(draw, (tx0, ty0, tx1, ty1), 10, (12, 16, 22), mix(BG_2, MUTED, 0.25), 1)
        draw.rounded_rectangle((tx0, ty0, tx1, ty0 + 30), 10, fill=PANEL)
        for j, color in enumerate([(248, 113, 113), (245, 158, 11), (52, 211, 153)]):
            draw.ellipse((tx0 + 14 + j * 18, ty0 + 11, tx0 + 22 + j * 18, ty0 + 19), fill=color)
        mono = font(14, "mono")
        lines = [
            ("$ pytest -q", TEXT),
            ("................................................  100%", MUTED),
            ("652 passed in 51.46s", GREEN),
            ("0 failed, 0 errors", MUTED),
            ("", MUTED),
            ("$ cd playwright && pytest -q", TEXT),
            ("7 passed, 1 skipped in 7.16s", GREEN),
        ]
        total_chars = sum(len(x) for x, _ in lines) or 1
        reveal = int(total_chars * _ease_in_out(p))
        used = 0
        ly = ty0 + 44
        cursor_x, cursor_y = tx0 + 18, ly
        for text, color in lines:
            if used >= reveal:
                break
            take = min(len(text), reveal - used)
            draw.text((tx0 + 18, ly), text[:take], font=mono, fill=color)
            used += len(text)
            cursor_x = tx0 + 20 + draw.textlength(text[:take], font=mono)
            cursor_y = ly
            ly += 25
        if int(t * 2) % 2 == 0:
            draw.rectangle((cursor_x, cursor_y, cursor_x + 7, cursor_y + 15), fill=ACCENT)
        return


_BG_CACHE: dict[int, Image.Image] = {}


def background(chapter_idx: int, ghost: bool = True) -> Image.Image:
    """Fondo editorial: gradiente, una luz de profundidad y retícula fina."""
    key = (chapter_idx, ghost)
    if key in _BG_CACHE:
        return _BG_CACHE[key].copy()

    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)
    for y in range(H):
        draw.line((0, y, W, y), fill=mix(BG, BG_2, y / (H - 1)))

    wash = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    wd = ImageDraw.Draw(wash)
    for i in range(40, 0, -1):
        t = i / 40
        rr = int(560 * t)
        wd.ellipse((W - rr, -rr, W + rr, rr), fill=ACCENT + (int(26 * (1 - t) ** 2),))
    img = Image.alpha_composite(img.convert("RGBA"), wash).convert("RGB")
    draw = ImageDraw.Draw(img)

    for x in range(0, W, 64):
        draw.line((x, 0, x, H), fill=mix(BG_2, MUTED, 0.05), width=1)
    for y in range(0, H, 64):
        draw.line((0, y, W, y), fill=mix(BG_2, MUTED, 0.05), width=1)

    if ghost:
        fnt = font(240, "display")
        txt = f"{chapter_idx:02d}"
        tw = draw.textlength(txt, font=fnt)
        draw.text((W - 44 - tw, H - 300), txt, font=fnt, fill=mix(BG_2, MUTED, 0.06))

    _BG_CACHE[key] = img
    return img.copy()


def _layout_words(draw: ImageDraw.ImageDraw, text: str, fnt, max_width: int,
                  x0: int, y0: int, line_h: int) -> list[tuple[str, float, float]]:
    words = (text or "").split()
    lines: list[list[str]] = []
    current: list[str] = []
    width = 0.0
    for word in words:
        w = draw.textlength(word + " ", font=fnt)
        if current and width + w > max_width:
            lines.append(current)
            current, width = [], 0.0
        current.append(word)
        width += w
    if current:
        lines.append(current)
    out: list[tuple[str, float, float]] = []
    y = y0
    for line in lines:
        x = x0
        for word in line:
            out.append((word, x, y))
            x += draw.textlength(word + " ", font=fnt)
        y += line_h
    return out


def prepare_slide(slide: dict, chapter_title: str, idx: int, total: int,
                  chapter_idx: int, duration: float, cues: list[float]) -> dict:
    dummy = Image.new("RGB", (W, H))
    draw = ImageDraw.Draw(dummy)
    diagram = slide.get("diagrama")
    f_title = font(48, "bold")
    title_words = _layout_words(draw, slide.get("titulo", ""), f_title,
                                690 if diagram else 1130, 48, 102, 56)
    f_bullet = font(23)
    max_width = 660 if diagram else 1120
    bullets = slide.get("bullets") or []
    bullet_lines = [wrap_text(draw, b, f_bullet, max_width - 70) for b in bullets]

    title_lineas = len({round(w[2]) for w in title_words}) or 1
    alturas = [len(lines) * 31 + 22 for lines in bullet_lines]
    arriba = max(102 + 56 * title_lineas + 40, 196)
    abajo = H - 104
    hueco = 0.0
    if len(alturas) > 1:
        hueco = (abajo - arriba - sum(alturas)) / (len(alturas) - 1)
        hueco = max(10.0, min(36.0, hueco))
    posiciones = []
    y = arriba
    for h in alturas:
        posiciones.append(y)
        y += h + hueco

    return {
        "slide": slide, "chapter_title": chapter_title, "idx": idx, "total": total,
        "chapter_idx": chapter_idx, "duration": duration, "cues": cues,
        "diagram": diagram, "title_words": title_words, "bullet_lines": bullet_lines,
        "bullets": bullets, "max_width": max_width, "bullet_positions": posiciones,
        "title_lineas": title_lineas,
    }


def draw_slide_frame(prep: dict, t: float) -> Image.Image:
    img = background(prep["chapter_idx"])
    draw = ImageDraw.Draw(img)
    duration = prep["duration"]
    idx, total = prep["idx"], prep["total"]

    progress = (idx - 1 + _clamp01(t / duration)) / total
    draw.rectangle((0, 0, W, 3), fill=mix(BG_2, MUTED, 0.16))
    draw.rectangle((0, 0, int(W * progress), 3), fill=ACCENT)

    f_kicker = font(11, "display")
    f_chapter = font(12, "medium")
    kicker = f"CAPÍTULO {prep['chapter_idx']:02d}"
    kp = _clamp01(t / 0.4)
    draw.text((48, 34), kicker, font=f_kicker, fill=mix(BG_2, ACCENT, kp))
    kx = 48 + draw.textlength(kicker, font=f_kicker) + 12
    draw.text((kx, 33), "·", font=f_chapter, fill=mix(BG_2, MUTED, kp))
    draw.text((kx + 12, 32), prep["chapter_title"].upper(), font=f_chapter,
              fill=mix(BG_2, MUTED, kp))
    f_count = font(14, "display")
    count = f"{idx:02d} / {total:02d}"
    draw.text((W - 48 - draw.textlength(count, font=f_count), 34), count,
              font=f_count, fill=mix(BG_2, MUTED, kp))
    draw.line((48, 66, W - 48, 66), fill=mix(BG_2, MUTED, 0.20 * kp), width=1)

    f_title = font(48, "bold")
    for i, (word, x, y) in enumerate(prep["title_words"]):
        p = _ease_out((t - 0.10 - i * 0.055) / 0.45)
        if p <= 0:
            continue
        draw.text((x, y + (1 - p) * 18), word, font=f_title, fill=mix(BG_2, TEXT, p))

    underline = _ease_out((t - 0.55) / 0.45)
    if underline > 0:
        uy = 102 + 56 * prep["title_lineas"] + 10
        draw.rectangle((48, uy, 48 + 64 * underline, uy + 4), fill=ACCENT)

    f_bullet = font(23)
    f_index = font(15, "display")
    cues = prep["cues"]
    visible_ratio = 0.0
    for i, lines in enumerate(prep["bullet_lines"]):
        cue = cues[i] if i < len(cues) else 0.4
        p = _ease_out((t - cue) / 0.45)
        if p <= 0:
            continue
        by = prep["bullet_positions"][i]
        row_h = len(lines) * 31 + 22
        visible_ratio += p
        draw.line((48, by + row_h, 48 + prep["max_width"], by + row_h),
                  fill=mix(BG_2, MUTED, 0.16 * p), width=1)
        draw.text((48, by + 4), f"{i + 1:02d}", font=f_index,
                  fill=mix(BG_2, ACCENT, p))
        ty = by + (1 - p) * 16
        for line in lines:
            draw.text((94, ty), line, font=f_bullet, fill=mix(BG_2, TEXT, p))
            ty += 31

    if prep["diagram"]:
        n_elements = 6 if prep["diagram"].lower() in ("taxonomy",) else \
            5 if prep["diagram"].lower() == "pipeline" else \
            4 if prep["diagram"].lower() == "ci" else \
            3 if prep["diagram"].lower() in ("pyramid", "gates", "deploy", "metrics") else 1
        if cues:
            stage = visible_ratio * n_elements / max(1, len(cues))
        else:
            stage = n_elements * _ease_in_out((t - 0.4) / max(1.0, duration - 1.0))
        gp = _clamp01((t - 0.5) / 1.6)
        draw_diagram(draw, prep["diagram"], (748, 182, 1216, 556), stage, gp, t)

    draw.line((48, H - 46, W - 48, H - 46), fill=mix(BG_2, MUTED, 0.16 * kp), width=1)
    f_footer = font(10, "display")
    draw.text((48, H - 32), "ITINERARIO / GESTIÓN DE PRUEBAS Y CI/CD",
              font=f_footer, fill=mix(BG_2, MUTED, kp))
    right = "GUÍA DE ESTUDIO / 2026"
    draw.text((W - 48 - draw.textlength(right, font=f_footer), H - 32), right,
              font=f_footer, fill=mix(BG_2, MUTED, kp))
    return img


def draw_title_frame(t: float, duration: float, titulo: str) -> Image.Image:
    img = background(0, ghost=False)
    draw = ImageDraw.Draw(img)
    draw.rectangle((0, 0, 120 * _ease_out(t / 0.6), 4), fill=ACCENT)
    kp = _clamp01((t - 0.1) / 0.4)
    draw.text((48, 150), "GUÍA DE ESTUDIO / ITINERARIO",
              font=font(12, "display"), fill=mix(BG, ACCENT, kp))
    fnt = font(64, "bold")
    for i, (word, x, y) in enumerate(_layout_words(draw, titulo, fnt, 1020, 48, 196, 72)):
        p = _ease_out((t - 0.2 - i * 0.07) / 0.5)
        if p > 0:
            draw.text((x, y + (1 - p) * 22), word, font=fnt, fill=mix(BG, TEXT, p))
    up = _ease_out((t - 0.8) / 0.5)
    draw.rectangle((48, 196 + 72 * 2 + 18, 48 + 112 * up, 196 + 72 * 2 + 22), fill=ACCENT)
    sp = _clamp01((t - 1.0) / 0.5)
    draw.text((48, 196 + 72 * 2 + 42), "Pruebas, herramientas de ecosistema e integración continua",
              font=font(20, "medium"), fill=mix(BG, MUTED, sp))
    draw.text((48, H - 60), "ESTADIO ANTONIO HERRERA GUTIÉRREZ / 2026",
              font=font(11, "display"), fill=mix(BG, MUTED, sp))
    return img


def draw_end_frame(t: float, duration: float) -> Image.Image:
    img = background(0, ghost=False)
    draw = ImageDraw.Draw(img)
    draw.rectangle((0, 0, 120 * _ease_out(t / 0.6), 4), fill=ACCENT)
    fnt = font(72, "bold")
    p = _ease_out((t - 0.15) / 0.6)
    draw.text((48, 230 + (1 - p) * 24), "Gracias", font=fnt, fill=mix(BG, TEXT, p))
    up = _ease_out((t - 0.6) / 0.5)
    draw.rectangle((48, 340, 48 + 120 * up, 344), fill=ACCENT)
    sp = _clamp01((t - 0.8) / 0.5)
    draw.text((48, 372), "La calidad se demuestra con evidencia, no con opinión.",
              font=font(24, "medium"), fill=mix(BG, MUTED, sp))
    draw.text((48, H - 60), "ITINERARIO / GESTIÓN DE PRUEBAS Y CI/CD",
              font=font(11, "display"), fill=mix(BG, MUTED, sp))
    return img


def draw_chapter_frame(t: float, duration: float, idx: int, total: int, titulo: str) -> Image.Image:
    img = background(idx, ghost=False)
    draw = ImageDraw.Draw(img)
    draw.rectangle((0, 0, 120 * _ease_out(t / 0.5), 4), fill=ACCENT)
    kp = _clamp01((t - 0.05) / 0.4)
    draw.text((48, 130), f"CAPÍTULO {idx:02d} / {total:02d}",
              font=font(12, "display"), fill=mix(BG, ACCENT, kp))
    np_ = _ease_out((t - 0.05) / 0.5)
    draw.text((40 - (1 - np_) * 40, 150), f"{idx:02d}", font=font(190, "display"),
              fill=mix(BG, ACCENT, np_))
    fnt = font(52, "bold")
    for i, (word, x, y) in enumerate(_layout_words(draw, titulo, fnt, 820, 48, 388, 60)):
        p = _ease_out((t - 0.3 - i * 0.07) / 0.5)
        if p > 0:
            draw.text((x, y + (1 - p) * 18), word, font=fnt, fill=mix(BG, TEXT, p))
    up = _ease_out((t - 0.7) / 0.4)
    draw.rectangle((48, 388 + 60 * 2 + 14, 48 + 100 * up, 388 + 60 * 2 + 18), fill=ACCENT)
    return img

def run(cmd: list[str], **kwargs) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, check=True, **kwargs)


def probe_duration(path: Path) -> float:
    out = subprocess.check_output([
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=nw=1:nk=1", str(path),
    ], text=True).strip()
    try:
        return float(out)
    except ValueError:
        return 0.0


def convert_to_wav(src: Path, dst: Path) -> None:
    run(["ffmpeg", "-y", "-i", str(src), "-ar", "44100", "-ac", "2", "-c:a", "pcm_s16le", str(dst)],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def tts_say(text: str, out_wav: Path, voice: str) -> bool:
    if shutil.which("say") is None:
        return False
    aiff = out_wav.with_suffix(".aiff")
    candidates = [voice, "Paulina", "Monica", "Mónica", "Jorge", ""]
    for candidate in candidates:
        cmd = ["say", "-r", "150", "-o", str(aiff)]
        if candidate:
            cmd += ["-v", candidate]
        cmd += [text]
        try:
            run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if aiff.exists() and aiff.stat().st_size > 1000:
                convert_to_wav(aiff, out_wav)
                aiff.unlink(missing_ok=True)
                return True
        except Exception:
            continue
    return False


def tts_edge(text: str, out_wav: Path, voice: str) -> bool:
    try:
        import edge_tts
    except ImportError:
        return False
    mp3 = out_wav.with_suffix(".mp3")
    edge_voice = voice if voice.startswith("es-") else "es-CO-SalomeNeural"
    try:
        async def _run() -> None:
            await edge_tts.Communicate(text, edge_voice, rate="-8%").save(str(mp3))
        asyncio.run(_run())
        if mp3.exists() and mp3.stat().st_size > 1000:
            convert_to_wav(mp3, out_wav)
            mp3.unlink(missing_ok=True)
            return True
    except Exception as exc:
        eprint(f"  edge-tts fallo: {exc}")
    return False


def tts_pyttsx3(text: str, out_wav: Path) -> bool:
    try:
        import pyttsx3
    except ImportError:
        return False
    try:
        engine = pyttsx3.init()
        engine.setProperty("rate", 150)
        for v in engine.getProperty("voices"):
            if "spanish" in (v.name or "").lower() or "es_" in (v.id or "").lower():
                engine.setProperty("voice", v.id)
                break
        engine.save_to_file(text, str(out_wav))
        engine.runAndWait()
        return out_wav.exists() and out_wav.stat().st_size > 1000
    except Exception as exc:
        eprint(f"  pyttsx3 fallo: {exc}")
        return False


def make_audio(text: str, out_wav: Path, voice: str, motor: str) -> float:
    out_wav.parent.mkdir(parents=True, exist_ok=True)
    text = (text or "").strip()
    if not text:
        run(["ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo",
             "-t", "1.2", "-c:a", "pcm_s16le", str(out_wav)],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return probe_duration(out_wav)

    ok = False
    if motor in ("auto", "say"):
        ok = tts_say(text, out_wav, voice)
    if not ok and motor in ("auto", "edge"):
        ok = tts_edge(text, out_wav, voice)
    if not ok and motor in ("auto", "pyttsx3"):
        ok = tts_pyttsx3(text, out_wav)
    if not ok:
        eprint("  AVISO: no se pudo generar voz; se usa silencio de 1.2 s.")
        run(["ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo",
             "-t", "1.2", "-c:a", "pcm_s16le", str(out_wav)],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return probe_duration(out_wav)


def make_silence(path: Path, duration: float) -> float:
    path.parent.mkdir(parents=True, exist_ok=True)
    run(["ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo",
         "-t", f"{duration:.3f}", "-c:a", "pcm_s16le", str(path)],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return duration


def encode_segment(render_frame, audio: Path, out: Path, duration: float, fps: int = 30) -> None:
    """Renderiza la animación fotograma a fotograma y la codifica con el audio."""
    out.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "ffmpeg", "-y",
        "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(fps),
        "-i", "-", "-i", str(audio), "-t", f"{duration:.3f}",
        "-vf", "format=yuv420p",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "21",
        "-c:a", "aac", "-b:a", "192k",
        "-af", "apad=pad_dur=1.0,aresample=44100",
        "-shortest", str(out),
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE,
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    assert proc.stdin is not None
    try:
        for i in range(int(round(duration * fps))):
            frame = render_frame(i / fps)
            proc.stdin.write(frame.tobytes())
    finally:
        try:
            proc.stdin.close()
        except BrokenPipeError:
            pass
        proc.wait()
    if proc.returncode != 0:
        raise RuntimeError(f"ffmpeg falló al codificar {out}")


def compute_cues(narracion: str, duration: float, k: int) -> list[float]:
    """Cadencia de revelado: primera idea pronto y luego cada 4-10 s.

    Si una frase de la narración termina cerca del punto previsto, el revelado se
    ancla a esa frase; si no, se mantiene la cadencia regular.
    """
    if k <= 0:
        return []
    first = min(2.2, max(0.5, duration * 0.12))
    end = max(first + 1.0, duration - 1.2)
    if k == 1:
        cues = [first]
    else:
        step = min(10.0, max(3.5, (end - first) / k))
        cues = [first + step * i for i in range(k)]

    sentences = split_sentences(narracion)
    if sentences:
        bounds: list[float] = []
        acc = 0
        for s in sentences:
            acc += len(s)
            bounds.append(acc)
        total = acc or 1
        bt = [0.35 + (duration - 1.2) * (b / total) for b in bounds]
        snapped = []
        for cue in cues:
            near = min(bt, key=lambda x: abs(x - cue))
            snapped.append(near if abs(near - cue) <= 1.5 else cue)
        cues = snapped

    for i in range(1, len(cues)):
        cues[i] = max(cues[i], cues[i - 1] + 1.2)
    return [min(c, duration - 0.45) for c in cues]


def split_sentences(text: str) -> list[str]:
    text = re.sub(r"\s+", " ", (text or "").strip())
    if not text:
        return []
    parts = re.split(r"(?<=[.!?])\s+", text)
    return [p.strip() for p in parts if p.strip()]


def srt_time(seconds: float) -> str:
    ms = int(round(seconds * 1000))
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def write_srt(entries: list[tuple[float, float, str]], path: Path) -> None:
    lines: list[str] = []
    for i, (start, end, text) in enumerate(entries, 1):
        lines += [str(i), f"{srt_time(start)} --> {srt_time(end)}", text, ""]
    path.write_text("\n".join(lines), encoding="utf-8")


def write_chapters(chapters: list[dict], metadata: Path, human: Path) -> None:
    meta = [";FFMETADATA1", "title=Herramientas de ecosistema y CI/CD"]
    human_lines = []
    for ch in chapters:
        start = int(ch["start"] * 1000)
        end = int(ch["end"] * 1000)
        meta += ["[CHAPTER]", "TIMEBASE=1/1000", f"START={start}", f"END={end}",
                 f"title={ch['titulo']}"]
        human_lines.append(f"{srt_time(ch['start'])[:-4]} - {srt_time(ch['end'])[:-4]}  {ch['titulo']}")
    metadata.write_text("\n".join(meta) + "\n", encoding="utf-8")
    human.write_text("\n".join(human_lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Genera un video narrado desde video.json")
    parser.add_argument("--guion", required=True, help="Ruta a video.json")
    parser.add_argument("--salida", default="video", help="Carpeta de salida")
    parser.add_argument("--voz", default="Paulina", help="Voz de macOS o edge-tts")
    parser.add_argument("--motor", default="auto", choices=["auto", "say", "edge", "pyttsx3"],
                        help="Motor de voz")
    args = parser.parse_args()

    if shutil.which("ffmpeg") is None or shutil.which("ffprobe") is None:
        eprint("ERROR: ffmpeg y ffprobe deben estar en PATH. En macOS: brew install ffmpeg")
        return 2

    guion = json.loads(Path(args.guion).read_text(encoding="utf-8"))
    salida = Path(args.salida)
    (salida / "audio").mkdir(parents=True, exist_ok=True)
    (salida / "slides").mkdir(parents=True, exist_ok=True)
    (salida / "segmentos").mkdir(parents=True, exist_ok=True)
    voz = args.voz or guion.get("voz") or "Paulina"

    chapters: list[dict] = []
    srt_entries: list[tuple[float, float, str]] = []
    segments: list[Path] = []
    cursor = 0.0

    capitulos = guion.get("capitulos", [])
    total_slides = sum(len(c.get("slides", [])) for c in capitulos)
    total_chapters = len(capitulos)
    slide_no = 0
    silencio = salida / "audio" / "_silencio.wav"

    # Portada animada
    duracion_portada = 2.8
    portada = salida / "segmentos" / "00-portada.mp4"
    make_silence(silencio, duracion_portada)
    encode_segment(lambda t: draw_title_frame(t, duracion_portada, guion.get("titulo", "Curso")),
                   silencio, portada, duracion_portada)
    segments.append(portada)
    cursor += duracion_portada

    for ch_idx, ch in enumerate(capitulos, 1):
        ch_start = cursor
        ch_id = ch.get("id", "00")
        ch_title = ch.get("titulo", "")

        # Tarjeta de capítulo
        duracion_tarjeta = 1.9
        tarjeta = salida / "segmentos" / f"{ch_id}-00-tarjeta.mp4"
        make_silence(silencio, duracion_tarjeta)
        encode_segment(
            lambda t, i=ch_idx, ttl=ch_title: draw_chapter_frame(
                t, duracion_tarjeta, i, total_chapters, ttl),
            silencio, tarjeta, duracion_tarjeta)
        segments.append(tarjeta)
        cursor += duracion_tarjeta

        print(f"[capitulo {ch_id}] {ch_title}")
        for s in ch.get("slides", []):
            slide_no += 1
            sid = f"{ch_id}-{slide_no:02d}"
            wav = salida / "audio" / f"{sid}.wav"
            seg = salida / "segmentos" / f"{sid}.mp4"

            audio_dur = make_audio(s.get("narracion", ""), wav, voz, args.motor)
            duration = max(audio_dur + 0.8, 2.0)
            cues = compute_cues(s.get("narracion", ""), duration, len(s.get("bullets") or []))
            prep = prepare_slide(s, ch_title, slide_no, total_slides, ch_idx, duration, cues)
            encode_segment(lambda t, p=prep: draw_slide_frame(p, t), wav, seg, duration)
            segments.append(seg)

            sentences = split_sentences(s.get("narracion", ""))
            if sentences:
                total_chars = sum(len(x) for x in sentences) or 1
                t = cursor
                for sentence in sentences:
                    share = max(len(sentence) / total_chars * audio_dur, 0.9)
                    end = min(t + share, cursor + audio_dur)
                    srt_entries.append((t, end, sentence))
                    t = end
                if srt_entries:
                    srt_entries[-1] = (srt_entries[-1][0], cursor + audio_dur, srt_entries[-1][2])

            cursor += duration
            print(f"  slide {slide_no:02d}/{total_slides}: {duration:5.1f}s  {s.get('titulo','')[:60]}")
        chapters.append({"titulo": ch_title, "start": ch_start, "end": cursor})

    # Cierre
    duracion_fin = 2.4
    cierre = salida / "segmentos" / "99-cierre.mp4"
    make_silence(silencio, duracion_fin)
    encode_segment(lambda t: draw_end_frame(t, duracion_fin), silencio, cierre, duracion_fin)
    segments.append(cierre)
    cursor += duracion_fin

    lista = salida / "lista.txt"
    lista.write_text("".join(f"file '{p.resolve().as_posix()}'\n" for p in segments), encoding="utf-8")

    sin_subs = salida / "_sin_subs.mp4"
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(lista), "-c", "copy", str(sin_subs)],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    srt = salida / "subtitulos.srt"
    write_srt(srt_entries, srt)
    meta = salida / "capitulos.metadata.txt"
    human = salida / "capitulos.txt"
    write_chapters(chapters, meta, human)

    final = salida / "exposicion.mp4"
    run([
        "ffmpeg", "-y", "-i", str(sin_subs), "-i", str(srt), "-i", str(meta),
        "-map", "0:v", "-map", "0:a", "-map", "1:s", "-map_metadata", "2",
        "-c:v", "copy", "-c:a", "copy", "-c:s", "mov_text",
        "-metadata:s:s:0", "language=spa",
        "-metadata", f"title={guion.get('titulo', 'Curso')}",
        str(final),
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    dur = probe_duration(final)
    print(f"\nOK: {final} ({dur/60:.1f} min, {final.stat().st_size/1024/1024:.1f} MB)")
    print(f"Subtitulos: {srt}")
    print(f"Capitulos: {human}")
    if dur < 1200:
        print("AVISO: el video dura menos de 20 min. Agrega narracion o baja la velocidad de voz.")
    if final.stat().st_size > 100 * 1024 * 1024:
        print("AVISO: el MP4 supera 100 MB. No lo subas a GitHub; usa Git LFS o entregalo aparte.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
