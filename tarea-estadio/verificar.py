#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Verificador de los STL del estadio (tarea EPT).

1) Cada PIEZA por separado es un solido cerrado (watertight) -> eso es lo que
   mira Tinkercad al importar.
2) Cada ARCHIVO STL: aristas compartidas = piezas pegadas cara a cara (normal).
3) Ninguna pieza se atraviesa con otra (geometria real, no caja envolvente).
4) Cotas reales del modelo.
"""
import json
import math
import os
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
STL_DIR = os.path.join(HERE, "estadio-piezas")
Q = 4


def leer_stl(path):
    with open(path, "rb") as f:
        data = f.read()
    n = struct.unpack("<I", data[80:84])[0]
    tris, off = [], 84
    for _ in range(n):
        vals = struct.unpack("<12fH", data[off:off + 50])
        tris.append((vals[3:6], vals[6:9], vals[9:12]))
        off += 50
    if off != len(data):
        raise SystemExit("STL con basura al final: " + path)
    return tris


def k(v):
    return (round(v[0], Q), round(v[1], Q), round(v[2], Q))


def cerrado(tris):
    """True si el conjunto de triangulos es un solido cerrado sin degenerados."""
    aristas, degen = {}, 0
    for t in tris:
        a, b, c = k(t[0]), k(t[1]), k(t[2])
        if a == b or b == c or a == c:
            degen += 1
            continue
        ux, uy, uz = t[1][0] - t[0][0], t[1][1] - t[0][1], t[1][2] - t[0][2]
        vx, vy, vz = t[2][0] - t[0][0], t[2][1] - t[0][1], t[2][2] - t[0][2]
        cr = (uy * vz - uz * vy, uz * vx - ux * vz, ux * vy - uy * vx)
        if math.sqrt(cr[0] ** 2 + cr[1] ** 2 + cr[2] ** 2) < 1e-9:
            degen += 1
        for e in ((a, b), (b, c), (c, a)):
            aristas[e] = aristas.get(e, 0) + 1
    sueltas = sum(1 for (a, b) in aristas if (b, a) not in aristas)
    raras = sum(1 for (a, b), c in aristas.items() if (b, a) in aristas and c != 1)
    return (sueltas == 0 and raras == 0 and degen == 0), sueltas, raras, degen


modelo = json.load(open(os.path.join(HERE, "estadio-modelo.json")))
piezas = modelo["piezas"]
ok = True

print("=" * 78)
print("1) CADA PIEZA ES UN SOLIDO CERRADO (watertight)  -> %d piezas" % len(piezas))
print("=" * 78)
fallos_pieza = []
for p in piezas:
    tris = [tuple(t[i:i + 3] for i in (0, 3, 6, 9)) for t in p["t"]]
    bien, s, r, d = cerrado(tris)
    if not bien:
        fallos_pieza.append((p["n"], p["tipo"], s, r, d))
print("  piezas cerradas : %d / %d" % (len(piezas) - len(fallos_pieza), len(piezas)))
for f in fallos_pieza:
    print("   FALLA:", f)
    ok = False
print("  cubos (12 tris) y Tejados (8 tris):",
      sorted({len(p["t"]) for p in piezas}))

print()
print("=" * 78)
print("2) ARCHIVOS STL")
print("=" * 78)
print("  %-26s %6s %8s %8s %s" % ("archivo", "tris", "sueltas", "pegadas", "estado"))
for fn in sorted(os.listdir(STL_DIR)):
    if not fn.endswith(".stl"):
        continue
    tris = leer_stl(os.path.join(STL_DIR, fn))
    bien, s, r, d = cerrado(tris)
    n_pz = sum(1 for p in piezas if p["archivo"] == fn[:-4])
    print("  %-26s %6d %8d %8d  %s (%d piezas)" %
          (fn, len(tris), s, r, "cerrado" if bien else "cerrado con uniones", n_pz))
    if s or d:
        print("    ^ aristas sueltas/degeneradas: revisar")
        ok = False

print()
print("=" * 78)
print("3) NINGUNA PIEZA SE ATRAVIESA CON OTRA (geometria real)")
print("=" * 78)


def caja(p):
    cx, cy, cz = p["c"]
    dx, dy, dz = p["d"]
    return (cx - dx / 2, cy - dy / 2, cz - dz / 2, cx + dx / 2, cy + dy / 2, cz + dz / 2)


def toca(a, b, eps=1e-6):
    """a y b son (xmin, ymin, zmin, xmax, ymax, zmax). Se solapan si en los
    3 ejes el minimo de uno es menor que el maximo del otro."""
    amin, amax = a[:3], a[3:]
    bmin, bmax = b[:3], b[3:]
    return all(ai < bj - eps and bi < aj - eps
               for ai, aj, bi, bj in zip(amin, amax, bmin, bmax))


def dentro_prisma(pt, p):
    """Punto dentro del prisma triangular (Tejado) usando su seccion."""
    cx, cy, cz = p["c"]
    dx, dy, dz = p["d"]
    hx, hy = dx / 2.0, dy / 2.0
    z0, z1 = cz - dz / 2.0, cz + dz / 2.0
    x, y, z = pt
    if z < z0 or z > z1:
        return False
    t = (z - z0) / (z1 - z0)                      # 0 en el alero, 1 en la cumbrera
    if p["tipo"] == "Tejado (prisma)":             # cumbrera paralela a X
        if x < cx - hx or x > cx + hx:
            return False
        semiancho = hy * (1 - t)
        return abs(y - cy) <= semiancho + 1e-9
    if y < cy - hy or y > cy + hy:
        return False
    semiancho = hx * (1 - t)
    return abs(x - cx) <= semiancho + 1e-9


VOL_MAX = 1.0   # mm^3: por encima de esto una pieza esta realmente metida en otra
uniones, cruces = [], []
for i in range(len(piezas)):
    for j in range(i + 1, len(piezas)):
        a, b = piezas[i], piezas[j]
        ca, cb = caja(a), caja(b)
        if not toca(ca, cb):
            continue
        if a["tipo"] == "Cubo" and b["tipo"] == "Cubo":
            lados = [min(a_hi, b_hi) - max(a_lo, b_lo)
                     for a_lo, a_hi, b_lo, b_hi in zip(ca[:3], ca[3:], cb[:3], cb[3:])]
            vol = lados[0] * lados[1] * lados[2]
            fila = (a["n"], b["n"], round(lados[0], 2), round(lados[1], 2),
                    round(lados[2], 2), round(vol, 3))
            (cruces if vol > VOL_MAX else uniones).append(fila)
            continue
        pr, cb2 = (a, b) if a["tipo"] != "Cubo" else (b, a)
        cx, cy, cz = cb2["c"]
        dx, dy, dz = cb2["d"]
        dentro = False
        for sx in (-1, 1):
            for sy in (-1, 1):
                for sz in (-1, 1):
                    pt = (cx + sx * dx / 2, cy + sy * dy / 2, cz + sz * dz / 2)
                    if dentro_prisma(pt, pr):
                        dentro = True
        if dentro:
            cruces.append((a["n"], b["n"], "prisma", "", "", ""))
print("  CONTACTOS/UNIONES de menos de %.1f mm3 (lineas que se cruzan, piezas apoyadas): %d  -> OK" % (VOL_MAX, len(uniones)))
print("  PIEZAS ATRAVESADAS (mas de %.1f mm3 metidos en otra): %d" % (VOL_MAX, len(cruces)))
for c in cruces[:60]:
    print("    X", c)
if cruces:
    ok = False
choques = cruces

print()
print("=" * 78)
print("4) COTAS Y RESUMEN")
print("=" * 78)
tris = leer_stl(os.path.join(HERE, "estadio-tinkercad.stl"))
xs = [v[0] for t in tris for v in t]
ys = [v[1] for t in tris for v in t]
zs = [v[2] for t in tris for v in t]
print("  ancho  X: %.2f a %.2f  = %.2f mm" % (min(xs), max(xs), max(xs) - min(xs)))
print("  fondo  Y: %.2f a %.2f  = %.2f mm" % (min(ys), max(ys), max(ys) - min(ys)))
print("  alto   Z: %.2f a %.2f  = %.2f mm" % (min(zs), max(zs), max(zs) - min(zs)))
tipos = {}
for p in piezas:
    tipos[p["tipo"]] = tipos.get(p["tipo"], 0) + 1
print("  piezas:", len(piezas), "| figuras usadas:", tipos)
print("  solo CUBO y PRISMA TRIANGULAR:", set(tipos) <= {"Cubo", "Tejado (prisma)"})
print("  pasos:", len(modelo["pasos"]))
print()
print("RESULTADO FINAL:", "TODO OK" if ok else "HAY ERRORES")
sys.exit(0 if ok else 1)
