#!/usr/bin/env python3
"""Genera un curso HTML autocontenido a partir de los documentos de la exposición.

Entrada:
  docs/exposicion/fuente/CURSO.md          (15 módulos con secciones, preguntas y defensa)
  docs/exposicion/EVALUACION_SECCION.md    (30 preguntas con opciones y clave)
  docs/exposicion/PREGUNTAS_DEFENSA.md     (preguntas abiertas con respuesta modelo)

Salida:
  curso/index.html
  curso/index-single.html   (mismo contenido, portable)
  curso/start.sh

Sin dependencias externas: solo la biblioteca estándar.
"""
from __future__ import annotations

import argparse
import html
import json
import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
FUENTE = RAIZ / "docs" / "exposicion" / "fuente" / "CURSO.md"
EVALUACION = RAIZ / "docs" / "exposicion" / "EVALUACION_SECCION.md"
DEFENSA = RAIZ / "docs" / "exposicion" / "PREGUNTAS_DEFENSA.md"

EXCLUIR_SECCIONES = {"objetivo", "aplicación a itinerario", "aplicacion a itinerario",
                     "preguntas", "frase de defensa"}


# ---------------------------------------------------------------------------
# Markdown mínimo
# ---------------------------------------------------------------------------
def _inline(texto: str) -> str:
    """Escapa HTML y aplica negritas, cursivas, código y enlaces."""
    t = html.escape(texto, quote=False)
    t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
    t = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", t)
    t = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2" target="_blank" rel="noopener">\1</a>', t)
    return t


def md_to_html(texto: str) -> str:
    lineas = texto.splitlines()
    salida: list[str] = []
    i = 0
    parrafo: list[str] = []

    def volcar_parrafo() -> None:
        if parrafo:
            salida.append("<p>" + _inline(" ".join(parrafo).strip()) + "</p>")
            parrafo.clear()

    while i < len(lineas):
        linea = lineas[i]
        limpia = linea.strip()

        if limpia.startswith("```"):
            volcar_parrafo()
            lenguaje = limpia[3:].strip()
            i += 1
            bloque: list[str] = []
            while i < len(lineas) and not lineas[i].strip().startswith("```"):
                bloque.append(lineas[i])
                i += 1
            clase = f' class="lenguaje-{html.escape(lenguaje)}"' if lenguaje else ""
            salida.append(f"<pre><code{clase}>" + html.escape("\n".join(bloque)) + "</code></pre>")
            i += 1
            continue

        if not limpia:
            volcar_parrafo()
            i += 1
            continue

        if re.fullmatch(r"-{3,}", limpia):
            volcar_parrafo()
            salida.append("<hr>")
            i += 1
            continue

        if limpia.startswith("|") and i + 1 < len(lineas) and re.match(r"^\|[\s:|-]+\|$", lineas[i + 1].strip()):
            volcar_parrafo()
            cabecera = [c.strip() for c in limpia.strip("|").split("|")]
            i += 2
            filas: list[list[str]] = []
            while i < len(lineas) and lineas[i].strip().startswith("|"):
                filas.append([c.strip() for c in lineas[i].strip().strip("|").split("|")])
                i += 1
            th = "".join(f"<th>{_inline(c)}</th>" for c in cabecera)
            cuerpo = "".join(
                "<tr>" + "".join(f"<td>{_inline(c)}</td>" for c in fila) + "</tr>" for fila in filas
            )
            salida.append(f"<table><thead><tr>{th}</tr></thead><tbody>{cuerpo}</tbody></table>")
            continue

        if limpia.startswith(">"):
            volcar_parrafo()
            cita: list[str] = []
            while i < len(lineas) and lineas[i].strip().startswith(">"):
                cita.append(lineas[i].strip().lstrip(">").strip())
                i += 1
            salida.append("<blockquote>" + _inline(" ".join(cita)) + "</blockquote>")
            continue

        m = re.match(r"^(#{2,6})\s+(.*)$", limpia)
        if m:
            volcar_parrafo()
            nivel = min(len(m.group(1)) + 1, 6)
            salida.append(f"<h{nivel}>{_inline(m.group(2))}</h{nivel}>")
            i += 1
            continue

        if re.match(r"^[-*]\s+", limpia):
            volcar_parrafo()
            items: list[str] = []
            while i < len(lineas) and re.match(r"^\s*[-*]\s+", lineas[i]):
                item = re.sub(r"^\s*[-*]\s+", "", lineas[i])
                i += 1
                while i < len(lineas) and lineas[i].startswith("  ") and lineas[i].strip() \
                        and not re.match(r"^\s*[-*]\s+", lineas[i]):
                    item += " " + lineas[i].strip()
                    i += 1
                items.append(f"<li>{_inline(item.strip())}</li>")
            salida.append("<ul>" + "".join(items) + "</ul>")
            continue

        if re.match(r"^\d+[.)]\s+", limpia):
            volcar_parrafo()
            items = []
            while i < len(lineas) and re.match(r"^\s*\d+[.)]\s+", lineas[i]):
                item = re.sub(r"^\s*\d+[.)]\s+", "", lineas[i])
                i += 1
                while i < len(lineas) and lineas[i].startswith("  ") and lineas[i].strip() \
                        and not re.match(r"^\s*\d+[.)]\s+", lineas[i]):
                    item += " " + lineas[i].strip()
                    i += 1
                items.append(f"<li>{_inline(item.strip())}</li>")
            salida.append("<ol>" + "".join(items) + "</ol>")
            continue

        parrafo.append(limpia)
        i += 1

    volcar_parrafo()
    return "\n".join(salida)


