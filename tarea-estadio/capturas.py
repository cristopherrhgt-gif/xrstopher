#!/usr/bin/env python3
# Genera las capturas (renders PNG) del estadio para el documento escolar.
import json
import math
import os
import struct
import zlib

HERE = os.path.dirname(os.path.abspath(__file__))
M = json.load(open(os.path.join(HERE, "estadio-modelo.json")))
W, H = 900, 560


def render(path, rx, rz, zoom, centro=None, hasta_paso=18):
    cx, sx, cz, sz = math.cos(rx), math.sin(rx), math.cos(rz), math.sin(rz)
    L = [0.35, 0.5, 0.75]
    ln = math.sqrt(sum(v * v for v in L)); L = [v / ln for v in L]
    buf = bytearray(b'\x12\x16\x1c' * W * H)
    zbuf = [-1e9] * (W * H)

    ox = oy = 0.0
    if centro:
        x1 = centro[0] * cz - centro[1] * sz
        y1 = centro[0] * sz + centro[1] * cz
        ox = -(x1 * zoom)
        oy = (y1 * sx + centro[2] * cx) * zoom

    def proy(x, y, z):
        x1 = x * cz - y * sz
        y1 = x * sz + y * cz
        y2 = y1 * cx - z * sx
        z2 = y1 * sx + z * cx
        return (W / 2 + x1 * zoom + ox, H / 2 - z2 * zoom + oy, y2)

    caras = []
    for p in M["piezas"]:
        if p["paso"] > hasta_paso:
            continue
        hexa = p["hex"]
        base = (int(hexa[1:3], 16), int(hexa[3:5], 16), int(hexa[5:7], 16))
        for t in p["t"]:
            v = [(t[k], t[k + 1], t[k + 2]) for k in (0, 3, 6)]
            a = [v[1][j] - v[0][j] for j in range(3)]
            b = [v[2][j] - v[0][j] for j in range(3)]
            N = [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]
            ny1 = N[0] * sz + N[1] * cz
            if ny1 * cx - N[2] * sx <= 0:
                continue
            nl = math.sqrt(sum(c * c for c in N)) or 1
            luz = 0.30 + 0.70 * max(0.0, sum(N[j] / nl * L[j] for j in range(3)))
            P = [proy(*q) for q in v]
            caras.append((P, tuple(min(255, int(c * luz)) for c in base),
                          sum(q[2] for q in P) / 3))
    caras.sort(key=lambda c: c[2])
    for P, rgb, _ in caras:
        xs = [q[0] for q in P]; ys = [q[1] for q in P]
        x0, x1 = max(0, int(min(xs))), min(W - 1, int(max(xs)) + 1)
        y0, y1 = max(0, int(min(ys))), min(H - 1, int(max(ys)) + 1)
        ax, ay = P[0][0], P[0][1]; bx, by = P[1][0], P[1][1]; gx, gy = P[2][0], P[2][1]
        D = (by - gy) * (ax - gx) - (bx - gx) * (ay - gy)
        if abs(D) < 1e-9:
            continue
        for yy in range(y0, y1 + 1):
            row = yy * W
            for xx in range(x0, x1 + 1):
                px, py = xx + 0.5, yy + 0.5
                l = ((by - gy) * (px - gx) - (bx - gx) * (py - gy)) / D
                m = ((gy - ay) * (px - gx) - (gx - ax) * (py - gy)) / D
                if l < -1e-9 or m < -1e-9 or (1 - l - m) < -1e-9:
                    continue
                z = l * P[0][2] + m * P[1][2] + (1 - l - m) * P[2][2]
                idx = row + xx
                if z > zbuf[idx]:
                    zbuf[idx] = z
                    j = idx * 3
                    buf[j], buf[j + 1], buf[j + 2] = rgb
    if path:
        guardar_png(path, buf)
    return bytes(buf)


def guardar_png(path, buf):
    raw = b"".join(b"\x00" + bytes(buf[i * W * 3:(i + 1) * W * 3]) for i in range(H))

    def chunk(t, d):
        return struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d) & 0xffffffff)
    open(path, "wb").write(b"\x89PNG\r\n\x1a\n"
                           + chunk(b"IHDR", struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0))
                           + chunk(b"IDAT", zlib.compress(raw, 9))
                           + chunk(b"IEND", b""))


CAPS = [
    ("cap-portada.png",  dict(rx=-0.55, rz=0.62, zoom=3.1)),
    ("cap-arriba.png",   dict(rx=-0.95, rz=0.62, zoom=3.0)),
    ("cap-frente.png",   dict(rx=-0.28, rz=0.35, zoom=3.1)),
    ("cap-paso03.png",   dict(rx=-0.95, rz=0.0, zoom=3.4, hasta_paso=4)),
    ("cap-paso08.png",   dict(rx=-0.55, rz=0.62, zoom=3.1, hasta_paso=8)),
    ("cap-paso10.png",   dict(rx=-0.55, rz=0.62, zoom=3.1, hasta_paso=10)),
]

