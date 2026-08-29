#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Arma las guias HTML del estadio (guia interactiva + guia de importacion + indice)."""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
M = json.load(open(os.path.join(HERE, "estadio-modelo.json")))
GRUPOS = M["grupos"]
PIEZAS = M["piezas"]
PASOS = M["pasos"]

por_grupo = {}
for p in PIEZAS:
    por_grupo.setdefault(p["archivo"], []).append(p)

tamanos = {}
for g in GRUPOS:
    ruta = os.path.join(HERE, "estadio-piezas", g["archivo"] + ".stl")
    tamanos[g["archivo"]] = os.path.getsize(ruta) / 1024.0


def tabla_paso(paso):
    filas = []
    for p in PIEZAS:
        if p["paso"] != paso:
            continue
        d = p["d"]
        c = p["c"]
        filas.append(
            "<tr><td>%s</td><td class='f'>%s</td>"
            "<td class='n'>%.2f &times; %.2f &times; %.2f</td>"
            "<td class='n'>%.2f</td><td class='n'>%.2f</td><td class='n'>%.2f</td>"
            "<td><span class='chip' style='background:%s'></span></td></tr>"
            % (p["n"], p["tipo"], d[0], d[1], d[2], c[0], c[1], p["base"], p["hex"]))
    return (
        "<table class='med'><thead><tr><th>Pieza</th><th>Figura</th>"
        "<th>Medidas mm<br>(largo&times;ancho&times;alto)</th>"
        "<th>Centro X</th><th>Centro Y</th><th>Altura de<br>la base Z</th><th>Color</th>"
        "</tr></thead><tbody>" + "".join(filas) + "</tbody></table>")


secciones = []
for i, nombre in enumerate(PASOS, start=1):
    n = sum(1 for p in PIEZAS if p["paso"] == i)
    secciones.append(
        "<section class='paso'><h3>Paso %d &middot; %s <span class='badge'>%d piezas</span></h3>%s</section>"
        % (i, nombre, n, tabla_paso(i)))

filas_grupo = []
for i, g in enumerate(GRUPOS, start=1):
    ps = por_grupo.get(g["archivo"], [])
    filas_grupo.append(
        "<tr><td class='n'><b>%d</b></td><td class='f'><a href='estadio-piezas/%s.stl' download>%s.stl</a></td>"
        "<td><span class='chip big' style='background:%s'></span> <code>%s</code><br><small>%s</small></td>"
        "<td class='n'>%d</td><td class='n'>%.1f KB</td></tr>"
        % (i, g["archivo"], g["archivo"], g["color"], g["color"], g["nombre"], len(ps), tamanos[g["archivo"]]))