# ---------------------------------------------------------------------------
# Parsers
# ---------------------------------------------------------------------------
def parse_curso(ruta: Path) -> dict:
    texto = ruta.read_text(encoding="utf-8")
    lineas = texto.splitlines()
    titulo = next((l.lstrip("# ").strip() for l in lineas if l.startswith("# ")), "Curso")
    intro_lineas: list[str] = []
    modulos: list[dict] = []
    actual: dict | None = None
    seccion_actual: str | None = None
    buffer: list[str] = []

    def cerrar_seccion() -> None:
        nonlocal buffer, seccion_actual
        if actual is not None and seccion_actual is not None:
            contenido = "\n".join(buffer).strip()
            clave = seccion_actual.lower()
            if clave.startswith("preguntas"):
                preguntas = [
                    re.sub(r"^\d+[.)]\s*", "", l).strip()
                    for l in contenido.splitlines() if re.match(r"^\d+[.)]\s+", l.strip())
                ]
                actual["preguntas"] = preguntas
            elif clave.startswith("frase de defensa"):
                actual["defensa"] = re.sub(r"\s+", " ", contenido).strip().strip('"')
            elif clave not in EXCLUIR_SECCIONES:
                actual["secciones"].append({"titulo": seccion_actual, "html": md_to_html(contenido)})
            elif clave.startswith("objetivo") or clave.startswith("aplicaci"):
                actual["secciones"].append({"titulo": seccion_actual, "html": md_to_html(contenido),
                                            "tipo": "especial"})
        buffer = []
        seccion_actual = None

    for linea in lineas:
        m = re.match(r"^##\s+Módulo\s+(\d+)\.\s*(.*)$", linea.strip())
        if m:
            cerrar_seccion()
            if actual:
                modulos.append(actual)
            actual = {"numero": int(m.group(1)), "titulo": m.group(2).strip(),
                      "secciones": [], "preguntas": [], "defensa": ""}
            continue
        if linea.startswith("## ") and actual is None:
            intro_lineas.append(linea)
            continue
        m = re.match(r"^###\s+(.*)$", linea.strip())
        if m:
            cerrar_seccion()
            seccion_actual = m.group(1).strip()
            continue
        if actual is None:
            if not linea.startswith("#"):
                intro_lineas.append(linea)
        elif seccion_actual is not None:
            buffer.append(linea)
    cerrar_seccion()
    if actual:
        modulos.append(actual)

    return {
        "titulo": titulo,
        "intro_html": md_to_html("\n".join(intro_lineas)),
        "modulos": modulos,
    }


def parse_evaluacion(ruta: Path) -> list[dict]:
    texto = ruta.read_text(encoding="utf-8")
    if "## Clave de respuestas" in texto:
        cuerpo, clave_txt = texto.split("## Clave de respuestas", 1)
    else:
        cuerpo, clave_txt = texto, ""

    clave: dict[int, str] = {}
    for linea in clave_txt.splitlines():
        if not linea.strip().startswith("|"):
            continue
        celdas = [c.strip() for c in linea.strip().strip("|").split("|")]
        for i in range(0, len(celdas) - 1, 2):
            if celdas[i].isdigit() and celdas[i + 1] in {"a", "b", "c", "d"}:
                clave[int(celdas[i])] = celdas[i + 1]

    preguntas: list[dict] = []
    # El enunciado puede ocupar varias líneas; cierra con ** al final.
    patron = re.compile(r"\*\*(\d+)\.\s+(.*?)\*\*", re.S)
    marcas = list(patron.finditer(cuerpo))
    for idx, marca in enumerate(marcas):
        numero = int(marca.group(1))
        inicio = marca.end()
        fin = marcas[idx + 1].start() if idx + 1 < len(marcas) else len(cuerpo)
        bloque = cuerpo[inicio:fin]
        if "## Parte" in bloque:
            bloque = bloque.split("## Parte")[0]
        if "## Preguntas abiertas" in bloque:
            bloque = bloque.split("## Preguntas abiertas")[0]
        lineas = [l.rstrip() for l in bloque.strip().splitlines()]
        opciones: list[dict] = []
        actual_op: dict | None = None
        for linea in lineas:
            if linea.strip().startswith("---") or linea.strip().startswith("## "):
                break
            mo = re.match(r"^([a-d])\)\s*(.*)$", linea.strip())
            if mo:
                actual_op = {"letra": mo.group(1), "texto": mo.group(2).strip()}
                opciones.append(actual_op)
            elif actual_op is not None and linea.strip():
                actual_op["texto"] += " " + linea.strip()
        enunciado = re.sub(r"\s+", " ", marca.group(2)).strip()
        if not opciones or numero not in clave:
            continue
        preguntas.append({
            "numero": numero,
            "pregunta": enunciado,
            "opciones": [{"letra": o["letra"], "texto": re.sub(r"\s+", " ", o["texto"])} for o in opciones],
            "correcta": clave[numero],
        })
    return preguntas


