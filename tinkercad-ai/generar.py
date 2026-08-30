#!/usr/bin/env python3
"""
Generador de modelos 3D (STL) para importar en Tinkercad.

Este script es el "cerebro" que usa la IA para hacer tu trabajo:
tú le pides el diseño en lenguaje natural, la IA escribe/ejecuta
este tipo de código y produce el archivo .STL que importas a Tinkercad.

Uso:
    python3 generar.py --part engranaje --teeth 12 --thickness 8 --hole 10 --out engranaje.stl
    python3 generar.py --part caja --length 60 --width 40 --height 20 --wall 2 --out caja_base.stl
    python3 generar.py --part tapa --length 60 --width 40 --out caja_tapa.stl
"""

import argparse
import math

import numpy as np
from stl import mesh


def _extrude_ring(outer, inner, z0, z1):
    """Construye una extrusión entre dos polígonos (anillo si `inner` no es None).
    outer/inner: listas de (x, y) con la MISMA cantidad de puntos y ángulos alineados.
    Devuelve un stl.mesh.Mesh (paredes + cara superior + cara inferior).
    """
    O = np.array(outer, dtype=float)
    N = len(O)
    tris = []

    def add_quad(a, b, c, d):
        # dos triángulos por cuadrilátero
        tris.append([np.array(a), np.array(b), np.array(c)])
        tris.append([np.array(a), np.array(c), np.array(d)])

    # Pared exterior (normales hacia afuera)
    for i in range(N):
        j = (i + 1) % N
        add_quad(
            (O[i][0], O[i][1], z0), (O[j][0], O[j][1], z0),
            (O[j][0], O[j][1], z1), (O[i][0], O[i][1], z1),
        )

    if inner is not None:
        I = np.array(inner, dtype=float)
        # Pared interior (normales hacia adentro => invertir orden)
        for i in range(N):
            j = (i + 1) % N
            add_quad(
                (I[i][0], I[i][1], z0), (I[i][0], I[i][1], z1),
                (I[j][0], I[j][1], z1), (I[j][0], I[j][1], z0),
            )
        # Cara superior (anillo): pares radiales
        for i in range(N):
            j = (i + 1) % N
            tris.append([(O[i][0], O[i][1], z1), (O[j][0], O[j][1], z1), (I[j][0], I[j][1], z1)])
            tris.append([(O[i][0], O[i][1], z1), (I[j][0], I[j][1], z1), (I[i][0], I[i][1], z1)])
        # Cara inferior (anillo)
        for i in range(N):
            j = (i + 1) % N
            tris.append([(O[i][0], O[i][1], z0), (I[j][0], I[j][1], z0), (O[j][0], O[j][1], z0)])
            tris.append([(O[i][0], O[i][1], z0), (I[i][0], I[i][1], z0), (I[j][0], I[j][1], z0)])
    else:
        # Cara superior: abanico desde el centroide
        c = O.mean(axis=0)
        for i in range(N):
            j = (i + 1) % N
            tris.append([(c[0], c[1], z1), (O[i][0], O[i][1], z1), (O[j][0], O[j][1], z1)])
        # Cara inferior (invertida)
        for i in range(N):
            j = (i + 1) % N
            tris.append([(c[0], c[1], z0), (O[j][0], O[j][1], z0), (O[i][0], O[i][1], z0)])

    m = mesh.Mesh(np.zeros(len(tris), dtype=mesh.Mesh.dtype))
    for k, t in enumerate(tris):
        m.vectors[k] = t
    m.update_normals()
    return m


def _circle_points(radius, count, start=0.0):
    return [
        (radius * math.cos(start + 2 * math.pi * i / count),
         radius * math.sin(start + 2 * math.pi * i / count))
        for i in range(count)
    ]


def engranaje(teeth=12, outer_r=40, thickness=8, hole_r=10):
    """Engranaje tipo sprocket con agujero central."""
    step = 2 * math.pi / teeth
    root_r = outer_r * 0.78
    outer, inner = [], []
    for i in range(teeth):
        a = i * step
        # por diente: valle -> hombro izquierdo -> punta -> hombro derecho
        for ang, r in ((a, root_r),
                       (a + 0.28 * step, outer_r),
                       (a + 0.72 * step, outer_r)):
            outer.append((math.cos(ang) * r, math.sin(ang) * r))
            inner.append((math.cos(ang) * hole_r, math.sin(ang) * hole_r))
    return _extrude_ring(outer, inner, 0, thickness)


def _rect_points(lx, ly, inward=0.0):
    """Rectángulo centrado: 8 puntos (4 esquinas + 4 medios de lado)."""
    x, y = lx / 2 - inward, ly / 2 - inward
    return [
        (-x, -y), (0, -y), (x, -y), (x, 0),
        (x, y), (0, y), (-x, y), (-x, 0),
    ]


def caja(length=60, width=40, height=20, wall=2):
    """Caja hueca abierta por arriba (para 3D printing)."""
    outer = _rect_points(length, width)
    inner = _rect_points(length, width, inward=wall)
    return _extrude_ring(outer, inner, 0, height)


def tapa(length=60, width=40, thickness=3, lip=0.8):
    """Tapa sólida un poco más grande que la caja."""
    outer = _rect_points(length + lip, width + lip)
    return _extrude_ring(outer, None, 0, thickness)


def main():
    ap = argparse.ArgumentParser(description="Genera STL para Tinkercad")
    ap.add_argument("--part", required=True, choices=["engranaje", "caja", "tapa"])
    ap.add_argument("--teeth", type=int, default=12)
    ap.add_argument("--thickness", type=float, default=8)
    ap.add_argument("--hole", type=float, default=10)
    ap.add_argument("--outer-r", type=float, default=40)
    ap.add_argument("--length", type=float, default=60)
    ap.add_argument("--width", type=float, default=40)
    ap.add_argument("--height", type=float, default=20)
    ap.add_argument("--wall", type=float, default=2)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    if args.part == "engranaje":
        m = engranaje(teeth=args.teeth, outer_r=args.outer_r,
                      thickness=args.thickness, hole_r=args.hole)
    elif args.part == "caja":
        m = caja(length=args.length, width=args.width,
                 height=args.height, wall=args.wall)
    else:
        m = tapa(length=args.length, width=args.width)

    m.save(args.out)
    n = len(m.vectors)
    print(f"OK -> {args.out}  ({n} triángulos)")


if __name__ == "__main__":
    main()