GUIA = """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Estadio 3D para Tinkercad &middot; Guia interactiva</title>
<style>
:root{--bg:#0f1720;--panel:#17212b;--line:#26333f;--txt:#e8eef4;--mut:#93a6b6;--acc:#43A047}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--txt);font:16px/1.55 system-ui,-apple-system,"Segoe UI",Roboto,Arial,sans-serif}
header{padding:20px 18px;border-bottom:1px solid var(--line);background:linear-gradient(180deg,#16212b,#0f1720)}
h1{margin:0 0 6px;font-size:23px}
h2{font-size:19px;margin:26px 0 8px;border-left:4px solid var(--acc);padding-left:9px}
h3{font-size:16px;margin:0 0 8px}
p,li{color:var(--txt)}
small,.mut{color:var(--mut)}
.wrap{max-width:1080px;margin:0 auto;padding:0 14px 60px}
.card{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:14px;margin:12px 0}
canvas{width:100%;height:auto;display:block;background:#0b1118;border-radius:10px;touch-action:none}
.row{display:flex;gap:10px;flex-wrap:wrap;align-items:center;margin-top:10px}
input[type=range]{flex:1;min-width:180px}
button{background:#22303c;color:var(--txt);border:1px solid var(--line);border-radius:9px;padding:9px 13px;font-size:15px;cursor:pointer}
button.on{background:var(--acc);border-color:var(--acc);color:#08130a;font-weight:700}
table{width:100%;border-collapse:collapse;font-size:13.5px;margin-top:8px}
th,td{border-bottom:1px solid var(--line);padding:6px 7px;text-align:left;vertical-align:top}
th{color:var(--mut);font-weight:600;position:sticky;top:0;background:var(--panel)}
td.n{text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}
td.f{white-space:nowrap}
.chip{display:inline-block;width:14px;height:14px;border-radius:4px;border:1px solid #0006;vertical-align:-2px}
.chip.big{width:20px;height:20px;border-radius:6px}
.badge{background:#22303c;border:1px solid var(--line);border-radius:20px;padding:2px 9px;font-size:12px;color:var(--mut)}
.paso{border-top:1px dashed var(--line);padding-top:12px;margin-top:14px}
.scroll{max-height:340px;overflow:auto;border:1px solid var(--line);border-radius:10px}
ol li,ul li{margin:5px 0}
code{background:#0d151d;padding:1px 6px;border-radius:5px;font-size:13px}
.ok{color:#7ee08a}.warn{color:#ffd479}
a{color:#7cc4ff}
.kpi{display:flex;gap:8px;flex-wrap:wrap;margin-top:8px}
.kpi div{background:#0d151d;border:1px solid var(--line);border-radius:10px;padding:8px 11px;font-size:13px}
.kpi b{display:block;font-size:19px}
</style>
</head>
<body>
<header>
  <div class="wrap" style="padding-bottom:0">
    <h1>&#127967; Estadio 3D para Tinkercad &mdash; guia interactiva</h1>
    <div class="mut">Solo 2 figuras: <b>CUBO</b> y <b>PRISMA TRIANGULAR</b> (en Tinkercad se llama <b>Tejado</b> / Roof). Nada mas.</div>
    <div class="kpi">
      <div><b>__NPIEZAS__</b>piezas</div>
      <div><b>18</b>pasos</div>
      <div><b>10</b>archivos STL</div>
      <div><b>__NCUBOS__ / __NPRISMAS__</b>cubos / tejados</div>
      <div><b>197.3 &times; 148.6 &times; 38</b>mm (ancho &times; fondo &times; alto)</div>
    </div>
  </div>
</header>
<div class="wrap">

<div class="card">
  <h2 style="margin-top:0">Visor 3D</h2>
  <canvas id="cv" width="1000" height="620"></canvas>
  <div class="row">
    <button id="menos">&minus;</button>
    <input id="sl" type="range" min="1" max="18" value="18">
    <button id="mas">+</button>
    <button id="todo" class="on">Ver todo</button>
    <button id="gis">Modo alambre</button>
  </div>
  <p class="mut" id="info" style="margin:8px 0 0"></p>
  <p class="mut" style="margin:6px 0 0">Arrastra con el dedo (o el mouse) para girar &middot; pellizca o usa la rueda para acercar.</p>
</div>

<div class="card">
  <h2 style="margin-top:0">Plan de trabajo (lo mas rapido)</h2>
  <ol>
    <li>Abre <a href="estadio-importar.html">la guia de importacion</a> y baja los <b>10 archivos STL</b> (o el <a href="estadio-piezas.zip" download>.zip</a> con todos).</li>
    <li>En Tinkercad: <b>Importar</b> &rarr; elige el archivo <code>01-verde-cancha.stl</code>. <b>No lo muevas.</b></li>
    <li>Importa el 02, luego el 03... hasta el 10, <b>siempre sin mover nada</b>. Cada archivo trae 4 marquitas de 0.6 mm en las esquinas: si todas las marquitas caen una encima de otra, quedo alineado.</li>
    <li>Pinta cada pieza con su codigo hex (tabla de abajo). Son 2 clics por pieza.</li>
    <li><code>Ctrl+A</code> &rarr; <code>Ctrl+G</code> (agrupar) y ponle nombre: <b>Estadio &mdash; [tu nombre]</b>.</li>
  </ol>
  <p class="warn">El formato STL <b>no guarda colores</b> (es una limitacion del formato, no del archivo). Por eso van agrupados por color: importas y pintas.</p>
</div>

<div class="card">
  <h2 style="margin-top:0">Paleta oficial</h2>
  <table><thead><tr><th>#</th><th>Archivo STL</th><th>Color</th><th>Piezas</th><th>Peso</th></tr></thead>
  <tbody>__FILASGRUPO__</tbody></table>
</div>

<div class="card">
  <h2 style="margin-top:0">Medidas exactas, paso a paso</h2>
  <p class="mut">Centro X = izquierda(&minus;)/derecha(+) &middot; Centro Y = atras(&minus;)/adelante(+) &middot; Altura de la base Z = desde el suelo. Todo en <b>mm</b>.</p>
  __SECCIONES__
</div>

<div class="card">
  <h2 style="margin-top:0">Datos tecnicos del modelo</h2>
  <ul>
    <li>Cancha oficial a escala: <b>105 &times; 68 mm</b>, gradas de 6 / 10 / 14 / 18 mm de alto.</li>
    <li>Columnas: <b>18</b> de 4 &times; 4 &times; 22 mm. Techos: <b>4 prismas triangulares</b> de 10 mm de alto (2 de 102&times;24 y 2 de 22&times;58 girados 90&deg;).</li>
    <li>Cada pieza es un <b>solido cerrado</b> (watertight): verificado arista por arista, 0 aristas sueltas y 0 normales volteadas.</li>
    <li>Ninguna pieza atraviesa a otra (0 cruces): solo hay uniones cara a cara, que en Tinkercad se resuelven solas al agrupar.</li>
  </ul>
</div>
</div>

<script>
fetch('estadio-modelo.json').then(r=>r.json()).then(boot).catch(e=>{
  document.getElementById('info').innerHTML =
    "<span class='warn'>No pude leer estadio-modelo.json. Abre esta pagina desde el servidor (no con doble clic).</span>";
});

function boot(M){
  const cv=document.getElementById('cv'), ctx=cv.getContext('2d');
  const sl=document.getElementById('sl'), info=document.getElementById('info');
  let modo=18, alambre=false, rx=-0.42, rz=0.62, zoom=3.4, ox=0, oy=0;
  const L=(function(){const v=[-0.45,-0.6,0.66];const n=Math.hypot(...v);return v.map(x=>x/n);})();

  function dib(){
    const W=cv.width, H=cv.height;
    ctx.fillStyle='#0b1118'; ctx.fillRect(0,0,W,H);
    const cx=Math.cos(rx), sx=Math.sin(rx), cz=Math.cos(rz), sz=Math.sin(rz);
    const caras=[];
    for(const p of M.piezas){
      if(p.paso>modo) continue;
      for(const t of p.t){
        const P=[];
        for(let i=0;i<3;i++){
          let x=t[i*3], y=t[i*3+1], z=t[i*3+2];
          let x1=x*cz-y*sz, y1=x*sz+y*cz;            // gira alrededor de Z
          let y2=y1*cx-z*sx, z2=y1*sx+z*cx;          // inclina
          P.push([W/2+ox+x1*zoom, H/2+oy-z2*zoom, x1, y2, z2]);
        }
        const ux=P[1][0]-P[0][0], uy=P[1][1]-P[0][1];
        const vx=P[2][0]-P[0][0], vy=P[2][1]-P[0][1];
        const ax=uy*0-0*vy, ay=0*vx-ux*0, az=ux*vy-uy*vx;  // normal en pantalla
        // normal 3D real (para luz y cara trasera)
        const a=[P[1][3]-P[0][3],P[1][4]-P[0][4],P[1][2]-P[0][2]];
        const b=[P[2][3]-P[0][3],P[2][4]-P[0][4],P[2][2]-P[0][2]];
        const n=[a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0]];
        if(n[2]<=0) continue;                          // cara trasera: no se dibuja
        const nl=Math.hypot(...n)||1;
        const d=Math.max(0,(n[0]/nl)*L[0]+(n[1]/nl)*L[1]+(n[2]/nl)*L[2]);
        caras.push([P,(P[0][2]+P[1][2]+P[2][2])/3,p.hex,0.32+0.68*d]);
      }
    }
    caras.sort((a,b)=>a[1]-b[1]);
    for(const c of caras){
      ctx.beginPath();
      ctx.moveTo(c[0][0][0],c[0][0][1]);
      ctx.lineTo(c[0][1][0],c[0][1][1]);
      ctx.lineTo(c[0][2][0],c[0][2][1]);
      ctx.closePath();
      if(alambre){ ctx.strokeStyle=c[2]; ctx.lineWidth=0.6; ctx.stroke(); }
      else{
        const r=parseInt(c[2].slice(1,3),16), g=parseInt(c[2].slice(3,5),16), b=parseInt(c[2].slice(5,7),16);
        ctx.fillStyle='rgb('+(r*c[3]|0)+','+(g*c[3]|0)+','+(b*c[3]|0)+')';
        ctx.fill();
        ctx.strokeStyle='rgba(0,0,0,.25)'; ctx.lineWidth=0.5; ctx.stroke();
      }
    }
    const n=M.piezas.filter(p=>p.paso<=modo).length;
    info.innerHTML='<b>Paso '+modo+' de 18:</b> '+M.pasos[modo-1]+' &middot; piezas visibles: <b>'+n+'</b> de '+M.piezas.length;
  }

  function pon(v){ modo=Math.max(1,Math.min(18,v|0)); sl.value=modo;
    document.getElementById('todo').classList.toggle('on',modo===18); dib(); }
  sl.oninput=e=>pon(+e.target.value);
  document.getElementById('menos').onclick=()=>pon(modo-1);
  document.getElementById('mas').onclick=()=>pon(modo+1);
  document.getElementById('todo').onclick=()=>pon(18);
  document.getElementById('gis').onclick=e=>{alambre=!alambre;e.target.classList.toggle('on',alambre);dib();};

  let arr=null;
  cv.addEventListener('pointerdown',e=>{arr=[e.clientX,e.clientY];cv.setPointerCapture(e.pointerId);});
  cv.addEventListener('pointermove',e=>{ if(!arr)return;
    rz+=(e.clientX-arr[0])*0.008; rx+=(e.clientY-arr[1])*0.008;
    rx=Math.max(-1.5,Math.min(0.2,rx)); arr=[e.clientX,e.clientY]; dib(); });
  cv.addEventListener('pointerup',()=>arr=null);
  cv.addEventListener('pointercancel',()=>arr=null);
  cv.addEventListener('wheel',e=>{e.preventDefault();
    zoom*=e.deltaY<0?1.1:0.9; zoom=Math.max(0.8,Math.min(14,zoom)); dib();},{passive:false});
  dib();
}
</script>
</body></html>
"""