def parse_defensa(ruta: Path) -> list[dict]:
    texto = ruta.read_text(encoding="utf-8")
    marcas = list(re.finditer(r"^###\s+(\d+)\.\s+(.*)$", texto, re.M))
    salida: list[dict] = []
    for idx, marca in enumerate(marcas):
        inicio = marca.end()
        fin = marcas[idx + 1].start() if idx + 1 < len(marcas) else len(texto)
        bloque = texto[inicio:fin]
        bloque = bloque.split("\n## ")[0].strip()
        respuesta = ""
        mr = re.search(r"\*\*Respuesta:\*\*\s*(.*?)(?=\n\*\*|\Z)", bloque, re.S)
        if mr:
            respuesta = re.sub(r"\s+", " ", mr.group(1)).strip()
        if respuesta:
            salida.append({"numero": int(marca.group(1)), "pregunta": marca.group(2).strip(),
                           "respuesta": respuesta})
    return salida


def parse_glosario(modulos: list[dict]) -> list[dict]:
    tarjetas: list[dict] = []
    for modulo in modulos:
        for seccion in modulo["secciones"]:
            if seccion["titulo"].lower().startswith("glosario"):
                for m in re.finditer(r"<li><strong>([^<]+):</strong>\s*(.*?)</li>", seccion["html"], re.S):
                    termino = html.unescape(re.sub(r"<[^>]+>", "", m.group(1)))
                    definicion = html.unescape(re.sub(r"<[^>]+>", "", m.group(2)))
                    tarjetas.append({"frente": termino.strip(), "reverso": definicion.strip(),
                                     "origen": f"Módulo {modulo['numero']}"})
    return tarjetas


def flashcards_de_secciones(modulos: list[dict]) -> list[dict]:
    tarjetas: list[dict] = []
    for modulo in modulos:
        for seccion in modulo["secciones"]:
            if seccion.get("tipo") == "especial":
                continue
            texto = re.sub(r"<[^>]+>", " ", seccion["html"])
            texto = html.unescape(re.sub(r"\s+", " ", texto)).strip()
            if len(texto) < 40:
                continue
            frase = re.split(r"(?<=[.!?])\s", texto)
            reverso = " ".join(frase[:2])[:260]
            tarjetas.append({"frente": seccion["titulo"], "reverso": reverso,
                             "origen": f"Módulo {modulo['numero']}"})
    return tarjetas


