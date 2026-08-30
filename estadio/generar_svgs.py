#!/usr/bin/env python3
"""Genera los kits SVG del estadio (vistas superiores con colores).

- kit-1-cancha.svg      → cancha con franjas de césped (2 verdes) + líneas
- kit-2-graderias.svg   → tribunas con gradas y filas de asientos
- cancha-lineas.svg     → solo las líneas blancas (para importar encima)

Escala: 5 px por mm. Centro del estadio en (250, 160). Y invertido.
"""
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
S = 5.0
CX, CY = 250, 160


def x(mm): return CX + mm * S
def y(mm): return CY - mm * S


def rect(x0, y0, x1, y1, fill, stroke=None, sw=1, rx=0):
    r = f'<rect x="{x(x0):.1f}" y="{y(y1):.1f}" width="{(x1-x0)*S:.1f}" height="{(y1-y0)*S:.1f}"'
    r += f' fill="{fill}"'
    if stroke:
        r += f' stroke="{stroke}" stroke-width="{sw}"'
    if rx:
        r += f' rx="{rx}"'
    return r + '/>'


def poly_ring(cx, cy, r, n, fill, stroke=None, sw=1):
    pts = ' '.join(f"{x(cx + r*math.cos(2*math.pi*i/n)):.1f},{y(cy + r*math.sin(2*math.pi*i/n)):.1f}"
                   for i in range(n))
    p = f'<polygon points="{pts}" fill="{fill}"'
    if stroke:
        p += f' stroke="{stroke}" stroke-width="{sw}"'
    return p + '/>'


def header(w=500, h=320, bg=None):
    b = f'<rect x="0" y="0" width="{w}" height="{h}" fill="{bg}"/>' if bg else ''
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
            f'width="{w}" height="{h}">{b}')


# ---------------------------------------------------------------- cancha
def kit_1():
    parts = [header(bg="#2E7D32")]
    # base
    parts.append(rect(-50, -32, 50, 32, "#43A047"))
    # franjas oscuras
    for i in range(1, 10, 2):
        parts.append(rect(-50 + 10 * i, -32, -50 + 10 * (i + 1), 32, "#388E3C"))
    # líneas blancas
    W = "#FFFFFF"
    # borde
    parts.append(rect(-49.2, -31.2, 49.2, 31.2, "none", W, 3))
    # medio campo
    parts.append(rect(-0.5, -31.2, 0.5, 31.2, W))
    # círculo central (polígono de 36 lados)
    parts.append(poly_ring(0, 0, 8.5, 36, "none", W, 3))
    # áreas penales y metas
    for sx in (1, -1):
        parts.append(rect(sx * 34.3, -19.2, sx * 35.1, 19.2, "none", W, 3))
        parts.append(rect(sx * 35.1, -20, sx * 49.2, 20, "none", W, 3))
        parts.append(rect(sx * 44.8, -11.5, sx * 45.6, 11.5, "none", W, 3))
        parts.append(rect(sx * 45.6, -12.3, sx * 49.2, 12.3, "none", W, 3))
        parts.append(rect(sx * 38.7, -0.5, sx * 39.7, 0.5, W))
    # porterías
    for sx in (1, -1):
        parts.append(rect(sx * 50 - (0.2 if sx > 0 else 0), -3.6, sx * 50 + (0.2 if sx > 0 else 0), 3.6, "none", W, 4))
    return ''.join(parts) + '</svg>'


# ------------------------------------------------------------ graderías
def kit_2():
    parts = [header(bg="#37474F")]
    # tribunas (vista superior): Norte/Sur en Y, Este/Oeste en X
    G = "#90A4AE"
    parts.append(rect(-50, 36, 50, 74, G))
    parts.append(rect(-50, -74, 50, -36, G))
    parts.append(rect(54, -32, 97, 32, G))
    parts.append(rect(-97, -32, -54, 32, G))
    # escalones (tono más claro)
    L = "#B0BEC5"
    for b0, b1 in [(45.5, 55), (55, 64.5), (64.5, 74)]:
        parts.append(rect(-50, b0, 50, b1, L))
        parts.append(rect(-50, -b1, 50, -b0, L))
    for b0, b1 in [(64.75, 75.5), (75.5, 86.25), (86.25, 97)]:
        parts.append(rect(b0, -32, b1, 32, L))
        parts.append(rect(-b1, -32, -b0, 32, L))
    # filas de asientos (rojo/azul, en el borde de cada escalón)
    R, B = "#E53935", "#1E88E5"
    bs_ns = [36, 45.5, 55, 64.5]
    hs = [6, 10, 14, 18]
    for t, b in enumerate(bs_ns):
        c = R if t % 2 == 0 else B
        parts.append(rect(-50, b - 0.5, 50, b, c))
        parts.append(rect(-50, -b, 50, -b + 0.5, c))
    for t, b in enumerate([54, 64.75, 75.5, 86.25]):
        c = R if t % 2 == 0 else B
        parts.append(rect(b - 0.5, -32, b, 32, c))
        parts.append(rect(-b, -32, -b + 0.5, 32, c))
    # columnas
    C = "#546E7A"
    for xc in (-60, -36, -12, 12, 36, 60):
        for yc in (72, -72):
            parts.append(rect(xc - 2, yc - 2, xc + 2, yc + 2, C))
    for yc in (-24, 0, 24):
        for xc in (93, -93):
            parts.append(rect(xc - 2, yc - 2, xc + 2, yc + 2, C))
    # techos (silueta plateada)
    T = "#CFD8DC"
    parts.append(rect(51, -49, 97, 49, "none", T, 2))
    parts.append(rect(-97, -49, -51, 49, "none", T, 2))
    parts.append(rect(-25, 0, 25, 74, "none", T, 2))
    parts.append(rect(-25, -74, 25, 0, "none", T, 2))
    # cancha de referencia
    parts.append(rect(-50, -32, 50, 32, "#1B5E20"))
    return ''.join(parts) + '</svg>'


# -------------------------------------------------------- solo líneas
def kit_lines():
    parts = [header(bg="none")]
    W = "#FFFFFF"
    parts.append(rect(-49.2, -31.2, 49.2, 31.2, "none", W, 3))
    parts.append(rect(-0.5, -31.2, 0.5, 31.2, W))
    parts.append(poly_ring(0, 0, 8.5, 36, "none", W, 3))
    for sx in (1, -1):
        parts.append(rect(sx * 34.3, -19.2, sx * 35.1, 19.2, "none", W, 3))
        parts.append(rect(sx * 35.1, -20, sx * 49.2, 20, "none", W, 3))
        parts.append(rect(sx * 44.8, -11.5, sx * 45.6, 11.5, "none", W, 3))
        parts.append(rect(sx * 45.6, -12.3, sx * 49.2, 12.3, "none", W, 3))
        parts.append(rect(sx * 38.7, -0.5, sx * 39.7, 0.5, W))
    return ''.join(parts) + '</svg>'


def main():
    files = {"kit-1-cancha.svg": kit_1,
             "kit-2-graderias.svg": kit_2,
             "cancha-lineas.svg": kit_lines}
    for name, fn in files.items():
        path = os.path.join(HERE, name)
        with open(path, "w") as f:
            f.write(fn())
        print("svg ->", name)


if __name__ == "__main__":
    main()
