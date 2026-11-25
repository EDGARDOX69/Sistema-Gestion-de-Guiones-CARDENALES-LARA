#!/usr/bin/env bash
# Empaqueta la historia renderizada: subtítulos, evidencias y portada.
set -euo pipefail
RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$RAIZ"
export PATH="$RAIZ/venv/bin:$PATH"

SRC="$RAIZ/video-remotion/out/historia.mp4"
OUT="$RAIZ/video/historia.mp4"
EVID="$RAIZ/docs/exposicion/evidencias/video"
mkdir -p "$EVID"

if [[ ! -f "$SRC" ]]; then
  echo "Falta $SRC. Renderiza primero con Remotion." >&2
  exit 1
fi

echo "== 1/4 subtítulos =="
ffmpeg -y -v error -i "$SRC" -i "$RAIZ/video/historia.srt" \
  -map 0 -map 1 -c:v copy -c:a copy -c:s mov_text \
  -metadata:s:s:0 language=spa -movflags +faststart "$OUT"

echo "== 2/4 ffprobe =="
ffprobe -v error -show_entries format=duration,size \
  -show_entries stream=codec_type,codec_name,width,height -of json "$OUT" \
  | tee "$EVID/ffprobe_historia.json" >/dev/null

echo "== 3/4 contact sheet =="
ffmpeg -y -v error -i "$OUT" -vf "fps=1/32,scale=320:-1,tile=4x3" \
  -frames:v 1 "$EVID/contact-sheet-historia.jpg"

echo "== 4/4 portada =="
ffmpeg -y -v error -ss 6 -i "$OUT" -frames:v 1 "$RAIZ/video/historia_portada.png"

echo "OK: $OUT"
ls -lh "$OUT" "$RAIZ/video/historia_portada.png" "$EVID/contact-sheet-historia.jpg"