# ---------------------------------------------------------------------------
# HTML
# ---------------------------------------------------------------------------
CSS = """
:root{
  --fondo:#f6f7fb; --panel:#ffffff; --texto:#16202e; --suave:#5b6b82; --borde:#dde3ee;
  --acento:#1f6feb; --acento2:#0ea5a4; --ok:#15803d; --mal:#b91c1c; --sombra:0 10px 30px rgba(16,32,54,.08);
}
html[data-tema="oscuro"]{
  --fondo:#0b1220; --panel:#111b2d; --texto:#e8eefb; --suave:#9fb0cc; --borde:#22314b;
  --acento:#5ea1ff; --acento2:#2dd4bf; --ok:#4ade80; --mal:#f87171; --sombra:0 10px 30px rgba(0,0,0,.35);
}
*{box-sizing:border-box}
body{margin:0;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Inter,Roboto,Helvetica,Arial,sans-serif;
  background:var(--fondo);color:var(--texto);line-height:1.65}
a{color:var(--acento)}
header.top{position:sticky;top:0;z-index:30;display:flex;gap:.75rem;align-items:center;
  padding:.7rem 1rem;background:color-mix(in srgb,var(--panel) 88%,transparent);
  backdrop-filter:blur(8px);border-bottom:1px solid var(--borde)}
header.top h1{font-size:1rem;margin:0;flex:1;letter-spacing:.2px}
button{font:inherit;cursor:pointer;border:1px solid var(--borde);background:var(--panel);
  color:var(--texto);border-radius:10px;padding:.45rem .8rem;transition:.15s}
button:hover{border-color:var(--acento);transform:translateY(-1px)}
button.primario{background:var(--acento);color:#fff;border-color:transparent}
button.primario:hover{filter:brightness(1.07)}
.layout{display:grid;grid-template-columns:300px minmax(0,1fr);gap:1.25rem;max-width:1440px;
  margin:0 auto;padding:1.25rem}
aside{position:sticky;top:70px;align-self:start;max-height:calc(100vh - 90px);overflow:auto;
  background:var(--panel);border:1px solid var(--borde);border-radius:16px;padding:1rem;box-shadow:var(--sombra)}
aside input{width:100%;padding:.5rem .7rem;border-radius:9px;border:1px solid var(--borde);
  background:var(--fondo);color:var(--texto);margin-bottom:.75rem}
.progreso{height:9px;background:var(--borde);border-radius:99px;overflow:hidden;margin:.35rem 0 .8rem}
.progreso span{display:block;height:100%;width:0;background:linear-gradient(90deg,var(--acento),var(--acento2));
  transition:width .3s}
nav a{display:flex;gap:.5rem;align-items:center;padding:.45rem .55rem;border-radius:9px;
  color:var(--texto);text-decoration:none;font-size:.92rem}
nav a:hover{background:color-mix(in srgb,var(--acento) 10%,transparent)}
nav a.activo{background:color-mix(in srgb,var(--acento) 16%,transparent);font-weight:600}
nav a .num{font-variant-numeric:tabular-nums;color:var(--suave);font-size:.8rem;min-width:1.6rem}
nav a.hecho .num{color:var(--ok)}
main{min-width:0}
.modulo{background:var(--panel);border:1px solid var(--borde);border-radius:16px;padding:1.5rem 1.6rem;
  margin-bottom:1.25rem;box-shadow:var(--sombra);scroll-margin-top:80px}
.modulo h2{margin:.1rem 0 .6rem;font-size:1.35rem}
.modulo h3{margin:1.4rem 0 .5rem;font-size:1.08rem;color:var(--acento)}
.modulo p{margin:.55rem 0}
.modulo ul,.modulo ol{margin:.4rem 0 .8rem 1.2rem}
.modulo li{margin:.25rem 0}
.modulo code{background:color-mix(in srgb,var(--acento) 10%,transparent);padding:.1rem .35rem;
  border-radius:6px;font-size:.92em}
.modulo pre{background:#0d1526;color:#dbe7ff;padding:.9rem 1rem;border-radius:12px;overflow:auto;font-size:.88rem}
html[data-tema="claro"] .modulo pre{background:#101827}
.modulo table{border-collapse:collapse;width:100%;margin:.8rem 0;font-size:.92rem}
.modulo th,.modulo td{border:1px solid var(--borde);padding:.45rem .6rem;text-align:left}
.modulo th{background:color-mix(in srgb,var(--acento) 9%,transparent)}
blockquote{margin:.9rem 0;padding:.6rem .9rem;border-left:4px solid var(--acento2);
  background:color-mix(in srgb,var(--acento2) 8%,transparent);border-radius:0 10px 10px 0}
.especial{background:color-mix(in srgb,var(--acento) 6%,transparent);border:1px dashed var(--borde);
  border-radius:12px;padding:.8rem 1rem;margin:.9rem 0}
.defensa{margin-top:1rem;padding:.85rem 1rem;border-radius:12px;font-style:italic;
  background:color-mix(in srgb,var(--ok) 10%,transparent);border-left:4px solid var(--ok)}
.acciones-modulo{display:flex;gap:.6rem;flex-wrap:wrap;margin-top:1.1rem}
.hecho-badge{display:none;color:var(--ok);font-weight:600;align-self:center}
.modulo.hecho .hecho-badge{display:inline}
.quiz{margin-top:1.1rem;border-top:1px solid var(--borde);padding-top:.9rem}
.quiz h4{margin:.2rem 0 .7rem;font-size:.98rem}
.pregunta{border:1px solid var(--borde);border-radius:12px;padding:.8rem .9rem;margin:.7rem 0}
.pregunta p.enunciado{margin:.1rem 0 .55rem;font-weight:600}
.opcion{display:flex;gap:.5rem;align-items:flex-start;padding:.25rem 0;cursor:pointer}
.opcion input{margin-top:.35rem}
.feedback{display:none;margin-top:.5rem;font-size:.9rem;font-weight:600}
.feedback.ok{display:block;color:var(--ok)}
.feedback.mal{display:block;color:var(--mal)}
.paneljuego{background:var(--panel);border:1px solid var(--borde);border-radius:16px;padding:1.4rem;
  box-shadow:var(--sombra);margin-bottom:1.25rem}
.oculto{display:none !important}
.flashcard{min-height:150px;display:flex;align-items:center;justify-content:center;text-align:center;
  background:linear-gradient(135deg,color-mix(in srgb,var(--acento) 12%,var(--panel)),var(--panel));
  border:1px solid var(--borde);border-radius:14px;padding:1.2rem;margin:.8rem 0;cursor:pointer;font-size:1.05rem}
.flashcard small{display:block;margin-top:.6rem;color:var(--suave);font-size:.78rem}
.barra{display:flex;gap:.6rem;flex-wrap:wrap;align-items:center;margin:.4rem 0}
.resultado{font-size:1.05rem;font-weight:700;margin:.8rem 0}
.interpretacion{color:var(--suave)}
.examen .pregunta .feedback{font-weight:500}
footer{max-width:1440px;margin:0 auto;padding:1rem 1.25rem 2.5rem;color:var(--suave);font-size:.85rem}
@media(max-width:980px){
  .layout{grid-template-columns:1fr}
  aside{position:static;max-height:none;order:2}
  main{order:1}
  header.top h1{font-size:.9rem}
}
@media print{
  aside,header.top,.acciones-modulo,.quiz,.paneljuego{display:none !important}
  .modulo{box-shadow:none;border:none;page-break-inside:avoid}
  body{background:#fff;color:#000}
}
"""

