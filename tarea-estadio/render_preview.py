#!/usr/bin/env python3
# Rasterizador con z-buffer para VER el estadio.
# Culling y luz con la normal EN EL MUNDO; profundidad con el eje de camara.
import json, math, os, struct, zlib
HERE = os.path.dirname(os.path.abspath(__file__))
M = json.load(open(os.path.join(HERE, 'estadio-modelo.json')))
W, H = 900, 560
rx, rz, zoom = -0.55, 0.62, 3.1
cx, sx, cz, sz = math.cos(rx), math.sin(rx), math.cos(rz), math.sin(rz)
L = [0.35, 0.5, 0.75]
ln = math.sqrt(sum(v * v for v in L)); L = [v / ln for v in L]
buf = bytearray(b'\x12\x16\x1c' * W * H)
zbuf = [-1e9] * (W * H)

def proy(x, y, z):
    x1 = x * cz - y * sz; y1 = x * sz + y * cz
    y2 = y1 * cx - z * sx; z2 = y1 * sx + z * cx
    return (W / 2 + x1 * zoom, H / 2 - z2 * zoom, y2)

caras = []
for p in M['piezas']:
    hexa = p['hex']
    base = (int(hexa[1:3], 16), int(hexa[3:5], 16), int(hexa[5:7], 16))
    for t in p['t']:
        v = [(t[k], t[k + 1], t[k + 2]) for k in (0, 3, 6)]
        a = [v[1][j] - v[0][j] for j in range(3)]
        b = [v[2][j] - v[0][j] for j in range(3)]
        N = [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]
        # rotar la normal igual que el mundo; la camara mira desde +y2
        nx1 = N[0] * cz - N[1] * sz; ny1 = N[0] * sz + N[1] * cz
        ndep = ny1 * cx - N[2] * sx
        if ndep <= 0:
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
        for xx in range(x0, x1 + 1):
            px, py = xx + 0.5, yy + 0.5
            l = ((by - gy) * (px - gx) - (bx - gx) * (py - gy)) / D   # peso de A
            m = ((gy - ay) * (px - gx) - (gx - ax) * (py - gy)) / D   # peso de B
            if l < -1e-9 or m < -1e-9 or (1 - l - m) < -1e-9:
                continue
            z = l * P[0][2] + m * P[1][2] + (1 - l - m) * P[2][2]
            idx = yy * W + xx
            if z > zbuf[idx]:
                zbuf[idx] = z
                j = idx * 3
                buf[j], buf[j + 1], buf[j + 2] = rgb

def png(path, w, h, rgb):
    raw = b''.join(b'\x00' + bytes(rgb[i * w * 3:(i + 1) * w * 3]) for i in range(h))
    def chunk(t, d):
        return struct.pack('>I', len(d)) + t + d + struct.pack('>I', zlib.crc32(t + d) & 0xffffffff)
    open(path, 'wb').write(b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 2, 0, 0, 0))
                           + chunk(b'IDAT', zlib.compress(raw, 9)) + chunk(b'IEND', b''))

png(os.path.join(HERE, 'estadio-render.png'), W, H, buf)
print('render listo. pixeles pintados:', sum(1 for z in zbuf if z < 1e8), 'de', W * H)
