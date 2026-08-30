#!/usr/bin/env python3
"""
Genera el ESTADIO para Tinkercad — 9 piezas STL agrupadas POR COLOR
(solución final v2.0 del proyecto EPT).

Regla del trabajo: SOLO cubos y prismas triangulares ("Tejado").

Cada pieza lleva 4 marcas de posición (cubitos de 0.6 mm en las esquinas
±97, ±74) para que al importar en Tinkercad todas caigan alineadas solas.

Todas las piezas son sólidos cerrados (watertight) — se verifica con
unión booleana (manifold) y checks de trimesh.

Uso:
    python3 generar_estadio.py
"""

import os
import zipfile

import numpy as np
import trimesh

HERE = os.path.dirname(os.path.abspath(__file__))
PIECES_DIR = os.path.join(HERE, "estadio-piezas")

# ---------------------------------------------------------------- helpers

def _extrude(pts2, w0, w1, uv, axis):
    """Extruye un polígono 2D (ccw) a lo largo de `axis` desde w0 hasta w1.
    uv: tupla con los 2 ejes del plano del polígono."""
    tris = []
    N = len(pts2)

    def P(u, v, wt):
        d = {uv[0]: u, uv[1]: v, axis: wt}
        return (d["x"], d["y"], d["z"])

    # paredes laterales
    for i in range(N):
        j = (i + 1) % N
        a = P(*pts2[i], w0); b = P(*pts2[j], w0)
        c = P(*pts2[j], w1); d = P(*pts2[i], w1)
        tris.append([a, b, c]); tris.append([a, c, d])
    # tapas
    c0 = np.mean(pts2, axis=0)
    for i in range(N):
        j = (i + 1) % N
        tris.append([P(*c0, w1), P(*pts2[i], w1), P(*pts2[j], w1)])
        tris.append([P(*c0, w0), P(*pts2[j], w0), P(*pts2[i], w0)])
    m = trimesh.Trimesh(vertices=np.array(tris).reshape(-1, 3),
                        faces=np.arange(len(tris) * 3).reshape(-1, 3))
    m.merge_vertices(digits_vertex=7)
    if m.volume < 0:  # orientación correcta (volumen positivo)
        m.invert()
    return m


def box(x0, x1, y0, y1, z0, z1):
    """Cubo sólido (regla: solo cubos)."""
    return _extrude([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], z0, z1, ("x", "y"), "z")


def prism_xz(cx, y0, y1, base, height, z0):
    """Prisma triangular: triángulo en el plano X-Z extruido en Y.
    (forma 'Tejado' de Tinkercad)"""
    pts = [(cx - base / 2, z0), (cx + base / 2, z0), (cx, z0 + height)]
    return _extrude(pts, y0, y1, ("x", "z"), "y")


def prism_yz(cy, x0, x1, base, height, z0):
    """Prisma triangular: triángulo en el plano Y-Z extruido en X."""
    pts = [(cy - base / 2, z0), (cy + base / 2, z0), (cy, z0 + height)]
    return _extrude(pts, x0, x1, ("y", "z"), "x")


def union(parts):
    """Unión booleana → un solo sólido cerrado."""
    parts = [p for p in parts if p is not None]
    if not parts:
        return None
    m = trimesh.boolean.union(parts, engine="manifold")
    if not m.is_winding_consistent:
        m.fix_normals()
    if m.volume < 0:
        m.invert()
    return m


def markers():
    """4 cubitos de 0.6 mm en las esquinas ±97, ±74 (marcas de posición)."""
    m = []
    for sx in (1, -1):
        for sy in (1, -1):
            x = 97 * sx; y = 74 * sy
            x0, x1 = (x - 0.6, x) if sx > 0 else (x, x + 0.6)
            y0, y1 = (y - 0.6, y) if sy > 0 else (y, y + 0.6)
            m.append(box(x0, x1, y0, y1, 0, 0.6))
    return m


# ------------------------------------------------------------ constructor