JS = r"""
const CURSO = window.__CURSO__;
const LS = {
  get(k,d){try{const v=localStorage.getItem(k);return v===null?d:JSON.parse(v)}catch(e){return d}},
  set(k,v){try{localStorage.setItem(k,JSON.stringify(v))}catch(e){}}
};
const claveProgreso='itinerario.curso.progreso';
const claveTema='itinerario.curso.tema';
let hechos=new Set(LS.get(claveProgreso,[]));

function aplicarTema(tema){
  document.documentElement.setAttribute('data-tema',tema);
  document.getElementById('btnTema').textContent = tema==='oscuro' ? '☀️ Claro' : '🌙 Oscuro';
  LS.set(claveTema,tema);
}
function alternarTema(){
  const actual=document.documentElement.getAttribute('data-tema');
  aplicarTema(actual==='oscuro'?'claro':'oscuro');
}
function actualizarProgreso(){
  const total=CURSO.modulos.length;
  const pct=total?Math.round(hechos.size*100/total):0;
  document.getElementById('barraProgreso').style.width=pct+'%';
  document.getElementById('textoProgreso').textContent=pct+'% completado ('+hechos.size+'/'+total+')';
  CURSO.modulos.forEach(m=>{
    const card=document.getElementById('modulo-'+m.numero);
    const enlace=document.getElementById('nav-'+m.numero);
    const hecho=hechos.has(m.numero);
    if(card) card.classList.toggle('hecho',hecho);
    if(enlace) enlace.classList.toggle('hecho',hecho);
  });
}
function marcar(numero){
  if(hechos.has(numero)) hechos.delete(numero); else hechos.add(numero);
  LS.set(claveProgreso,[...hechos]);
  actualizarProgreso();
}
function filtrar(texto){
  const q=texto.trim().toLowerCase();
  CURSO.modulos.forEach(m=>{
    const enlace=document.getElementById('nav-'+m.numero);
    if(!enlace) return;
    const coincide=!q || (m.titulo+' '+m.textoBusqueda).toLowerCase().includes(q);
    enlace.classList.toggle('oculto',!coincide);
  });
}
function irAModulo(numero){
  const el=document.getElementById('modulo-'+numero);
  if(el) el.scrollIntoView({behavior:'smooth',block:'start'});
}
function corregirInline(boton){
  const quiz=boton.closest('.quiz');
  if(!quiz) return;
  quiz.querySelectorAll('.pregunta').forEach(pregunta=>{
    const elegida=pregunta.querySelector('input[type=radio]:checked');
    const feedback=pregunta.querySelector('.feedback');
    const correcta=pregunta.dataset.correcta;
    if(!elegida){feedback.className='feedback mal';feedback.textContent='Elige una opción.';return}
    if(elegida.value===correcta){
      feedback.className='feedback ok';feedback.textContent='✔ Correcto.';
    }else{
      feedback.className='feedback mal';
      feedback.textContent='✘ Incorrecto. La respuesta correcta es '+correcta+'.';
    }
  });
}
function abrirJuego(id){document.getElementById(id).classList.toggle('oculto')}

/* Flashcards */
let mazo=[], indiceMazo=0, mostrandoReverso=false;
function pintarTarjeta(){
  if(!mazo.length) return;
  const t=mazo[indiceMazo];
  document.getElementById('flashcard').innerHTML=(mostrandoReverso?t.reverso:t.frente)+
    '<small>'+t.origen+' · toca para '+(mostrandoReverso?'volver':'ver respuesta')+'</small>';
  document.getElementById('contadorMazo').textContent=(indiceMazo+1)+' / '+mazo.length;
}
function voltear(){mostrandoReverso=!mostrandoReverso;pintarTarjeta()}
function moverMazo(delta){
  if(!mazo.length) return;
  indiceMazo=(indiceMazo+delta+mazo.length)%mazo.length;
  mostrandoReverso=false;pintarTarjeta();
}
function mezclar(a){for(let i=a.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1));[a[i],a[j]]=[a[j],a[i]]}return a}
function iniciarMazo(){
  mazo=mezclar([...CURSO.flashcards]);indiceMazo=0;mostrandoReverso=false;
  document.getElementById('mazo').classList.remove('oculto');
  pintarTarjeta();
}

/* Defensa */
let defensaActual=null;
function nuevaDefensa(){
  const lista=CURSO.defensa;
  if(!lista.length) return;
  let siguiente;
  do{siguiente=Math.floor(Math.random()*lista.length)}while(lista.length>1 && siguiente===defensaActual);
  defensaActual=siguiente;
  const d=lista[siguiente];
  document.getElementById('defensaPregunta').textContent=d.pregunta;
  document.getElementById('defensaRespuesta').textContent=d.respuesta;
  document.getElementById('defensaRespuesta').classList.add('oculto');
  document.getElementById('defensaCaja').classList.remove('oculto');
}
function mostrarDefensa(){document.getElementById('defensaRespuesta').classList.remove('oculto')}

/* Examen */
function renderExamen(){
  const cont=document.getElementById('examenPreguntas');
  if(cont.dataset.listo) return;
  cont.innerHTML=CURSO.examen.map((q,i)=>`
    <div class="pregunta" data-num="${q.numero}" data-correcta="${q.correcta}">
      <p class="enunciado">${i+1}. ${q.pregunta}</p>
      ${q.opciones.map(o=>`<label class="opcion"><input type="radio" name="exam-${q.numero}" value="${o.letra}"><span>${o.letra}) ${o.texto}</span></label>`).join('')}
      <div class="feedback"></div>
    </div>`).join('');
  cont.dataset.listo='1';
}
function evaluarExamen(){
  renderExamen();
  let aciertos=0;
  document.querySelectorAll('#examenPreguntas .pregunta').forEach(p=>{
    const ok=p.dataset.correcta;
    const elegida=p.querySelector('input[type=radio]:checked');
    const fb=p.querySelector('.feedback');
    if(elegida && elegida.value===ok){aciertos++;fb.className='feedback ok';fb.textContent='✔ Correcto.'}
    else{fb.className='feedback mal';fb.textContent='✘ Correcto: '+ok+'.'+(elegida?' Elegiste '+elegida.value+'.':' Sin responder.')}
  });
  const total=CURSO.examen.length;
  const pct=Math.round(aciertos*100/total);
  let texto='';
  if(pct>=90) texto='Dominio sólido.';
  else if(pct>=70) texto='Base correcta; repasa los temas fallados.';
  else if(pct>=50) texto='Necesita repaso guiado.';
  else texto='Vuelve al curso desde el módulo 1.';
  document.getElementById('resultadoExamen').innerHTML=
    `Resultado: <strong>${aciertos}/${total}</strong> (${pct}%). <span class="interpretacion">${texto}</span>`;
}

/* Navegación activa */
function observarModulos(){
  if(!('IntersectionObserver' in window)) return;
  const enlaces=new Map(CURSO.modulos.map(m=>[m.numero,document.getElementById('nav-'+m.numero)]));
  const obs=new IntersectionObserver(entries=>{
    entries.forEach(e=>{
      if(e.isIntersecting){
        enlaces.forEach(a=>a&&a.classList.remove('activo'));
        const enlace=enlaces.get(Number(e.target.dataset.numero));
        if(enlace) enlace.classList.add('activo');
      }
    });
  },{rootMargin:'-40% 0px -55% 0px'});
  document.querySelectorAll('.modulo').forEach(m=>obs.observe(m));
}

document.addEventListener('DOMContentLoaded',()=>{
  aplicarTema(LS.get(claveTema,'claro'));
  actualizarProgreso();
  observarModulos();
  document.getElementById('buscador').addEventListener('input',e=>filtrar(e.target.value));
  document.getElementById('btnTema').addEventListener('click',alternarTema);
  document.querySelectorAll('.marcar').forEach(b=>b.addEventListener('click',()=>marcar(Number(b.dataset.numero))));
  document.querySelectorAll('.corregir').forEach(b=>b.addEventListener('click',()=>corregirInline(b)));
  document.getElementById('btnMazo').addEventListener('click',iniciarMazo);
  document.getElementById('flashcard').addEventListener('click',voltear);
  document.getElementById('btnAnterior').addEventListener('click',()=>moverMazo(-1));
  document.getElementById('btnSiguiente').addEventListener('click',()=>moverMazo(1));
  document.getElementById('btnDefensa').addEventListener('click',nuevaDefensa);
  document.getElementById('btnMostrarDefensa').addEventListener('click',mostrarDefensa);
  document.getElementById('btnExamen').addEventListener('click',()=>{renderExamen();abrirJuego('examenCaja')});
  document.getElementById('evaluarExamen').addEventListener('click',evaluarExamen);
  document.getElementById('reiniciarExamen').addEventListener('click',()=>{
    document.querySelectorAll('#examenPreguntas input').forEach(i=>i.checked=false);
    document.querySelectorAll('#examenPreguntas .feedback').forEach(f=>{f.className='feedback';f.textContent=''});
    document.getElementById('resultadoExamen').textContent='';
  });
  document.querySelectorAll('.enlace-modulo').forEach(a=>a.addEventListener('click',ev=>{
    ev.preventDefault();irAModulo(Number(a.dataset.numero));
  }));
});
"""