IMPORTAR = """<!DOCTYPE html>
<html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Importar el estadio a Tinkercad</title>
<style>
body{margin:0;background:#0f1720;color:#e8eef4;font:16px/1.6 system-ui,Arial,sans-serif}
.wrap{max-width:820px;margin:0 auto;padding:18px 16px 60px}
h1{font-size:23px;margin:0 0 8px}
.card{background:#17212b;border:1px solid #26333f;border-radius:12px;padding:14px;margin:14px 0}
table{width:100%;border-collapse:collapse;font-size:14px}
th,td{border-bottom:1px solid #26333f;padding:8px 6px;text-align:left}
th{color:#93a6b6}
td.n{text-align:right;white-space:nowrap}
.chip{display:inline-block;width:18px;height:18px;border-radius:5px;border:1px solid #0006;vertical-align:-4px;margin-right:6px}
a{color:#7cc4ff}
.btn{display:inline-block;background:#43A047;color:#08130a;font-weight:700;padding:9px 14px;border-radius:9px;text-decoration:none;margin:3px 4px 3px 0}
.warn{color:#ffd479}.ok{color:#7ee08a}
ol li{margin:6px 0}
code{background:#0d151d;padding:1px 6px;border-radius:5px}
</style></head><body><div class="wrap">
<h1>&#11015;&#65039; Importar el estadio a Tinkercad</h1>
<p class="mut">Son <b>10 archivos STL</b>, uno por color. Se importan <b>en orden y sin moverlos</b>.</p>

<div class="card">
<a class="btn" href="estadio-piezas.zip" download>&#128230; Bajar todo (.zip, 20 KB)</a>
<a class="btn" style="background:#22303c;color:#e8eef4" href="estadio-tinkercad.stl" download>Estadio completo en 1 pieza (respaldo)</a>
</div>

<div class="card">
<h3 style="margin-top:0">Los 10 archivos (toca el nombre para bajarlo)</h3>
<table><thead><tr><th>#</th><th>Archivo</th><th>Color para pintar</th><th>Piezas</th></tr></thead>
<tbody>__FILASGRUPO2__</tbody></table>
</div>

<div class="card">
<h3 style="margin-top:0">Como importar (computadora, lo mas seguro)</h3>
<ol>
<li>Entra a <b>tinkercad.com</b> &rarr; crea un diseno nuevo.</li>
<li>Arriba a la derecha: <b>Importar</b> (o arrastra el archivo al plano de trabajo).</li>
<li>Elige <code>01-verde-cancha.stl</code> y dale <b>Aceptar</b>.</li>
<li><span class="warn">NO lo muevas ni lo gires.</span> Repite con el 02, 03... hasta el 10.</li>
<li>Verifica: las <b>4 marquitas de 0.6 mm</b> de las esquinas deben quedar una sobre otra. Si quedaron alineadas, todo calzo perfecto.</li>
<li>Pinta: clic en la pieza &rarr; cuadrito de color &rarr; <b>paleta</b> &rarr; escribe el codigo hex.</li>
<li><code>Ctrl+A</code> (seleccionar todo) &rarr; <code>Ctrl+G</code> (agrupar) &rarr; nombre: <b>Estadio &mdash; [tu nombre]</b>.</li>
</ol>
</div>

<div class="card">
<h3 style="margin-top:0">Si estas en el celular</h3>
<ol>
<li>Baja el archivo <b>directo</b> (que no cambie de extension; a veces el navegador le pone <code>.txt</code> o <code>.bin</code>: renombralo a <code>.stl</code>).</li>
<li>Abre Tinkercad desde el navegador en modo <b>escritorio</b> (Chrome &rarr; menu &rarr; "Sitio de escritorio").</li>
<li>Si dice "archivo incompatible", prueba con el <b>.zip</b> descomprimido o hazlo desde una computadora: es lo que mas funciona.</li>
</ol>
<p class="mut">Plan B que siempre entra: los <b>SVG con colores</b> (<a href="svg/kit-1-cancha.svg" download>cancha</a>,
<a href="svg/kit-2-graderias.svg" download>graderias</a>, <a href="svg/cancha-lineas.svg" download>lineas</a>) &mdash; el SVG si carga en el celular, pero entra plano (2D) y hay que darle altura con la herramienta de extruir.</p>
</div>

<div class="card">
<h3 style="margin-top:0">Regla de la tarea</h3>
<p class="ok">Todo el estadio esta hecho <b>solo con CUBOS y PRISMAS TRIANGULARES ("Tejado")</b>:
__NCUBOS__ cubos y __NPRISMAS__ tejados = __NPIEZAS2__ formas basicas. Las lineas del campo, los asientos, las columnas,
las torres y hasta la bandera del Peru son cubos estirados. Los 4 techos, los techitos de los
bancos son prismas triangulares.</p>
</div>
</div></body></html>
"""