CAPS_RECORTES = [
    ("cap-detalle-sur.png",  dict(rx=-0.55, rz=0.62, zoom=4.2, centro=(0, 55, 8))),
    ("cap-detalle-este.png", dict(rx=-0.55, rz=0.62, zoom=4.2, centro=(85, 30, 15))),
    ("cap-detalle-norte.png",dict(rx=-0.55, rz=0.62, zoom=4.2, centro=(-20, -40, 8))),
]

def render_recorte(path, rx, rz, zoom, centro, w=900, h=560, hasta_paso=18):
    """Render grande y recorte alrededor de 'centro': camara identica a la
    vista completa (ya verificada), solo se encuadra la zona."""
    RW, RH = 2200, 1400
    cx, sx, cz, sz = math.cos(rx), math.sin(rx), math.cos(rz), math.sin(rz)
    L = [0.35, 0.5, 0.75]
    ln = math.sqrt(sum(v * v for v in L)); L = [v / ln for v in L]
    buf = bytearray(b'\x12\x16\x1c' * RW * RH)
    zbuf = [-1e9] * (RW * RH)

    def proy(x, y, z):
        x1 = x * cz - y * sz
        y1 = x * sz + y * cz
        y2 = y1 * cx - z * sx
        z2 = y1 * sx + z * cx
        return (RW / 2 + x1 * zoom, RH / 2 - z2 * zoom, y2)

    caras = []
    for p in M["piezas"]:
        if p["paso"] > hasta_paso:
            continue
        hexa = p["hex"]
        base = (int(hexa[1:3], 16), int(hexa[3:5], 16), int(hexa[5:7], 16))
        for t in p["t"]:
            v = [(t[k], t[k + 1], t[k + 2]) for k in (0, 3, 6)]
            a = [v[1][j] - v[0][j] for j in range(3)]
            b = [v[2][j] - v[0][j] for j in range(3)]
            N = [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]
            ny1 = N[0] * sz + N[1] * cz
            if ny1 * cx - N[2] * sx <= 0:
                continue
            nl = math.sqrt(sum(c * c for c in N)) or 1
            luz = 0.30 + 0.70 * max(0.0, sum(N[j] / nl * L[j] for j in range(3)))
            P = [proy(*q) for q in v]
            caras.append((P, tuple(min(255, int(c * luz)) for c in base),
                          sum(q[2] for q in P) / 3))
    caras.sort(key=lambda c: c[2])
    for P, rgb, _ in caras:
        xs = [q[0] for q in P]; ys = [q[1] for q in P]
        x0, x1 = max(0, int(min(xs))), min(RW - 1, int(max(xs)) + 1)
        y0, y1 = max(0, int(min(ys))), min(RH - 1, int(max(ys)) + 1)
        ax, ay = P[0][0], P[0][1]; bx, by = P[1][0], P[1][1]; gx, gy = P[2][0], P[2][1]
        D = (by - gy) * (ax - gx) - (bx - gx) * (ay - gy)
        if abs(D) < 1e-9:
            continue
        for yy in range(y0, y1 + 1):
            row = yy * RW
            for xx in range(x0, x1 + 1):
                px, py = xx + 0.5, yy + 0.5
                l = ((by - gy) * (px - gx) - (bx - gx) * (py - gy)) / D
                m = ((gy - ay) * (px - gx) - (gx - ax) * (py - gy)) / D
                if l < -1e-9 or m < -1e-9 or (1 - l - m) < -1e-9:
                    continue
                z = l * P[0][2] + m * P[1][2] + (1 - l - m) * P[2][2]
                idx = row + xx
                if z > zbuf[idx]:
                    zbuf[idx] = z
                    j = idx * 3
                    buf[j], buf[j + 1], buf[j + 2] = rgb
    # recorte centrado en el punto pedido
    pcx, pcy, _ = proy(*centro)
    ox0 = int(max(0, min(RW - w, pcx - w / 2)))
    oy0 = int(max(0, min(RH - h, pcy - h / 2)))
    out = bytearray(b'\x12\x16\x1c' * w * h)
    for yy in range(h):
        src = ((oy0 + yy) * RW + ox0) * 3
        out[yy * w * 3:(yy + 1) * w * 3] = buf[src:src + w * 3]
    global W, H
    W2, H2 = W, H
    W, H = w, h
    guardar_png(path, out)
    W, H = W2, H2


if __name__ == "__main__":
    os.makedirs(os.path.join(HERE, "capturas"), exist_ok=True)
    for nombre, kw in CAPS:
        render(os.path.join(HERE, "capturas", nombre), **kw)
        print("captura lista:", nombre)
    for nombre, kw in CAPS_RECORTES:
        render_recorte(os.path.join(HERE, "capturas", nombre), **kw)
        print("captura lista:", nombre)