def construir_html(curso: dict, examen: list[dict], defensa: list[dict]) -> str:
    por_modulo: dict[int, list[dict]] = {}
    for q in examen:
        destino = ((q["numero"] - 1) % len(curso["modulos"])) + 1
        por_modulo.setdefault(destino, []).append(q)

    secciones_html: list[str] = []
    nav_html: list[str] = []
    for modulo in curso["modulos"]:
        numero = modulo["numero"]
        tarjetas = por_modulo.get(numero, [])
        quiz_html = ""
        if tarjetas:
            preguntas_html = []
            for q in tarjetas:
                opciones = "".join(
                    f'<label class="opcion"><input type="radio" name="m{numero}-q{q["numero"]}" '
                    f'value="{o["letra"]}"><span>{o["letra"]}) {_inline(o["texto"])}</span></label>'
                    for o in q["opciones"]
                )
                preguntas_html.append(
                    f'<div class="pregunta" data-correcta="{q["correcta"]}">'
                    f'<p class="enunciado">{_inline(q["pregunta"])}</p>{opciones}'
                    f'<div class="feedback"></div></div>'
                )
            quiz_html = (
                '<div class="quiz"><h4>Autoevaluación</h4>' + "".join(preguntas_html) +
                f'<button class="corregir" type="button">Corregir</button></div>'
            )

        cuerpo = []
        for seccion in modulo["secciones"]:
            clase = ' class="especial"' if seccion.get("tipo") == "especial" else ""
            cuerpo.append(f'<section{clase}><h3>{_inline(seccion["titulo"])}</h3>{seccion["html"]}</section>')

        repaso = ""
        if modulo["preguntas"]:
            items = "".join(f"<li>{_inline(p)}</li>" for p in modulo["preguntas"])
            repaso = f'<section><h3>Preguntas de repaso</h3><ol>{items}</ol></section>'

        defensa_html = ""
        if modulo["defensa"]:
            defensa_html = f'<div class="defensa">“{_inline(modulo["defensa"])}”</div>'

        texto_busqueda = re.sub(r"<[^>]+>", " ", " ".join(s["html"] for s in modulo["secciones"]))
        texto_busqueda = html.unescape(re.sub(r"\s+", " ", texto_busqueda))[:4000]

        secciones_html.append(
            f'<article class="modulo" id="modulo-{numero}" data-numero="{numero}" '
            f'data-busqueda="{html.escape(texto_busqueda, quote=True)}">'
            f'<h2>Módulo {numero}. {_inline(modulo["titulo"])}</h2>'
            + "".join(cuerpo) + repaso + defensa_html +
            f'<div class="acciones-modulo"><button class="marcar" data-numero="{numero}" type="button">'
            f'✔ Marcar como estudiado</button><span class="hecho-badge">Estudiado</span></div>'
            + quiz_html + "</article>"
        )
        nav_html.append(
            f'<a href="#modulo-{numero}" class="enlace-modulo" id="nav-{numero}" data-numero="{numero}">'
            f'<span class="num">{numero:02d}</span><span>{_inline(modulo["titulo"])}</span></a>'
        )

    datos = {
        "modulos": [
            {"numero": m["numero"], "titulo": m["titulo"],
             "textoBusqueda": re.sub(r"<[^>]+>", " ", " ".join(s["html"] for s in m["secciones"]))}
            for m in curso["modulos"]
        ],
        "examen": examen,
        "defensa": defensa,
        "flashcards": [],
    }

    plantilla = """<!DOCTYPE html>
<html lang="es" data-tema="claro">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>__TITULO__</title>
<style>__CSS__</style>
</head>
<body>
<header class="top">
  <h1>__TITULO__</h1>
  <button id="btnMazo" type="button">🃏 Flashcards</button>
  <button id="btnDefensa" type="button">🎤 Modo defensa</button>
  <button class="primario" id="btnExamen" type="button">📝 Examen</button>
  <button type="button" onclick="location.href='../video/index.html'">🎬 Video interactivo</button>
  <button id="btnTema" type="button">🌙 Oscuro</button>
</header>
<div class="layout">
  <aside>
    <input id="buscador" type="search" placeholder="Buscar módulo o tema…" aria-label="Buscar">
    <div class="progreso"><span id="barraProgreso"></span></div>
    <div id="textoProgreso" style="font-size:.85rem;color:var(--suave);margin-bottom:.7rem">0% completado</div>
    <nav>__NAV__</nav>
  </aside>
  <main>
    __INTRO__
    <section class="paneljuego oculto" id="mazo">
      <h2 style="margin-top:0">Flashcards</h2>
      <div class="flashcard" id="flashcard" role="button" tabindex="0"></div>
      <div class="barra">
        <button id="btnAnterior" type="button">← Anterior</button>
        <strong id="contadorMazo"></strong>
        <button id="btnSiguiente" type="button">Siguiente →</button>
      </div>
    </section>
    <section class="paneljuego oculto" id="defensaCaja">
      <h2 style="margin-top:0">Modo defensa</h2>
      <p id="defensaPregunta" style="font-weight:600"></p>
      <button id="btnMostrarDefensa" type="button">Mostrar respuesta</button>
      <p id="defensaRespuesta" class="oculto"></p>
    </section>
    <section class="paneljuego oculto examen" id="examenCaja">
      <h2 style="margin-top:0">Examen de la sección</h2>
      <p style="color:var(--suave)">30 preguntas, una sola opción por pregunta. Al final verás tu puntaje y la corrección.</p>
      <div id="examenPreguntas"></div>
      <div class="barra">
        <button class="primario" id="evaluarExamen" type="button">Evaluar</button>
        <button id="reiniciarExamen" type="button">Reiniciar</button>
        <button type="button" onclick="document.getElementById('examenCaja').classList.add('oculto')">Cerrar</button>
      </div>
      <div class="resultado" id="resultadoExamen"></div>
    </section>
    __MODULOS__
    <footer>Curso generado desde <code>docs/exposicion/fuente/CURSO.md</code>. Progreso guardado en este navegador.</footer>
  </main>
</div>
<script>window.__CURSO__=__DATOS__;</script>
<script>__JS__</script>
</body>
</html>
"""
    intro = ""
    if curso["intro_html"].strip():
        intro = f'<section class="paneljuego">{curso["intro_html"]}</section>'

    html_final = (plantilla
                  .replace("__TITULO__", html.escape(curso["titulo"]))
                  .replace("__CSS__", CSS)
                  .replace("__NAV__", "".join(nav_html))
                  .replace("__INTRO__", intro)
                  .replace("__MODULOS__", "".join(secciones_html))
                  .replace("__DATOS__", json.dumps(datos, ensure_ascii=False))
                  .replace("__JS__", JS))
    return html_final


