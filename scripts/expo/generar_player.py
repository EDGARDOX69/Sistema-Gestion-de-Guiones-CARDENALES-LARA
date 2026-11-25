#!/usr/bin/env python3
"""Genera un reproductor HTML interactivo para el video de la exposición.

- Capítulos clicables y barra de progreso con marcas.
- Pregunta de repaso al terminar cada capítulo (banco de EVALUACION_SECCION.md).
- Notas por capítulo y progreso guardados en localStorage.
- Funciona offline: solo necesita el MP4 al lado.

Uso: python scripts/expo/generar_player.py [--salida video]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from generar_curso import parse_evaluacion  # noqa: E402

EVALUACION = RAIZ / "docs" / "exposicion" / "EVALUACION_SECCION.md"
GUION = RAIZ / "docs" / "exposicion" / "fuente" / "video.json"


def a_segundos(texto: str) -> float:
    h, m, s = texto.split(":")
    return int(h) * 3600 + int(m) * 60 + int(s)


def leer_capitulos(ruta: Path) -> list[dict]:
    capitulos = []
    for linea in ruta.read_text(encoding="utf-8").splitlines():
        m = re.match(r"(\d{2}:\d{2}:\d{2}) - (\d{2}:\d{2}:\d{2})\s+(.*)$", linea.strip())
        if m:
            capitulos.append({"inicio": a_segundos(m.group(1)),
                              "fin": a_segundos(m.group(2)), "titulo": m.group(3).strip()})
    return capitulos


PLANTILLA = """<!DOCTYPE html>
<html lang="es" data-tema="oscuro">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>__TITULO__ · reproductor interactivo</title>
<style>
:root{
  --fondo:#0a0e14; --panel:#111823; --panel2:#161f2b; --texto:#f0f4f8; --suave:#8b98aa;
  --borde:#26313f; --acento:#38bdf8; --ok:#34d399; --mal:#f87171;
}
*{box-sizing:border-box}
body{margin:0;background:var(--fondo);color:var(--texto);
  font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Inter,Roboto,Helvetica,Arial,sans-serif}
header{display:flex;align-items:center;gap:1rem;padding:.8rem 1.2rem;border-bottom:1px solid var(--borde);
  position:sticky;top:0;background:rgba(10,14,20,.92);backdrop-filter:blur(8px);z-index:10}