def build_all():
    os.makedirs(PIECES_DIR, exist_ok=True)

    G = {k: [] for k in [
        "verde-cancha", "gris-gradas", "blanco-lineas", "columnas-pizarra",
        "techos-plateado", "rojo-asientos", "azul-asientos", "oscuro",
        "amarillo-luces"]}

    def add(group, part):
        if isinstance(part, list):
            G[group].extend(part)
        else:
            G[group].append(part)

    # ================= CANCHA (verde) =================
    # base: 10 losas (una por franja, para contacto cara a cara exacto)
    for i in range(10):
        x0 = -50 + 10 * i
        add("verde-cancha", box(x0, x0 + 10, -32, 32, 0, 0.8))
    # franjas de césped: 5 claras (#43A047) aquí + 5 oscuras (#388E3C) extra
    dark_stripes = []
    for i in range(10):
        x0 = -50 + 10 * i
        s = box(x0, x0 + 10, -32, 32, 0.8, 1.4)
        if i % 2 == 0:
            add("verde-cancha", s)
        else:
            dark_stripes.append(s)

    # ================= LÍNEAS DE CANCHA (blanco) =================
    lz = (1.4, 1.7)  # z de las líneas (encima del césped)
    # borde: 4 esquinas + 4 segmentos (sin solaparse)
    add("blanco-lineas", box(49.2, 50, 31.2, 32, *lz))
    add("blanco-lineas", box(-50, -49.2, 31.2, 32, *lz))
    add("blanco-lineas", box(49.2, 50, -32, -31.2, *lz))
    add("blanco-lineas", box(-50, -49.2, -32, -31.2, *lz))
    add("blanco-lineas", box(-49.2, 49.2, 31.2, 32, *lz))
    add("blanco-lineas", box(-49.2, 49.2, -32, -31.2, *lz))
    add("blanco-lineas", box(49.2, 50, -31.2, 31.2, *lz))
    add("blanco-lineas", box(-50, -49.2, -31.2, 31.2, *lz))
    # línea de medio campo
    add("blanco-lineas", box(-0.5, 0.5, -31.2, 31.2, *lz))
    # círculo central con cubitos (sin los 2 que caen sobre la línea de medio campo)
    for k in range(24):
        if k in (6, 18):
            continue
        a = 2 * np.pi * k / 24
        cx = 8.5 * np.cos(a); cy = 8.5 * np.sin(a)
        add("blanco-lineas", box(cx - 0.5, cx + 0.5, cy - 0.5, cy + 0.5, *lz))
    # áreas penales y metas (los 2 lados) — las esquinas se solapan 0.2 mm
    # para que la unión booleana quede sin aristas compartidas
    for sx in (1, -1):
        add("blanco-lineas", box(sx * 34.3, sx * 35.1, -19.4, 19.4, *lz))
        add("blanco-lineas", box(sx * 35.1, sx * 49.4, 19.2, 20, *lz))
        add("blanco-lineas", box(sx * 35.1, sx * 49.4, -20, -19.2, *lz))
        add("blanco-lineas", box(sx * 44.8, sx * 45.6, -11.7, 11.7, *lz))
        add("blanco-lineas", box(sx * 45.6, sx * 49.4, 11.5, 12.3, *lz))
        add("blanco-lineas", box(sx * 45.6, sx * 49.4, -12.3, -11.5, *lz))
        add("blanco-lineas", box(sx * 38.7, sx * 39.7, -0.5, 0.5, *lz))  # punto penal
    # vallas publicitarias
    add("blanco-lineas", box(-46, 46, 32.2, 32.6, 0, 1.5))
    add("blanco-lineas", box(-46, 46, -32.6, -32.2, 0, 1.5))
    # porterías (postes + travesaño)
    for sx in (1, -1):
        add("blanco-lineas", box(sx * 50, sx * 50.2, 3.5, 3.7, 0, 2.5))
        add("blanco-lineas", box(sx * 50, sx * 50.2, -3.7, -3.5, 0, 2.5))
        add("blanco-lineas", box(sx * 50, sx * 50.2, -3.6, 3.6, 2.5, 2.7))
    # marcador gigante: paneles blancos (el cuerpo va en oscuro)
    add("blanco-lineas", box(-9, 9, 67, 67.2, 18.5, 21.5))
    add("blanco-lineas", box(-9, 9, 64.8, 65, 18.5, 21.5))
    # bandera del Perú: franja blanca (rojas van en rojo-asientos)
    add("blanco-lineas", box(92.5, 93, -66.95, -66.85, 14, 15.2))

    # ================= GRADAS (gris) =================
    def stand_tiers(p0, depth, axis, span0, span1):
        """Construye una tribuna escalonada (cubos por niveles, contacto
        cara a cara exacto). heights = [6,10,14,18]."""
        hs = [6, 10, 14, 18]
        bs = [p0 + depth * i / 4 for i in range(5)]
        parts = []
        for t in range(4):          # bloque de la grada t (altura hs[t])
            for level in range(t + 1):  # niveles 0..6, 6..10, 10..14, 14..18
                z0 = [0, 6, 10, 14][level]; z1 = [6, 10, 14, 18][level]
                if axis == "x":      # tribuna en X (gradas Este/Oeste)
                    parts.append(box(bs[t], bs[t + 1], span0, span1, z0, z1))
                else:                # tribuna en Y (gradas Norte/Sur)
                    parts.append(box(span0, span1, bs[t], bs[t + 1], z0, z1))
        return parts

    # Norte (Y+): y 36..74 ; Sur (Y-): y -74..-36 ; Este (X+): x 54..97 ; Oeste (X-)
    north = union(stand_tiers(36, 38, "y", -50, 50))
    south = north.copy()
    south.apply_transform(np.array([[1, 0, 0, 0], [0, -1, 0, 0],
                                    [0, 0, 1, 0], [0, 0, 0, 1]], dtype=float))
    east = union(stand_tiers(54, 43, "x", -32, 32))
    west = east.copy()
    west.apply_transform(np.array([[-1, 0, 0, 0], [0, 1, 0, 0],
                                   [0, 0, 1, 0], [0, 0, 0, 1]], dtype=float))
    add("gris-gradas", north)
    add("gris-gradas", south)
    add("gris-gradas", east)
    add("gris-gradas", west)
    # entrada monumental (frente a la tribuna Sur)
    add("gris-gradas", box(-7.5, -4.5, -34, -31, 0, 10))
    add("gris-gradas", box(4.5, 7.5, -34, -31, 0, 10))
    add("gris-gradas", box(-9, 9, -33, -31, 10, 12))

    # ================= COLUMNAS (pizarra) =================
    for x in (-60, -36, -12, 12, 36, 60):
        add("columnas-pizarra", box(x - 2, x + 2, 70, 74, 0, 22))
        add("columnas-pizarra", box(x - 2, x + 2, -74, -70, 0, 22))
    for y in (-24, 0, 24):
        add("columnas-pizarra", box(91, 95, y - 2, y + 2, 0, 22))
        add("columnas-pizarra", box(-95, -91, y - 2, y + 2, 0, 22))
    # torres de luz: mástiles
    for sx in (1, -1):
        for sy in (1, -1):
            add("columnas-pizarra", box(sx * 84, sx * 86, sy * 59, sy * 61, 0, 40))

    # ================= TECHOS (plateado) =================
    # 4 techos de prisma triangular: 98×46×10 (E/O) y 50×74×10 girado 90° (N/S)
    add("techos-plateado", prism_xz(74, -49, 49, 46, 10, 22))
    add("techos-plateado", prism_xz(-74, -49, 49, 46, 10, 22))
    # los techos N/S se solapan 1 mm en el centro (y=0) para una unión limpia
    add("techos-plateado", prism_yz(37.5, -25, 25, 74, 10, 22))   # y -0.5..74.5
    add("techos-plateado", prism_yz(-37.5, -25, 25, 74, 10, 22))  # y -74.5..0.5
    # techitos de los bancos de suplentes (este en y+, oeste en y-)
    add("techos-plateado", prism_xz(52.3, 8.3, 13.7, 2.2, 1.2, 3))
    add("techos-plateado", prism_xz(-52.3, -13.7, -8.3, 2.2, 1.2, 3))
    # frontón de la entrada
    add("techos-plateado", prism_xz(0, -33, -31, 18, 3, 12))

    # ================= ASIENTOS (rojo / azul) =================
    def seat_rows(stand_idx, sx, sy):
        """Filas de asientos (cubos delgados) sobre las gradas.
        stand_idx: nombre ('N','S','E','W'); sx/sy: -1 espeja el eje."""
        si = {"N": 0, "S": 1, "E": 2, "W": 3}[stand_idx]
        bs = {"N": [36, 45.5, 55, 64.5], "S": [36, 45.5, 55, 64.5],
              "E": [54, 64.75, 75.5, 86.25], "W": [54, 64.75, 75.5, 86.25]}[stand_idx]
        hs = [6, 10, 14, 18]
        rows = []
        for t in range(4):
            color = "rojo-asientos" if (si * 4 + t) % 2 == 0 else "azul-asientos"
            z0, z1 = hs[t] - 0.6, hs[t]
            if stand_idx in ("N", "S"):
                b = bs[t]
                y0, y1 = (b - 0.5, b) if sy > 0 else (-b, -b + 0.5)
                rows.append((color, box(-50, 50, y0, y1, z0, z1)))
            else:
                b = bs[t]
                x0, x1 = (b - 0.5, b) if sx > 0 else (-b, -b + 0.5)
                rows.append((color, box(x0, x1, -32, 32, z0, z1)))
        return rows

    for name, sx, sy in [("N", 1, 1), ("S", 1, -1),
                         ("E", 1, 1), ("W", -1, 1)]:
        for color, row in seat_rows(name, sx, sy):
            add(color, row)
    # bandera del Perú: franjas rojas
    add("rojo-asientos", box(92, 92.5, -66.95, -66.85, 14, 15.2))
    add("rojo-asientos", box(93, 93.5, -66.95, -66.85, 14, 15.2))

    # ================= OSCURO =================
    for sx in (1, -1):  # redes de las porterías
        add("oscuro", box(sx * 50.2, sx * 52.2, -3.7, 3.7, 0, 2.5))
    # marcador gigante (cuerpo)
    add("oscuro", box(-10, 10, 65, 67, 18, 22))
    # túnel de jugadores (boca cubierta contra la tribuna Oeste,
    # apartado de la portería — que está en y ±3.7)
    add("oscuro", box(-53.5, -50, 10.6, 15.4, 0, 1))
    add("oscuro", box(-53.5, -50, 10, 10.6, 0, 1))
    add("oscuro", box(-53.5, -50, 15.4, 16, 0, 1))
    add("oscuro", box(-53.5, -50, 10, 10.6, 1, 4.6))
    add("oscuro", box(-53.5, -50, 15.4, 16, 1, 4.6))
    add("oscuro", box(-53.5, -50, 10, 16, 4.6, 5.6))
    # bancos de suplentes (asiento + patas) — este en y+, oeste en y-
    for sx in (1, -1):
        y0, y1 = min(8.5 * sx, 13.5 * sx), max(8.5 * sx, 13.5 * sx)
        add("oscuro", box(sx * 51.4, sx * 53, y0, y1, 0, 1))
        for cy in (8.85 * sx, 13.15 * sx):
            for cx in (51.55, 52.85):
                add("oscuro", box(sx * cx, sx * cx + (0.3 if sx > 0 else -0.3),
                                  cy - 0.15, cy + 0.15, 1, 3))
    # banderines de córner (poste + banderita de prisma encima del poste)
    for sx in (1, -1):
        for sy in (1, -1):
            add("oscuro", box(49.3 * sx, 49.7 * sx, 35.6 * sy, 36.0 * sy, 0, 3))
            add("oscuro", prism_yz(35.8 * sy, 49.3 * sx, 49.7 * sx, 0.4, 0.4, 3))
    # mástil con bandera
    add("oscuro", box(92, 93, -67, -66, 0, 16))

    # ================= LUCES (amarillo) =================
    for sx in (1, -1):
        for sy in (1, -1):
            for z0 in (33, 35.5, 38):
                add("amarillo-luces", box(sx * 84, sx * 86, sy * 57, sy * 59, z0, z0 + 2))

    # ------------------------------------------------------------ construir
    colors = {
        "verde-cancha": "#43A047",
        "gris-gradas": "#90A4AE",
        "blanco-lineas": "#FFFFFF",
        "columnas-pizarra": "#546E7A",
        "techos-plateado": "#CFD8DC",
        "rojo-asientos": "#E53935",
        "azul-asientos": "#1E88E5",
        "oscuro": "#212121",
        "amarillo-luces": "#FFF176",
    }

    results = {}
    report = []
    for name, parts in G.items():
        m = union(parts)
        m = union([m] + markers())          # marcas de posición alineadas
        path = os.path.join(PIECES_DIR, name + ".stl")
        m.export(path)
        results[name] = m
        report.append((name, m))

    # bonus: franjas oscuras (verde #388E3C) — opcional para las 2 verdes
    bonus = union(dark_stripes + markers())
    bonus_path = os.path.join(PIECES_DIR, "verde-franjas-oscuras.stl")
    bonus.export(bonus_path)
    results["verde-franjas-oscuras"] = bonus
    report.append(("verde-franjas-oscuras (extra)", bonus))

    # estadio completo en 1 pieza (respaldo)
    full = union([m for name, m in results.items() if not name.startswith("verde-franjas")])
    full.export(os.path.join(HERE, "estadio-tinkercad.stl"))
    full.export(os.path.join(HERE, "estadio-tinkercad-ascii.stl"), file_type="stl_ascii")
    full.export(os.path.join(HERE, "estadio-tinkercad.obj"))
    report.append(("estadio completo", full))

    # zip con las 9 piezas
    zip_path = os.path.join(HERE, "estadio-piezas.zip")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for name in colors:
            zf.write(os.path.join(PIECES_DIR, name + ".stl"), name + ".stl")

    # reporte
    print(f"{'pieza':<34}{'watertight':<12}{'volumen':>10}  triángulos")
    for name, m in report:
        print(f"{name:<34}{str(m.is_watertight):<12}{m.volume:>10.1f}  {len(m.faces)}")

    # auditoría: solapes dentro de cada archivo
    print("\nAuditoría de solapes dentro de cada archivo:")
    total_overlap = 0.0
    for name, parts in G.items():
        bad = 0
        for i in range(len(parts)):
            for j in range(i + 1, len(parts)):
                a, b = parts[i].bounds, parts[j].bounds
                o = not (a[1, 0] <= b[0, 0] or b[1, 0] <= a[0, 0] or
                         a[1, 1] <= b[0, 1] or b[1, 1] <= a[0, 1] or
                         a[1, 2] <= b[0, 2] or b[1, 2] <= a[0, 2])
                if o:
                    ov = trimesh.boolean.intersection([parts[i], parts[j]], engine="manifold")
                    if ov.volume > 1e-6:
                        bad += 1
                        total_overlap += ov.volume
        print(f"  {name:<24} solapes: {bad}")
    print(f"  total volumen solapado: {total_overlap:.2f} mm³ "
          f"(los solapes se fusionan con la unión booleana → no afectan)")
    if total_overlap < 1e-6:
        print("  ✅ SIN solapes internos")

    print("\nZIP:", zip_path)
    return results


if __name__ == "__main__":
    build_all()