def main() -> int:
    parser = argparse.ArgumentParser(description="Genera el curso HTML de la exposición.")
    parser.add_argument("--salida", default=str(RAIZ / "curso"), help="Carpeta de salida")
    args = parser.parse_args()

    curso = parse_curso(FUENTE)
    examen = parse_evaluacion(EVALUACION)
    defensa = parse_defensa(DEFENSA)
    glosario = parse_glosario(curso["modulos"])
    tarjetas = glosario + flashcards_de_secciones(curso["modulos"])

    salida = Path(args.salida)
    salida.mkdir(parents=True, exist_ok=True)

    html_base = construir_html(curso, examen, defensa)
    # Las flashcards se inyectan después de calcularlas (evita duplicar lógica en JS).
    html_base = html_base.replace('"flashcards": []',
                                  '"flashcards": ' + json.dumps(tarjetas, ensure_ascii=False))

    (salida / "index.html").write_text(html_base, encoding="utf-8")
    (salida / "index-single.html").write_text(html_base, encoding="utf-8")
    arranque = salida / "start.sh"
    arranque.write_text(
        "#!/usr/bin/env bash\n"
        "cd \"$(dirname \"$0\")\" && open index.html\n",
        encoding="utf-8",
    )
    arranque.chmod(0o755)

    kilobytes = len(html_base.encode("utf-8")) / 1024
    print(f"OK: {salida / 'index.html'} ({kilobytes:.0f} KB)")
    print(f"    {len(curso['modulos'])} módulos · {len(examen)} preguntas de examen · "
          f"{len(tarjetas)} flashcards · {len(defensa)} preguntas de defensa")
    if len(examen) < 30:
        print(f"AVISO: se esperaban 30 preguntas de examen y se encontraron {len(examen)}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