header h1{font-size:.95rem;margin:0;flex:1;font-weight:600;letter-spacing:.2px}
header .kicker{color:var(--acento);font-size:.72rem;letter-spacing:.12em;font-weight:700}
.layout{display:grid;grid-template-columns:minmax(0,1fr) 340px;gap:1.2rem;max-width:1500px;margin:0 auto;padding:1.2rem}
.video-caja{background:var(--panel);border:1px solid var(--borde);border-radius:16px;overflow:hidden}
video{display:block;width:100%;background:#000;aspect-ratio:16/9}
.timeline{position:relative;height:26px;background:var(--panel2);cursor:pointer;border-top:1px solid var(--borde)}
.timeline .relleno{position:absolute;left:0;top:0;bottom:0;background:rgba(56,189,248,.22);width:0}
.timeline .marca{position:absolute;top:0;bottom:0;width:1px;background:var(--borde)}
.timeline .marca:hover{background:var(--acento)}
.controles{display:flex;align-items:center;gap:.6rem;padding:.6rem .8rem;flex-wrap:wrap}
button{font:inherit;cursor:pointer;border:1px solid var(--borde);background:var(--panel2);
  color:var(--texto);border-radius:9px;padding:.4rem .7rem;transition:.15s}
button:hover{border-color:var(--acento)}
button.primario{background:var(--acento);color:#06202e;border-color:transparent;font-weight:700}
select{font:inherit;background:var(--panel2);color:var(--texto);border:1px solid var(--borde);
  border-radius:9px;padding:.4rem .5rem}
.estado{color:var(--suave);font-size:.86rem;margin-left:auto}
.info{padding:.9rem 1rem 1.1rem}
.info h2{margin:.1rem 0 .3rem;font-size:1.15rem}
.info p{margin:.2rem 0 .8rem;color:var(--suave);font-size:.9rem}
textarea{width:100%;min-height:90px;background:var(--panel2);color:var(--texto);border:1px solid var(--borde);
  border-radius:10px;padding:.7rem;font:inherit;resize:vertical}
aside{background:var(--panel);border:1px solid var(--borde);border-radius:16px;padding:1rem;
  align-self:start;position:sticky;top:70px;max-height:calc(100vh - 90px);overflow:auto}
aside h2{font-size:.8rem;letter-spacing:.1em;color:var(--suave);margin:.2rem 0 .7rem}
.progreso{height:8px;background:var(--panel2);border-radius:99px;overflow:hidden;margin:.3rem 0 .8rem}
.progreso span{display:block;height:100%;background:linear-gradient(90deg,var(--acento),var(--ok));width:0}
.cap{display:flex;gap:.6rem;align-items:baseline;padding:.5rem .4rem;border-radius:8px;cursor:pointer;
  color:var(--texto);text-decoration:none;font-size:.88rem;border:1px solid transparent}
.cap:hover{background:var(--panel2)}
.cap.activo{background:rgba(56,189,248,.12);border-color:rgba(56,189,248,.35)}
.cap.visto{color:var(--suave)}
.cap .n{color:var(--acento);font-size:.72rem;font-weight:700;min-width:1.5rem}
.cap .t{flex:1}
.cap .d{color:var(--suave);font-size:.72rem}
.modal{position:fixed;inset:0;background:rgba(4,8,14,.78);display:flex;align-items:center;justify-content:center;
  padding:1rem;z-index:40}
.modal.oculto{display:none}
.tarjeta{background:var(--panel);border:1px solid var(--borde);border-radius:18px;max-width:620px;width:100%;
  padding:1.4rem;box-shadow:0 30px 80px rgba(0,0,0,.5)}
.tarjeta .eyebrow{color:var(--acento);font-size:.72rem;letter-spacing:.12em;font-weight:700}
.tarjeta h3{margin:.35rem 0 .9rem;font-size:1.15rem;line-height:1.4}
.opcion{display:flex;gap:.6rem;align-items:flex-start;padding:.55rem .6rem;border:1px solid var(--borde);
  border-radius:10px;margin:.4rem 0;cursor:pointer}
.opcion:hover{border-color:var(--acento)}
.opcion input{margin-top:.35rem}
.feedback{font-weight:700;margin:.7rem 0}
.feedback.ok{color:var(--ok)} .feedback.mal{color:var(--mal)}
.acciones{display:flex;gap:.6rem;justify-content:flex-end;margin-top:1rem}
@media(max-width:980px){.layout{grid-template-columns:1fr}aside{position:static;max-height:none;order:2}}
</style>
</head>
<body>
<header>
  <div>
    <div class="kicker">GUÍA INTERACTIVA · ITINERARIO</div>
    <h1>__TITULO__</h1>
  </div>
  <a href="../curso/index.html" style="color:var(--acento);font-size:.85rem">Abrir curso</a>
  __EXTRA__
</header>
<div class="layout">
  <main>
    <div class="video-caja">
      <video id="video" controls preload="metadata" src="__VIDEO__"></video>
      <div class="timeline" id="timeline" title="Salta a un capítulo"></div>
      <div class="controles">
        <button id="anterior">← Capítulo</button>
        <button id="siguiente">Capítulo →</button>
        <select id="velocidad" aria-label="Velocidad">
          <option value="0.75">0,75×</option>
          <option value="1" selected>1×</option>
          <option value="1.25">1,25×</option>
          <option value="1.5">1,5×</option>
        </select>
        <label style="font-size:.85rem;color:var(--suave);display:flex;gap:.4rem;align-items:center">
          <input type="checkbox" id="preguntas" checked> Repaso al terminar capítulo
        </label>
        <span class="estado" id="estado">Listo</span>
      </div>
      <div class="info">
        <h2 id="capTitulo">—</h2>
        <p id="capRango"></p>
        <label for="notas" style="font-size:.8rem;letter-spacing:.08em;color:var(--suave)">NOTAS DE ESTE CAPÍTULO</label>
        <textarea id="notas" placeholder="Anota lo que quieras defender o repasar…"></textarea>
      </div>
    </div>
  </main>
  <aside>
    <h2>PROGRESO</h2>
    <div class="progreso"><span id="barra"></span></div>
    <div id="textoProgreso" style="font-size:.82rem;color:var(--suave);margin-bottom:.8rem">0 de 12 capítulos</div>
    <h2>CAPÍTULOS</h2>
    <div id="listaCaps"></div>
  </aside>
</div>
<div class="modal oculto" id="modal">
  <div class="tarjeta">
    <div class="eyebrow" id="modalEyebrow">REPASO</div>
    <h3 id="modalPregunta"></h3>
    <div id="modalOpciones"></div>
    <div class="feedback" id="modalFeedback"></div>
    <div class="acciones">
      <button id="modalContinuar" class="primario">Continuar</button>
    </div>
  </div>
</div>
<script>
const CAPS = __CAPITULOS__;
const QUIZ = __QUIZ__;
const video = document.getElementById('video');
const LS = {
  get(k,d){try{const v=localStorage.getItem(k);return v===null?d:JSON.parse(v)}catch(e){return d}},
  set(k,v){try{localStorage.setItem(k,JSON.stringify(v))}catch(e){}}
};
const claveVistos='itinerario.video.vistos';
const claveNotas='itinerario.video.notas';
const memoria=(()=>{try{return JSON.parse(window.name||'{}')}catch(e){return {}}})();
let vistos=new Set(LS.get(claveVistos,memoria.vistos||[]));
let notas=LS.get(claveNotas,memoria.notas||{});
let capActual=-1;
let preguntado=new Set();
function guardar(){
  LS.set(claveVistos,[...vistos]); LS.set(claveNotas,notas);
  try{window.name=JSON.stringify({vistos:[...vistos],notas})}catch(e){}
}

function fmt(s){const m=Math.floor(s/60),ss=Math.floor(s%60);return m+':'+String(ss).padStart(2,'0')}
function capEn(t){for(let i=CAPS.length-1;i>=0;i--){if(t>=CAPS[i].inicio)return i}return 0}

function pintarLista(){
  const cont=document.getElementById('listaCaps');
  cont.innerHTML=CAPS.map((c,i)=>`
    <div class="cap ${i===capActual?'activo':''} ${vistos.has(i)?'visto':''}" data-i="${i}">
      <span class="n">${String(i+1).padStart(2,'0')}</span>
      <span class="t">${c.titulo}</span>
      <span class="d">${fmt(c.fin-c.inicio)}</span>
    </div>`).join('');
  cont.querySelectorAll('.cap').forEach(el=>el.addEventListener('click',()=>{
    const i=Number(el.dataset.i); video.currentTime=CAPS[i].inicio; video.play();
  }));
}
function pintarTimeline(){
  const tl=document.getElementById('timeline');
  tl.innerHTML='<div class="relleno" id="relleno"></div>'+
    CAPS.map((c,i)=>`<div class="marca" style="left:${(c.inicio/video.duration)*100}%" title="${c.titulo}" data-i="${i}"></div>`).join('');
  tl.querySelectorAll('.marca').forEach(m=>m.addEventListener('click',ev=>{
    ev.stopPropagation(); video.currentTime=CAPS[Number(m.dataset.i)].inicio;
  }));
  tl.addEventListener('click',ev=>{
    const r=tl.getBoundingClientRect();
    video.currentTime=((ev.clientX-r.left)/r.width)*video.duration;
  });
}
function pintarProgreso(){
  const pct=Math.round(vistos.size*100/CAPS.length);
  document.getElementById('barra').style.width=pct+'%';
  document.getElementById('textoProgreso').textContent=`${vistos.size} de ${CAPS.length} capítulos`;
}
function actualizarInfo(){
  const i=capEn(video.currentTime);
  if(i!==capActual){
    capActual=i; pintarLista();
    document.getElementById('capTitulo').textContent=CAPS[i].titulo;
    document.getElementById('capRango').textContent=`Capítulo ${i+1} de ${CAPS.length} · ${fmt(CAPS[i].inicio)} – ${fmt(CAPS[i].fin)}`;
    document.getElementById('notas').value=notas[i]||'';
  }
  const r=document.getElementById('relleno');
  if(r && video.duration) r.style.width=(video.currentTime/video.duration*100)+'%';
  document.getElementById('estado').textContent=fmt(video.currentTime)+' / '+fmt(video.duration||0);
}
function marcarVisto(i){
  if(vistos.has(i))return;
  vistos.add(i); guardar(); pintarProgreso(); pintarLista();
}
function quizDe(i){
  const pool=QUIZ.filter(q=>q.capitulo===i);
  if(!pool.length)return null;
  return pool[Math.floor(Math.random()*pool.length)];
}
function mostrarQuiz(i){
  const q=quizDe(i); if(!q)return;
  document.getElementById('modalEyebrow').textContent='REPASO · CAPÍTULO '+(i+1);
  document.getElementById('modalPregunta').textContent=q.pregunta;
  document.getElementById('modalOpciones').innerHTML=q.opciones.map(o=>`
    <label class="opcion"><input type="radio" name="q" value="${o.letra}"><span>${o.letra}) ${o.texto}</span></label>`).join('');
  const fb=document.getElementById('modalFeedback'); fb.className='feedback'; fb.textContent='';
  document.getElementById('modal').classList.remove('oculto');
  document.querySelectorAll('#modalOpciones input').forEach(inp=>inp.addEventListener('change',()=>{
    if(inp.value===q.correcta){fb.className='feedback ok';fb.textContent='✔ Correcto.';}
    else{fb.className='feedback mal';fb.textContent='✘ La respuesta correcta es '+q.correcta+'.';}
  }));
}
function finalizarCapitulo(i){
  marcarVisto(i);
  if(document.getElementById('preguntas').checked && !preguntado.has(i)){
    preguntado.add(i); video.pause(); mostrarQuiz(i);
  }
}
video.addEventListener('timeupdate',()=>{
  const i=capEn(video.currentTime);
  if(i!==capActual){
    const previo=capActual;
    actualizarInfo();
    const exceso=video.currentTime-CAPS[previo].fin;
    if(previo>=0 && exceso>=0 && exceso<3){ finalizarCapitulo(previo); }
  }else{
    actualizarInfo();
  }
});
video.addEventListener('ended',()=>finalizarCapitulo(CAPS.length-1));
video.addEventListener('loadedmetadata',()=>{pintarTimeline();actualizarInfo();pintarProgreso();});
document.getElementById('notas').addEventListener('input',e=>{
  notas[capActual]=e.target.value; guardar();
});
document.getElementById('velocidad').addEventListener('change',e=>{video.playbackRate=Number(e.target.value)});
document.getElementById('anterior').addEventListener('click',()=>{
  const i=Math.max(0,capEn(video.currentTime)-1); video.currentTime=CAPS[i].inicio;
});
document.getElementById('siguiente').addEventListener('click',()=>{
  const i=Math.min(CAPS.length-1,capEn(video.currentTime)+1); video.currentTime=CAPS[i].inicio;
});
document.getElementById('modalContinuar').addEventListener('click',()=>{
  document.getElementById('modal').classList.add('oculto'); video.play();
});
document.addEventListener('keydown',e=>{
  if(e.target.tagName==='TEXTAREA')return;
  if(e.code==='Space'){e.preventDefault(); video.paused?video.play():video.pause();}
  if(e.code==='ArrowRight'){video.currentTime+=5}
  if(e.code==='ArrowLeft'){video.currentTime-=5}
});
pintarLista(); pintarProgreso();
</script>
</body>
</html>
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Genera el reproductor interactivo del video.")
    parser.add_argument("--salida", default=str(RAIZ / "video"))
    parser.add_argument("--modo", choices=["largo", "historia"], default="largo")
    args = parser.parse_args()
    salida = Path(args.salida)

    preguntas = parse_evaluacion(EVALUACION)
    por_numero = {q["numero"]: q for q in preguntas}

    if args.modo == "historia":
        timeline = json.loads((RAIZ / "video-remotion" / "public" / "timeline.json")
                              .read_text(encoding="utf-8"))
        capitulos = leer_capitulos(salida / "historia_capitulos.txt")
        titulo = timeline.get("titulo", "Historia")
        video = "historia.mp4"
        destino = salida / "historia.html"
        extra = ('<a href="index.html" style="color:var(--suave);font-size:.85rem">'
                 'Versión larga</a>')
        mapa = {
            0: [1, 6], 1: [2, 3, 7], 2: [1, 7], 3: [9, 10, 11, 12],
            4: [17, 18, 19, 20], 5: [16, 21, 24, 25, 26],
            6: [27, 28, 29, 30], 7: [6, 12], 8: [5, 8], 9: [1],
        }
    else:
        guion = json.loads(GUION.read_text(encoding="utf-8"))
        capitulos = leer_capitulos(salida / "capitulos.txt")
        titulo = guion.get("titulo", "Curso")
        video = "exposicion.mp4"
        destino = salida / "index.html"
        extra = ('<a href="historia.html" style="color:var(--suave);font-size:.85rem">'
                 'Ver historia</a>')
        mapa = {
            1: [1], 2: [1, 2, 3, 4, 5, 6, 7, 8], 3: [9, 10, 11, 12],
            4: [13, 14, 15], 5: [13, 14], 6: [16, 17, 18],
            7: [19, 20, 21, 22], 8: [27], 9: [23, 24, 25, 26],
            10: [23, 24, 25, 26], 11: [27, 28, 29, 30], 12: [6, 12],
        }

    quiz = []
    for capitulo, numeros in mapa.items():
        for numero in numeros:
            q = por_numero.get(numero)
            if not q:
                continue
            quiz.append({"pregunta": q["pregunta"], "opciones": q["opciones"],
                         "correcta": q["correcta"], "capitulo": capitulo - 1})

    html = (PLANTILLA
            .replace("__TITULO__", titulo)
            .replace("__VIDEO__", video)
            .replace("__EXTRA__", extra)
            .replace("__CAPITULOS__", json.dumps(capitulos, ensure_ascii=False))
            .replace("__QUIZ__", json.dumps(quiz, ensure_ascii=False)))
    destino.write_text(html, encoding="utf-8")
    print(f"OK: {destino} ({len(html.encode('utf-8'))/1024:.0f} KB, "
          f"{len(capitulos)} capítulos, {len(quiz)} preguntas)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
