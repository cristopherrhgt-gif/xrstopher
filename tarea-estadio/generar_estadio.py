#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generador del ESTADIO para Tinkercad (tarea EPT).
REGLA DE LA TAREA: solo se usan 2 figuras -> CUBO y PRISMA TRIANGULAR ("Tejado").
Todo se exporta como STL binario (solidos cerrados / watertight).

Salidas:
  estadio-piezas/NN-<color>.stl   -> 9 archivos agrupados POR COLOR (con 4 marcas de posicion)
  estadio-tinkercad.stl           -> estadio completo en 1 sola pieza (respaldo)
  estadio-tinkercad-ascii.stl     -> mismo respaldo en STL ASCII
  estadio-tinkercad.obj           -> respaldo OBJ
  estadio-modelo.json             -> datos para el visor 3D de la guia
  piezas.json                     -> tabla de medidas (mm) para la guia
  svg/kit-*.svg                   -> SVG con colores (planos de referencia)
"""

import json
import math
import os
import struct
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_STL = os.path.join(HERE, "estadio-piezas")
OUT_SVG = os.path.join(HERE, "svg")
os.makedirs(OUT_STL, exist_ok=True)
os.makedirs(OUT_SVG, exist_ok=True)

# ----------------------------------------------------------------------------
# COLORES OFICIALES DEL DISENO
# ----------------------------------------------------------------------------
COLORES = {
    "verde":     "#43A047",
    "verde2":    "#388E3C",
    "gris":      "#90A4AE",
    "blanco":    "#FFFFFF",
    "pizarra":   "#546E7A",
    "plateado":  "#CFD8DC",
    "rojo":      "#E53935",
    "azul":      "#1E88E5",
    "oscuro":    "#212121",
    "amarillo":  "#FFF176",
}

# Orden de importacion en Tinkercad (1..9)
GRUPOS = [
    ("01-verde-cancha",      "verde",    "Verde cancha (base)"),
    ("02-verde-franjas",     "verde2",   "Verde oscuro (franjas de cesped)"),
    ("03-gris-gradas",       "gris",     "Gris (gradas de las 4 tribunas)"),
    ("04-blanco-lineas",     "blanco",   "Blanco (lineas de la cancha)"),
    ("05-columnas-pizarra",  "pizarra",  "Pizarra (columnas, mastil, astas)"),
    ("06-techos-plateado",   "plateado", "Plateado (4 techos = prisma triangular)"),
    ("07-rojo-asientos",     "rojo",     "Rojo (asientos + franja bandera)"),
    ("08-azul-asientos",     "azul",     "Azul (asientos)"),
    ("09-oscuro",            "oscuro",   "Oscuro (porterias, vallas, tunel, bancos, entradas)"),
    ("10-amarillo-luces",    "amarillo", "Amarillo (luces y pantallas)"),
]

STEP_NAMES = [
    "Base de la cancha (1 cubo verde)",
    "Franjas de cesped (cubos verde oscuro)",
    "Lineas de la cancha (cubitos blancos)",
    "Porterias (postes + travesano, cubos oscuros)",
    "Tribuna NORTE - gradas escalonadas",
    "Tribuna SUR - gradas escalonadas",
    "Tribuna ESTE - gradas escalonadas",
    "Tribuna OESTE - gradas escalonadas",
    "18 columnas (4x4x22)",
    "4 techos (prisma triangular / Tejado)",
    "Vallas publicitarias",
    "Tunel de jugadores",
    "2 bancos de suplentes (con techito de prisma)",
    "Marcador gigante",
    "4 torres de luz",
    "Mastil con bandera del Peru",
    "Entrada monumental + banderines de corner",
    "4 marcas de posicion (para alinear al importar)",
]

pieces = []  # cada pieza: dict con grupo, paso, nombre, tipo, x,y,z (centro), dx,dy,dz, hex


def cubo(grupo, paso, nombre, cx, cy, z_base, dx, dy, dz):
    pieces.append(dict(grupo=grupo, paso=paso, nombre=nombre, tipo="cubo",
                       x=cx, y=cy, z=z_base + dz / 2.0,
                       dx=dx, dy=dy, dz=dz, base=z_base,
                       hex=COLORES[dict((g[0], g[1]) for g in GRUPOS)[grupo]]))


def prisma(grupo, paso, nombre, x_min, x_max, y_min, y_max, z_base, altura):
    """Prisma triangular = 'Tejado' de Tinkercad.
    Arista superior (cumbrera) paralela al eje X, en y = (y_min+y_max)/2.
    Equivale al Tejado puesto en el suelo, sin rotar."""
    cx = (x_min + x_max) / 2.0
    cy = (y_min + y_max) / 2.0
    pieces.append(dict(grupo=grupo, paso=paso, nombre=nombre, tipo="prisma",
                       x=cx, y=cy, z=z_base + altura / 2.0,
                       dx=x_max - x_min, dy=y_max - y_min, dz=altura,
                       base=z_base,
                       hex=COLORES[dict((g[0], g[1]) for g in GRUPOS)[grupo]]))


def prisma_girado90(grupo, paso, nombre, x_min, x_max, y_min, y_max, z_base, altura):
    """Prisma triangular con la cumbrera paralela al eje Y (Tejado girado 90 grados)."""
    cx = (x_min + x_max) / 2.0
    cy = (y_min + y_max) / 2.0
    pieces.append(dict(grupo=grupo, paso=paso, nombre=nombre, tipo="prisma90",
                       x=cx, y=cy, z=z_base + altura / 2.0,
                       dx=x_max - x_min, dy=y_max - y_min, dz=altura,
                       base=z_base,
                       hex=COLORES[dict((g[0], g[1]) for g in GRUPOS)[grupo]]))


# ============================================================================
# GEOMETRIA DEL ESTADIO  (unidad = mm en Tinkercad)
#   X = izquierda(-) / derecha(+)      Y = atras(-) / adelante(+)      Z = altura
#   Cancha de futbol: 105 x 68 mm      Centro del diseno: X=0, Y=0
# ============================================================================

# ---- PASO 1: base de la cancha ---------------------------------------------
cubo("01-verde-cancha", 1, "Base de cancha", 0, 0, 0, 105, 68, 2)   # cancha oficial 105 x 68 mm

# ---- PASO 2: franjas de cesped (9 franjas a lo ancho) ----------------------
FRANJA = 105.0 / 9.0
for i in range(9):
    if i % 2 == 0:
        continue  # las pares ya son el verde de la base
    cx = -52.5 + FRANJA * (i + 0.5)
    cubo("02-verde-franjas", 2, "Franja de cesped %d" % (i + 1),
         cx, 0, 2, FRANJA, 68, 0.6)

# ---- PASO 3: lineas de la cancha (cubitos blancos) -------------------------
LZ, LT = 2.6, 0.4  # altura de la linea, grosor
# lineas de banda (largas) y de meta (cortas) del rectangulo 105 x 68
cubo("04-blanco-lineas", 3, "Linea banda norte", 0, -34 + LT / 2, LZ, 105, LT, 0.3)
cubo("04-blanco-lineas", 3, "Linea banda sur", 0, 34 - LT / 2, LZ, 105, LT, 0.3)
cubo("04-blanco-lineas", 3, "Linea meta oeste", -52.5 + LT / 2, 0, LZ, LT, 68, 0.3)
cubo("04-blanco-lineas", 3, "Linea meta este", 52.5 - LT / 2, 0, LZ, LT, 68, 0.3)
# linea media
cubo("04-blanco-lineas", 3, "Linea media", 0, 0, LZ, LT, 68 - 2 * LT, 0.3)
# areas
for lado, sx in (("oeste", -1), ("este", 1)):
    xa = sx * (52.5 - 16.5)   # linea del area grande
    xp = sx * (52.5 - 5.5)    # linea del area chica
    cubo("04-blanco-lineas", 3, "Area grande %s (fondo)" % lado, xa, 0, LZ, LT, 40.32, 0.3)
    cubo("04-blanco-lineas", 3, "Area grande %s (arriba)" % lado, sx * (52.5 - 8.25), -(20.16 - LT / 2), LZ, 16.5 - LT, LT, 0.3)
    cubo("04-blanco-lineas", 3, "Area grande %s (abajo)" % lado, sx * (52.5 - 8.25), 20.16 - LT / 2, LZ, 16.5 - LT, LT, 0.3)
    cubo("04-blanco-lineas", 3, "Area chica %s (fondo)" % lado, xp, 0, LZ, LT, 18.32, 0.3)
    cubo("04-blanco-lineas", 3, "Area chica %s (arriba)" % lado, sx * (52.5 - 2.75), -(9.16 - LT / 2), LZ, 5.5 - LT, LT, 0.3)
    cubo("04-blanco-lineas", 3, "Area chica %s (abajo)" % lado, sx * (52.5 - 2.75), 9.16 - LT / 2, LZ, 5.5 - LT, LT, 0.3)
    cubo("04-blanco-lineas", 3, "Punto penal %s" % lado, sx * 41.5, 0, LZ, 1, 1, 0.4)
# circulo central: 24 cubitos formando el anillo (radio 9.15)
for i in range(24):
    a = 2 * math.pi * i / 24.0
    cubo("04-blanco-lineas", 3, "Circulo central %02d" % (i + 1),
         11.0 * math.cos(a), 11.0 * math.sin(a), LZ, 2.0, 2.0, 0.3)

# ---- PASO 4: porterias -----------------------------------------------------
for lado, sx in (("oeste", -1), ("este", 1)):
    gx = sx * 52.5
    cubo("09-oscuro", 4, "Poste %s norte" % lado, gx, -3.66, 2.6 + LZ, 0.6, 0.6, 2)
    cubo("09-oscuro", 4, "Poste %s sur" % lado, gx, 3.66, 2.6 + LZ, 0.6, 0.6, 2)
    cubo("09-oscuro", 4, "Travesano %s" % lado, gx, 0, 2 + LZ, 0.6, 7.92, 0.6)
    cubo("09-oscuro", 4, "Red %s (fondo)" % lado, gx + sx * 2.0, 0, LZ, 0.3, 7.32, 4)
    cubo("09-oscuro", 4, "Red %s (techo)" % lado, gx + sx * 1.0, 0, 4 + LZ, 2.0, 7.32, 0.3)

# ---- PASOS 5-8: tribunas con gradas escalonadas ---------------------------
# alturas de grada: 6 / 10 / 14 / 18 mm  (se sube hacia afuera)
GRADAS = [6, 10, 14, 18]
ANCHO_GRADA = 5.0


def tribuna_larga(paso, nombre, sy):
    """Tribuna sobre el lado largo (norte sy=-1 / sur sy=+1)."""
    for k, h in enumerate(GRADAS):
        y_c = sy * (36.5 + ANCHO_GRADA * (k + 0.5))
        cubo("03-gris-gradas", paso, "%s grada %d" % (nombre, k + 1),
             0, y_c, 0, 110, ANCHO_GRADA, h)


def tribuna_corta(paso, nombre, sx):
    """Tribuna sobre el lado corto (este sx=+1 / oeste sx=-1)."""
    for k, h in enumerate(GRADAS):
        x_c = sx * (58.5 + ANCHO_GRADA * (k + 0.5))
        cubo("03-gris-gradas", paso, "%s grada %d" % (nombre, k + 1),
             x_c, 0, 0, ANCHO_GRADA, 70, h)


tribuna_larga(5, "Tribuna NORTE", -1)
tribuna_larga(6, "Tribuna SUR", 1)
tribuna_corta(7, "Tribuna ESTE", 1)
tribuna_corta(8, "Tribuna OESTE", -1)

# ---- asientos: filas rojas (abajo) y azules (arriba) por bloque ------------
def asientos_larga(paso, sy):
    xs = [-55, -27.5, 0, 27.5]        # 4 bloques de 27.5 mm
    anchos = [27.5, 27.5, 27.5, 27.5]
    for k in range(len(GRADAS)):      # una fila por grada
        y_c = sy * (36.5 + ANCHO_GRADA * (k + 0.5))
        h = GRADAS[k]
        for j, (x0, w) in enumerate(zip(xs, anchos)):
            color = "07-rojo-asientos" if k % 2 == 0 else "08-azul-asientos"
            cubo(color, paso, "Asientos %s fila %d bloque %d" % ("N" if sy < 0 else "S", k + 1, j + 1),
                 x0 + w / 2.0, y_c, h, w, 3.2, 1.6)


def asientos_corta(paso, sx):
    ys = [-35, -17.5, 0, 17.5]
    largos = [17.5, 17.5, 17.5, 17.5]
    for k in range(len(GRADAS)):
        x_c = sx * (58.5 + ANCHO_GRADA * (k + 0.5))
        h = GRADAS[k]
        for j, (y0, w) in enumerate(zip(ys, largos)):
            color = "07-rojo-asientos" if k % 2 == 0 else "08-azul-asientos"
            cubo(color, paso, "Asientos %s fila %d bloque %d" % ("E" if sx > 0 else "O", k + 1, j + 1),
                 x_c, y0 + w / 2.0, h, 3.2, w, 1.6)


# tribuna norte -> paso 5, sur -> 6, este -> 7, oeste -> 8
asientos_larga(5, -1)
asientos_larga(6, 1)
asientos_corta(7, 1)
asientos_corta(8, -1)

# ---- PASO 9: 18 columnas 4x4x22 -------------------------------------------
COL_X = [-48, -16, 16, 48]
COL_X_CUMBRERA = [-48, -20, 20, 48]
for i, x_c in enumerate(COL_X):
    cubo("05-columnas-pizarra", 9, "Columna norte frente %d" % (i + 1), x_c, -35.5, 0, 4, 2, 22)
    cubo("05-columnas-pizarra", 9, "Columna sur frente %d" % (i + 1), x_c, 35.5, 0, 4, 2, 22)
    cubo("05-columnas-pizarra", 9, "Columna norte cumbrera %d" % (i + 1), COL_X_CUMBRERA[i], -59, 0, 4, 4, 22)
    cubo("05-columnas-pizarra", 9, "Columna sur cumbrera %d" % (i + 1), COL_X_CUMBRERA[i], 59, 0, 4, 4, 22)
# 2 columnas bajo la cumbrera de los techos cortos (este / oeste)
cubo("05-columnas-pizarra", 9, "Columna cumbrera este", 81, 0, 0, 4, 4, 22)
cubo("05-columnas-pizarra", 9, "Columna cumbrera oeste", -81, 0, 0, 4, 4, 22)

# ---- PASO 10: 4 techos = PRISMA TRIANGULAR ("Tejado") ---------------------
prisma("06-techos-plateado", 10, "Techo norte", -51, 51, -56, -32, 22, 10)     # 102 x 22, cumbrera en Y=-45
prisma("06-techos-plateado", 10, "Techo sur", -51, 51, 32, 56, 22, 10)        # 102 x 22, cumbrera en Y=+45
prisma_girado90("06-techos-plateado", 10, "Techo este (girado 90)", 56, 78, -29, 29, 22, 10)   # 22 x 58
prisma_girado90("06-techos-plateado", 10, "Techo oeste (girado 90)", -78, -56, -29, 29, 22, 10)

# ---- PASO 11: vallas publicitarias ----------------------------------------
for j, xc in enumerate([-37, 37]):   # 2 vallas por banda, fuera del tunel y de las columnas
    cubo("09-oscuro", 11, "Valla norte %d" % (j + 1), xc, -34.25, 2, 12, 0.5, 2.5)
    cubo("09-oscuro", 11, "Valla sur %d" % (j + 1), xc, 34.25, 2, 12, 0.5, 2.5)
for j, y0 in enumerate([-24, 0.5]):
    cubo("09-oscuro", 11, "Valla este %d" % (j + 1), 53.6, y0 + 11.75, 2, 0.5, 23.5, 2.5)
    cubo("09-oscuro", 11, "Valla oeste %d" % (j + 1), -53.6, y0 + 11.75, 2, 0.5, 23.5, 2.5)

# ---- PASO 12: tunel de jugadores ------------------------------------------
cubo("09-oscuro", 12, "Tunel (marco)", 0, -35.25, 0, 14, 2.5, 2.0)
cubo("09-oscuro", 12, "Tunel (dintel)", 0, -35.25, 2.0, 14, 2.5, 0.6)

# ---- PASO 13: 2 bancos de suplentes ---------------------------------------
for j, bx in enumerate([-30, 30]):
    cubo("09-oscuro", 13, "Banco %d (asiento)" % (j + 1), bx, -35.2, 0, 12, 2.0, 1.6)
    cubo("09-oscuro", 13, "Banco %d (respaldo)" % (j + 1), bx, -36.35, 0, 12, 0.3, 3.4)
    prisma("09-oscuro", 13, "Techo banco %d (prisma)" % (j + 1), bx - 7, bx + 7, -36.9, -34.9, 3.4, 2.0)

# ---- PASO 14: marcador gigante --------------------------------------------
cubo("05-columnas-pizarra", 14, "Marcador poste izquierdo", 82, 40, 0, 4, 4, 24)
cubo("05-columnas-pizarra", 14, "Marcador poste derecho", 98, 40, 0, 4, 4, 24)
cubo("09-oscuro", 14, "Marcador dintel", 90, 40, 33, 20, 4, 3)
cubo("09-oscuro", 14, "Marcador pantalla (fondo)", 90, 39.25, 24, 12, 2, 9)
cubo("10-amarillo-luces", 14, "Marcador pantalla (luz)", 90, 40.75, 25.5, 9, 1, 6)

# ---- PASO 15: 4 torres de luz ---------------------------------------------
TORRES = [(-88, -66), (88, -66), (-88, 66), (88, 66)]
etiquetas = ["NO", "NE", "SO", "SE"]
for i, (tx, ty) in enumerate(TORRES):
    cubo("05-columnas-pizarra", 15, "Torre de luz %s (poste)" % etiquetas[i], tx, ty, 0, 3, 3, 34)
    cubo("10-amarillo-luces", 15, "Torre de luz %s (panel)" % etiquetas[i], tx, ty, 34, 9, 9, 4)

# ---- PASO 16: mastil + bandera del Peru -----------------------------------
cubo("05-columnas-pizarra", 16, "Mastil", -60, 52, 0, 1.2, 1.2, 26)
for k, franja in enumerate(["07-rojo-asientos", "04-blanco-lineas", "07-rojo-asientos"]):
    cubo(franja, 16, "Bandera Peru franja %d" % (k + 1), -56.7, 52, 20 + 2 * k, 6.6, 0.4, 2)

# ---- PASO 17: entrada monumental + banderines de corner -------------------
cubo("09-oscuro", 17, "Entrada pilar oeste", -14, 59, 0, 5, 5, 16)
cubo("09-oscuro", 17, "Entrada pilar este", 14, 59, 0, 5, 5, 16)
cubo("09-oscuro", 17, "Entrada dintel", 0, 59, 16, 33, 5, 4)
for j, (fx, fy) in enumerate([(-54.5, -35.6), (54.5, -35.6), (-54.5, 35.6), (54.5, 35.6)]):
    cubo("05-columnas-pizarra", 17, "Banderin corner %d (asta)" % (j + 1), fx, fy, 2.6, 0.4, 0.4, 3)
    cubo("10-amarillo-luces", 17, "Banderin corner %d (tela)" % (j + 1), fx + 0.9, fy, 4.6, 1.8, 0.3, 1)

# ---- PASO 18: 4 marcas de posicion (para que todo caiga alineado) ---------
for j, (mx, my) in enumerate([(-97, -74), (97, -74), (-97, 74), (97, 74)]):
    cubo("09-oscuro", 18, "Marca de posicion %d" % (j + 1), mx, my, 0, 0.6, 0.6, 0.6)

print("piezas totales:", len(pieces))
por_grupo = {}
por_paso = {}
for p in pieces:
    por_grupo[p["grupo"]] = por_grupo.get(p["grupo"], 0) + 1
    por_paso[p["paso"]] = por_paso.get(p["paso"], 0) + 1
for g, _c, nombre in GRUPOS:
    print("  %-24s %3d piezas  -> %s" % (g, por_grupo.get(g, 0), nombre))
for s in range(1, 19):
    print("  paso %2d: %3d piezas  | %s" % (s, por_paso.get(s, 0), STEP_NAMES[s - 1]))


# ============================================================================
# TRIANGULADO  (solidos cerrados: cada arista compartida exactamente 2 veces)
# ============================================================================
def tri_cubo(p):
    x, y, z, dx, dy, dz = p["x"], p["y"], p["z"], p["dx"], p["dy"], p["dz"]
    hx, hy, hz = dx / 2.0, dy / 2.0, dz / 2.0
    v = [
        (x - hx, y - hy, z - hz), (x + hx, y - hy, z - hz),
        (x + hx, y + hy, z - hz), (x - hx, y + hy, z - hz),
        (x - hx, y - hy, z + hz), (x + hx, y - hy, z + hz),
        (x + hx, y + hy, z + hz), (x - hx, y + hy, z + hz),
    ]
    caras = [
        (0, 3, 2), (0, 2, 1),   # z-
        (4, 5, 6), (4, 6, 7),   # z+
        (0, 1, 5), (0, 5, 4),   # y-
        (3, 7, 6), (3, 6, 2),   # y+
        (0, 4, 7), (0, 7, 3),   # x-
        (1, 2, 6), (1, 6, 5),   # x+
    ]
    return [(v[a], v[b], v[c]) for a, b, c in caras]


def prisma_tris_final(p):
    """Triangulacion del 'Tejado' (prisma triangular) de Tinkercad.

    6 vertices y 5 caras:
      base rectangular (2 tris) + 2 faldas rectangulares (2+2 tris)
      + 2 tapas triangulares (1+1)  =  8 triangulos.
    Cada una de las 9 aristas queda recorrida 2 veces, en sentidos opuestos.
    """
    x, y, z, dx, dy, dz = p["x"], p["y"], p["z"], p["dx"], p["dy"], p["dz"]
    hx, hy = dx / 2.0, dy / 2.0
    z0, z1 = z - dz / 2.0, z + dz / 2.0
    if p["tipo"] == "prisma":
        # cumbrera paralela al eje X: L = extremo x-, R = extremo x+
        Lm, Lp = (x - hx, y - hy, z0), (x - hx, y + hy, z0)   # aleros en x-
        Rm, Rp = (x + hx, y - hy, z0), (x + hx, y + hy, z0)   # aleros en x+
        Cm, Cp = (x - hx, y, z1), (x + hx, y, z1)             # cumbrera
        return [
            (Lm, Rp, Rm), (Lm, Lp, Rp),   # base rectangular      -> -Z
            (Lm, Rm, Cp), (Lm, Cp, Cm),   # falda lado y-
            (Lp, Rp, Cp), (Lp, Cp, Cm),   # falda lado y+
            (Lm, Lp, Cm),                 # tapa x- (triangulo)
            (Rm, Rp, Cp),                 # tapa x+ (triangulo)
        ]
    # cumbrera paralela al eje Y (Tejado girado 90 grados): L = y-, R = y+
    Lm, Lp = (x - hx, y - hy, z0), (x + hx, y - hy, z0)       # aleros en y-
    Rm, Rp = (x - hx, y + hy, z0), (x + hx, y + hy, z0)       # aleros en y+
    Cm, Cp = (x, y - hy, z1), (x, y + hy, z1)                 # cumbrera
    return [
        (Lm, Rp, Rm), (Lm, Lp, Rp),      # base rectangular      -> -Z
        (Lm, Rm, Cp), (Lm, Cp, Cm),      # falda lado x-
        (Lp, Rp, Cp), (Lp, Cp, Cm),      # falda lado x+
        (Lm, Lp, Cm),                    # tapa y- (triangulo)
        (Rm, Rp, Cp),                    # tapa y+ (triangulo)
    ]


def triangulos(p):
    if p["tipo"] == "cubo":
        return tri_cubo(p)
    return prisma_tris_final(p)


# ---- verificacion rapida: normales hacia afuera ----------------------------
def centroide(p):
    return (p["x"], p["y"], p["z"])


def normal(t):
    (a, b, c) = t
    ux, uy, uz = b[0] - a[0], b[1] - a[1], b[2] - a[2]
    vx, vy, vz = c[0] - a[0], c[1] - a[1], c[2] - a[2]
    return (uy * vz - uz * vy, uz * vx - ux * vz, ux * vy - uy * vx)


def orientar(t, c):
    """Garantiza que el triangulo apunte hacia afuera del solido."""
    n = normal(t)
    m = ((t[0][0] + t[1][0] + t[2][0]) / 3.0 - c[0],
         (t[0][1] + t[1][1] + t[2][1]) / 3.0 - c[1],
         (t[0][2] + t[1][2] + t[2][2]) / 3.0 - c[2])
    if n[0] * m[0] + n[1] * m[1] + n[2] * m[2] < 0:
        return (t[0], t[2], t[1])
    return t


# pasada 1: orientar todas las caras hacia afuera
for p in pieces:
    c = centroide(p)
    p["_tris"] = [orientar(t, c) for t in triangulos(p)]

# pasada 1b: cada pieza debe ser un solido cerrado (arista emparejada 2 veces,
# en sentidos opuestos). Si no, hay un error de winding y se avisa al toque.
def _kk(v):
    return (round(v[0], 6), round(v[1], 6), round(v[2], 6))


def pieza_cierra(tris):
    ar = {}
    for t in tris:
        a, b, c = _kk(t[0]), _kk(t[1]), _kk(t[2])
        for e in ((a, b), (b, c), (c, a)):
            ar[e] = ar.get(e, 0) + 1
    sueltas = [e for e in ar if (e[1], e[0]) not in ar]
    dobles = [e for e in ar if (e[1], e[0]) in ar and ar[e] != 1]
    return sueltas, dobles


rotas = []
for p in pieces:
    su, do = pieza_cierra(p["_tris"])
    if su or do:
        rotas.append((p["nombre"], p["tipo"], len(su), len(do)))
if rotas:
    for r in rotas:
        print("  PIEZA NO CERRADA:", r)
    raise SystemExit("ERROR: %d piezas no cierran (winding mal)" % len(rotas))
print("las %d piezas cierran: cada arista emparejada en sentidos opuestos" % len(pieces))

# pasada 2: volver a verificar (ahora con tolerancia de punto flotante)
EPS = 1e-9
bad = 0
for p in pieces:
    c = centroide(p)
    for t in p["_tris"]:
        n = normal(t)
        m = ((t[0][0] + t[1][0] + t[2][0]) / 3.0 - c[0],
             (t[0][1] + t[1][1] + t[2][1]) / 3.0 - c[1],
             (t[0][2] + t[1][2] + t[2][2]) / 3.0 - c[2])
        if n[0] * m[0] + n[1] * m[1] + n[2] * m[2] < -EPS:
            bad += 1
print("triangulos con normal invertida:", bad)
assert bad == 0, "hay normales invertidas"


# ============================================================================
# EXPORT STL
# ============================================================================
def stl_binario(path, lista_piezas, nombre_solido="estadio"):
    tris = []
    for p in lista_piezas:
        tris += p['_tris']
    with open(path, "wb") as f:
        f.write(b"ESTADIO EPT - solo cubo y prisma triangular".ljust(80, b"\0"))
        f.write(struct.pack("<I", len(tris)))
        for t in tris:
            n = normal(t)
            L = math.sqrt(n[0] ** 2 + n[1] ** 2 + n[2] ** 2) or 1.0
            f.write(struct.pack("<3f", n[0] / L, n[1] / L, n[2] / L))
            for v in t:
                f.write(struct.pack("<3f", v[0], v[1], v[2]))
            f.write(struct.pack("<H", 0))
    return len(tris)


def stl_ascii(path, lista_piezas):
    with open(path, "w") as f:
        f.write("solid estadio\n")
        for p in lista_piezas:
            for t in p['_tris']:
                n = normal(t)
                L = math.sqrt(n[0] ** 2 + n[1] ** 2 + n[2] ** 2) or 1.0
                f.write(" facet normal %.6f %.6f %.6f\n" % (n[0] / L, n[1] / L, n[2] / L))
                f.write("  outer loop\n")
                for v in t:
                    f.write("   vertex %.6f %.6f %.6f\n" % v)
                f.write("  endloop\n endfacet\n")
        f.write("endsolid estadio\n")


def obj(path, lista_piezas):
    off = 1
    with open(path, "w") as f:
        f.write("# Estadio EPT - solo cubo y prisma triangular\n")
        for p in lista_piezas:
            vs = {}
            for t in p['_tris']:
                for v in t:
                    vs[v] = None
            keys = list(vs.keys())
            idx = {v: off + i for i, v in enumerate(keys)}
            for v in keys:
                f.write("v %.6f %.6f %.6f\n" % v)
            off += len(keys)
            for t in p['_tris']:
                f.write("f %d %d %d\n" % (idx[t[0]], idx[t[1]], idx[t[2]]))


n = 0
for g, _hexcolor, _nombre in GRUPOS:
    sel = [p for p in pieces if p["grupo"] == g]
    path = os.path.join(OUT_STL, g + ".stl")
    t = stl_binario(path, sel, g)
    kb = os.path.getsize(path) / 1024.0
    print("STL %-24s %3d piezas %5d triangulos %7.1f KB" % (g, len(sel), t, kb))
    n += len(sel)

total = stl_binario(os.path.join(HERE, "estadio-tinkercad.stl"), pieces)
stl_ascii(os.path.join(HERE, "estadio-tinkercad-ascii.stl"), pieces)
obj(os.path.join(HERE, "estadio-tinkercad.obj"), pieces)
print("STL completo: %d piezas, %d triangulos" % (n, total))

with zipfile.ZipFile(os.path.join(HERE, "estadio-piezas.zip"), "w", zipfile.ZIP_DEFLATED) as z:
    for g, _c, _n in GRUPOS:
        z.write(os.path.join(OUT_STL, g + ".stl"), "estadio-piezas/" + g + ".stl")
print("zip listo:", os.path.getsize(os.path.join(HERE, "estadio-piezas.zip")) / 1024.0, "KB")


# ============================================================================
# JSON para la guia (visor 3D + tablas)
# ============================================================================
modelo = {"colores": COLORES, "grupos": [dict(zip(("archivo", "color", "nombre"), g)) for g in GRUPOS],
          "pasos": STEP_NAMES, "piezas": []}
for i, p in enumerate(pieces):
    modelo["piezas"].append({
        "n": p["nombre"], "paso": p["paso"], "archivo": p["grupo"], "hex": p["hex"],
        "tipo": "Tejado (prisma)" if p["tipo"] != "cubo" else "Cubo",
        "d": [round(p["dx"], 2), round(p["dy"], 2), round(p["dz"], 2)],
        "c": [round(p["x"], 2), round(p["y"], 2), round(p["z"], 2)],
        "base": round(p["base"], 2),
        "t": [[round(c, 6) for v in t for c in v] for t in p["_tris"]],
    })
with open(os.path.join(HERE, "estadio-modelo.json"), "w") as f:
    json.dump(modelo, f, separators=(",", ":"))
print("modelo json:", os.path.getsize(os.path.join(HERE, "estadio-modelo.json")) / 1024.0, "KB")


# ============================================================================
# SVG de referencia (vista de planta, con los colores reales)
# ============================================================================
def svg(grupos_sel, path, titulo, escala=6.0, ox=640, oy=440):
    L = ['<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d">' % (2 * ox, 2 * oy, 2 * ox, 2 * oy)]
    L.append('<rect width="100%" height="100%" fill="#263238"/>')
    L.append('<text x="20" y="34" fill="#fff" font-family="Arial" font-size="22">%s</text>' % titulo)
    sel = [p for p in pieces if p["grupo"] in grupos_sel and p["paso"] != 18]
    sel.sort(key=lambda p: p["dz"])
    for p in sel:
        w, h = p["dx"] * escala, p["dy"] * escala
        x = ox + (p["x"] - p["dx"] / 2.0) * escala
        y = oy - (p["y"] + p["dy"] / 2.0) * escala
        L.append('<rect x="%.2f" y="%.2f" width="%.2f" height="%.2f" fill="%s" stroke="#212121" stroke-width="0.6"/>'
                 % (x, y, w, h, p["hex"]))
    L.append("</svg>")
    with open(path, "w") as f:
        f.write("\n".join(L))
    print("svg:", os.path.basename(path), len(sel), "figuras")


svg(["01-verde-cancha"], os.path.join(OUT_SVG, "kit-1-cancha.svg"), "Kit 1 - Cancha y franjas de cesped")
svg(["03-gris-gradas", "07-rojo-asientos", "08-azul-asientos"],
    os.path.join(OUT_SVG, "kit-2-graderias.svg"), "Kit 2 - Graderias y asientos")
svg(["04-blanco-lineas"], os.path.join(OUT_SVG, "cancha-lineas.svg"), "Lineas de la cancha")