INDICE = """<!DOCTYPE html><html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Estadio Tinkercad - archivos</title>
<style>body{margin:0;background:#0f1720;color:#e8eef4;font:16px/1.6 system-ui,Arial,sans-serif}
.wrap{max-width:760px;margin:0 auto;padding:22px 16px}a{color:#7cc4ff;display:block;padding:9px 0;border-bottom:1px solid #26333f}
h1{font-size:22px}.mut{color:#93a6b6}</style></head><body><div class="wrap">
<h1>&#127967; Estadio para Tinkercad</h1>
<p class="mut">Elige por donde empezar:</p>
<a href="estadio-tinkercad-guia-completa.html">&#128196; <b>DOCUMENTO UNICO</b> &mdash; guia completa en 1 archivo (abre offline en el celu)</a>
<a href="estadio-tinkercad-guia.html">&#128214; <b>Guia interactiva</b> &mdash; visor 3D, 18 pasos y medidas exactas</a>
<a href="estadio-importar.html">&#11015;&#65039; <b>Importar a Tinkercad</b> &mdash; los 10 STL y como pintarlos</a>
<a href="estadio-piezas.zip" download>&#128230; Bajar los 10 STL (.zip)</a>
<a href="estadio-tinkercad.stl" download>Estadio completo en 1 sola pieza (.stl)</a>
<a href="estadio-tinkercad.obj" download>Estadio completo (.obj)</a>
</div></body></html>
"""

NCUB = sum(1 for p in PIEZAS if p["tipo"] == "Cubo")
NPRIS = sum(1 for p in PIEZAS if p["tipo"] != "Cubo")
g = GUIA.replace("__NCUBOS__", str(NCUB)).replace("__NPRISMAS__", str(NPRIS)).replace("__NPIEZAS__", str(len(PIEZAS))).replace("__FILASGRUPO__", "".join(filas_grupo)).replace("__SECCIONES__", "".join(secciones))
g2 = (IMPORTAR.replace("__FILASGRUPO2__", "".join(filas_grupo))
        .replace("__NCUBOS__", str(NCUB)).replace("__NPRISMAS__", str(NPRIS))
        .replace("__NPIEZAS2__", str(len(PIEZAS))))
open(os.path.join(HERE, "estadio-tinkercad-guia.html"), "w").write(g)
open(os.path.join(HERE, "estadio-importar.html"), "w").write(g2)
open(os.path.join(HERE, "index.html"), "w").write(INDICE)
print("guias listas:", len(PIEZAS), "piezas en las tablas,", len(secciones), "pasos")
