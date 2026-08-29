#!/usr/bin/env python3
# Genera el documento escolar del estadio en PDF, WORD (.docx) y HTML,
# con capturas y tablas. Todo en Python puro (sin librerias).
import base64
import json
import os
import struct
import zipfile
import zlib

HERE = os.path.dirname(os.path.abspath(__file__))
CAP = os.path.join(HERE, "capturas")
M = json.load(open(os.path.join(HERE, "estadio-modelo.json")))

GRUPOS = M["grupos"]
PASOS = M["pasos"]
PIEZAS = M["piezas"]
NCUB = sum(1 for p in PIEZAS if p["tipo"] == "Cubo")
NPRIS = len(PIEZAS) - NCUB
por_grupo = {}
for p in PIEZAS:
    por_grupo.setdefault(p["archivo"], 0)
    por_grupo[p["archivo"]] += 1
por_paso = {}
for p in PIEZAS:
    por_paso[p["paso"]] = por_paso.get(p["paso"], 0) + 1

CLAVE = ["Base de cancha", "Franja de cesped 2", "Linea banda norte", "Linea media",
         "Círculo central 01", "Poste oeste norte", "Travesano oeste",
         "Tribuna NORTE grada 1", "Tribuna NORTE grada 4", "Asientos N fila 1 bloque 1",
         "Asientos E fila 2 bloque 1", "Columna norte frente 1", "Columna norte cumbrera 1",
         "Columna cumbrera este", "Techo norte", "Techo este (girado 90)",
         "Valla norte 1", "Tunel (marco)", "Tunel (dintel)", "Banco 1 (asiento)",
         "Techo banco 1 (prisma)", "Marcador pantalla (luz)", "Torre de luz NO (panel)",
         "Mastil", "Bandera Peru franja 1", "Entrada dintel", "Banderin corner 1 (tela)",
         "Marca de posicion 1"]
tabla_clave = []
for p in PIEZAS:
    if p["n"] in CLAVE:
        tabla_clave.append(p)

IMGS = ["cap-detalle-norte.png", "cap-arriba.png", "cap-frente.png",
        "cap-paso03.png", "cap-paso08.png", "cap-paso10.png",
        "cap-detalle-sur.png", "cap-detalle-este.png"]


def png_rgb(path):
    d = open(path, "rb").read()
    assert d[:8] == b"\x89PNG\r\n\x1a\n"
    pos = 8
    w = h = None
    idat = b""
    while pos < len(d):
        ln = struct.unpack(">I", d[pos:pos + 4])[0]
        t = d[pos + 4:pos + 8]
        seg = d[pos + 8:pos + 8 + ln]
        if t == b"IHDR":
            w, h = struct.unpack(">II", seg[:8])
        elif t == b"IDAT":
            idat += seg
        pos += 12 + ln
    raw = zlib.decompress(idat)
    stride = w * 3
    out = bytearray()
    for i in range(h):
        f = raw[i * (stride + 1)]
        assert f == 0, "solo soporto filter 0"
        out += raw[i * (stride + 1) + 1:(i + 1) * (stride + 1)]
    return w, h, bytes(out)


RGB = {n: png_rgb(os.path.join(CAP, n)) for n in IMGS}

# ============================================================================
# 1) PDF  (A4, Helvetica WinAnsi, imagenes RGB FlateDecode)
# ============================================================================
PW, PH = 595, 842
objs = []          # (num, bytes)


def esc(t):
    return t.replace("\\", r"\\").replace("(", r"\(").replace(")", r"\)")


class Pag:
    def __init__(self):
        self.ops = []

    def texto(self, x, y, s, txt, bold=False):
        f = "/F2" if bold else "/F1"
        self.ops.append("BT %s %d Tf %d %d Td (%s) Tj ET" % (f, s, x, y, esc(txt)))

    def linea(self, x1, y1, x2, y2, w=0.8, gris="0.45 0.45 0.45"):
        self.ops.append("%s RG %s w %d %d m %d %d l S" % (gris, w, x1, y1, x2, y2))

    def img(self, name, x, y, w):
        ww, hh, _ = RGB[name]
        h = w * hh / ww
        self.ops.append("q %s 0 0 %s %d %d cm /Im_%s Do Q" % (
            format(w, ".1f"), format(h, ".1f"), x, y, name.replace(".", "_")))
        return h


paginas = []

# ---- pagina 1: portada
p = Pag()
p.texto(60, 780, 22, "DISEÑO 3D EN TINKERCAD", True)
p.texto(60, 752, 22, "ESTADIO DE FÚTBOL", True)
p.texto(60, 726, 11, "Curso: EPT   |   Grado: 4.º de secundaria   |   Fecha: ____________")
p.texto(60, 710, 11, "Estudiante: ______________________________________________")
p.texto(60, 684, 11, "REGLA DE LA TAREA: todo el modelo usa solamente 2 figuras de", True)
p.texto(60, 670, 11, "Tinkercad: el CUBO y el PRISMA TRIANGULAR (\"Tejado\" / Roof).", True)
p.texto(60, 648, 10, "Piezas: %d en total (%d cubos + %d prismas triangulares), construidas" % (len(PIEZAS), NCUB, NPRIS))
p.texto(60, 634, 10, "en %d pasos. Medidas totales: 197.3 x 148.6 x 38.0 mm" % len(PASOS))
p.texto(60, 620, 10, "(cancha oficial a escala: 105 x 68 mm).")
h = p.img("cap-detalle-norte.png", 60, 610 - 300, 475)
p.texto(60, 610 - 300 - 14, 9, "Captura 1. Vista general del estadio: cancha con franjas y lineas, 4 tribunas con")
p.texto(60, 610 - 300 - 26, 9, "asientos rojos/azules, 4 techos de prisma triangular, columnas, torres de luz,")
p.texto(60, 610 - 300 - 38, 9, "marcador gigante, túnel, bancos de suplentes y entrada monumental.")
paginas.append(p)

# ---- paginas de capturas (layout dinamico: 2 figs por pagina)
def nueva(titulo=None):
    p = Pag()
    yy = 790
    if titulo:
        p.texto(60, yy, 16, titulo, True)
        yy -= 26
    paginas.append(p)
    return p, yy

def fig(nombre, cap):
    global paginas
    w, hh, _ = RGB[nombre]
    h = 455 * hh / w
    p, yy = paginas[-1], getattr(paginas[-1], "_y", None)
    if yy is None or yy - h < 70:
        p, yy = nueva()
    yy -= h
    p.img(nombre, 70, yy, 455)
    yy -= 14
    p.texto(70, yy, 9, cap)
    p._y = yy - 22

p, y0 = nueva("1. CAPTURAS DEL MODELO")
p._y = y0
fig("cap-arriba.png", "Captura 2. Vista desde arriba: franjas de cesped, lineas, circulo central, areas y 4 tribunas.")
fig("cap-frente.png", "Captura 3. Vista a ras de cancha: fachadas, entrada monumental y torres de luz.")
fig("cap-detalle-este.png", "Captura 4. Detalle este: tribuna con asientos rojos/azules, techo de prisma y marcador.")
fig("cap-detalle-sur.png", "Captura 5. Detalle sur: entrada monumental, tunel de jugadores y bancos de suplentes.")

p, y0 = nueva("2. CONSTRUCCION PASO A PASO (18 pasos)")
p._y = y0
fig("cap-paso03.png", "Captura 6. Pasos 1-4: base verde, franjas, lineas blancas y porterias.")
fig("cap-paso08.png", "Captura 7. Pasos 5-8: las 4 tribunas con gradas 6/10/14/18 mm y asientos.")
fig("cap-paso10.png", "Captura 8. Pasos 9-10: 18 columnas de 4x4x22 y 4 techos de prisma triangular.")
p, yy = paginas[-1], paginas[-1]._y
yy -= 14
p.texto(60, yy, 9, "Pasos 11-18 (vallas, tunel, bancos, marcador, torres, mastil con bandera del Peru,")
p.texto(60, yy - 12, 9, "entrada y marcas de posicion) se aprecian en las capturas 1, 4 y 5.")

# ---- pagina: colores + pasos + importar
p = Pag()
p.texto(60, 790, 16, "3. ARCHIVOS STL POR COLOR (orden de importacion 1 a 10)", True)
y = 764
p.texto(60, y, 10, "#   Archivo                          Color (hex)    Piezas", True)
y -= 8
p.linea(60, y, 535, y)
y -= 16
for i, g in enumerate(GRUPOS, start=1):
    p.texto(60, y, 10, "%-3d %-30s %-14s %d" % (i, g["archivo"] + ".stl", g["color"], por_grupo[g["archivo"]]))
    p.texto(470, y, 10, g["nombre"][:24])
    y -= 15
y -= 12
p.texto(60, y, 13, "4. LOS 18 PASOS", True)
y -= 18
for i, nombre in enumerate(PASOS, start=1):
    p.texto(60, y, 9, "%2d. %s (%d piezas)" % (i, nombre, por_paso.get(i, 0)))
    y -= 13
y -= 12
p.texto(60, y, 13, "5. COMO SE IMPORTA EN TINKERCAD", True)
y -= 16
for t in ["1. Importar los 10 STL en orden, SIN moverlos: las 4 marcas de 0.6 mm de las",
          "   esquinas quedan alineadas solas.",
          "2. Pintar cada pieza con su codigo hex (2 clics por pieza).",
          "3. Ctrl+A  ->  Ctrl+G (agrupar) y poner nombre: Estadio - [tu nombre].",
          "4. El STL no guarda colores (limitacion del formato): por eso van por color."]:
    p.texto(60, y, 9, t)
    y -= 13
paginas.append(p)

# ---- pagina: medidas + verificacion
p = Pag()
p.texto(60, 790, 16, "6. MEDIDAS DE LAS PIEZAS PRINCIPALES (mm)", True)
y = 766
p.texto(60, y, 9, "Pieza                        Figura     Largo  Ancho  Alto   Base Z", True)
y -= 6
p.linea(60, y, 535, y)
y -= 14
for pz in tabla_clave:
    d = pz["d"]
    p.texto(60, y, 8.4, "%-28s %-10s %6.1f %6.1f %5.1f %8.1f" % (
        pz["n"][:28], "cubo" if pz["tipo"] == "Cubo" else "tejado", d[0], d[1], d[2], pz["base"]))
    y -= 11.5
y -= 12
p.texto(60, y, 13, "7. VERIFICACION TECNICA", True)
y -= 16
for t in ["- Cada una de las %d piezas es un SOLIDO CERRADO (watertight): 0 aristas" % len(PIEZAS),
          "  sueltas, 0 triangulos degenerados, 0 normales invertidas.",
          "- Ninguna pieza atraviesa a otra: 0 cruces de volumen (verificador propio).",
          "- Solo se usan 2 figuras: %d cubos y %d prismas triangulares." % (NCUB, NPRIS),
          "- Cotas reales del archivo: X 197.30 mm, Y 148.60 mm, Z 38.00 mm.",
          "- Documentos acompanantes: guia HTML interactiva con visor 3D y tablas",
          "  completas de las %d piezas, y 10 archivos STL listos para importar." % len(PIEZAS)]:
    p.texto(60, y, 9, t)
    y -= 13
paginas.append(p)

# ---- ensamblar PDF
img_objs = {}   # name -> obj num
next_num = [1]


def num():
    n = next_num[0]
    next_num[0] += 1
    return n


font1 = num()
font2 = num()
for n in IMGS:
    img_objs[n] = num()
page_nums = [num() for _ in paginas]
pages_num = num()
catalog_num = num()

body = b"%PDF-1.4\n"
offsets = {}


def wobj(n, data):
    global body
    offsets[n] = len(body)
    body += ("%d 0 obj\n" % n).encode() + data + b"\nendobj\n"


wobj(font1, b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>")
wobj(font2, b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold /Encoding /WinAnsiEncoding >>")
for n in IMGS:
    ww, hh, rgb = RGB[n]
    comp = zlib.compress(rgb, 9)
    wobj(img_objs[n], ("<< /Type /XObject /Subtype /Image /Width %d /Height %d "
                       "/ColorSpace /DeviceRGB /BitsPerComponent 8 /Filter /FlateDecode "
                       "/Length %d >>\nstream\n" % (ww, hh, len(comp))).encode() + comp + b"\nendstream")
for pn, pg in zip(page_nums, paginas):
    contenido = "\n".join(pg.ops).encode("latin-1", "replace")
    cnum = num()
    wobj(cnum, ("<< /Length %d >>\nstream\n" % len(contenido)).encode() + contenido + b"\nendstream")
    res = ("<< /Font << /F1 %d 0 R /F2 %d 0 R >> /XObject << %s >> >>" % (
        font1, font2, " ".join("/Im_%s %d 0 R" % (n.replace(".", "_"), img_objs[n]) for n in IMGS)))
    wobj(pn, ("<< /Type /Page /Parent %d 0 R /MediaBox [0 0 %d %d] /Contents %d 0 R /Resources %s >>"
              % (pages_num, PW, PH, cnum, res)).encode())
wobj(pages_num, ("<< /Type /Pages /Kids [%s] /Count %d >>" % (
    " ".join("%d 0 R" % n for n in page_nums), len(page_nums))).encode())
wobj(catalog_num, ("<< /Type /Catalog /Pages %d 0 R >>" % pages_num).encode())
xref_pos = len(body)
body += ("xref\n0 %d\n" % (next_num[0])).encode()
body += b"0000000000 65535 f \n"
for n in range(1, next_num[0]):
    body += ("%010d 00000 n \n" % offsets[n]).encode()
body += ("trailer\n<< /Size %d /Root %d 0 R >>\nstartxref\n%d\n%%%%EOF\n" % (
    next_num[0], catalog_num, xref_pos)).encode()
open(os.path.join(HERE, "estadio-documento.pdf"), "wb").write(body)
print("PDF listo: %d paginas, %d KB" % (len(paginas), len(body) // 1024))

# ============================================================================
# 2) WORD (.docx) - zip de XML con imagenes PNG
# ============================================================================
WEMU = 5486400  # 6 pulgadas


def img_docx(nombre, rid):
    ww, hh, _ = RGB[nombre]
    h = int(WEMU * hh / ww)
    return ('<w:p><w:r><w:drawing><wp:inline distT="0" distB="0" distL="0" distR="0">'
            '<wp:extent cx="%d" cy="%d"/><wp:docPr id="%d" name="%s"/>'
            '<a:graphic xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">'
            '<a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture">'
            '<pic:pic xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture">'
            '<pic:nvPicPr><pic:cNvPr id="%d" name="%s"/><pic:cNvPicPr/></pic:nvPicPr>'
            '<pic:blipFill><a:blip r:embed="rId%s"/><a:stretch><a:fillRect/></a:stretch></pic:blipFill>'
            '<pic:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="%d" cy="%d"/></a:xfrm>'
            '<a:prstGeom prst="rect"><a:avLst/></a:prstGeom></pic:spPr></pic:pic>'
            '</a:graphicData></a:graphic></wp:inline></w:drawing></w:r></w:p>' % (WEMU, h, rid, nombre, rid, nombre, rid, WEMU, h))


def par(txt, size=22, bold=False, color=None):
    rpr = "<w:rPr>%s%s</w:rPr>" % ("<w:b/>" if bold else "",
                                  ("<w:sz w:val=\"%d\"/>" % size) if size != 22 else "")
    t = txt.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return "<w:p><w:r>%s<w:t xml:space=\"preserve\">%s</w:t></w:r></w:p>" % (rpr, t)


def celda(txt, w, bold=False, shade=None):
    t = txt.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    sh = "<w:shd w:val=\"clear\" w:fill=\"%s\"/>" % shade if shade else ""
    return ("<w:tc><w:tcPr><w:tcW w:w=\"%d\" w:type=\"dxa\"/>%s</w:tcPr>%s</w:tc>"
            % (w, sh, par(t, 16, bold)))


def tabla(filas, anchos):
    grid = "".join("<w:gridCol w:w=\"%d\"/>" % w for w in anchos)
    trs = []
    for i, f in enumerate(filas):
        tc = "".join(celda(c, w, bold=(i == 0), shade="D9E2F3" if i == 0 else None)
                     for c, w in zip(f, anchos))
        trs.append("<w:tr>%s</w:tr>" % tc)
    return ("<w:tbl><w:tblPr><w:tblW w:w=\"0\" w:type=\"auto\"/>"
            "<w:tblBorders>%s</w:tblBorders></w:tblPr><w:tblGrid>%s</w:tblGrid>%s</w:tbl>"
            % ("".join("<w:%s w:val=\"single\" w:sz=\"4\" w:space=\"0\" w:color=\"808080\"/>" % e
                       for e in ("top", "left", "bottom", "right", "insideH", "insideV")), grid, "".join(trs)))


B = []
B.append(par("DISEÑO 3D EN TINKERCAD - ESTADIO DE FÚTBOL", 32, True))
B.append(par("Curso: EPT  |  Grado: 4. de secundaria  |  Fecha: ____________", 20))
B.append(par("Estudiante: ______________________________________________", 20))
B.append(par("REGLA DE LA TAREA: todo el modelo usa solamente 2 figuras de Tinkercad: "
             "el CUBO y el PRISMA TRIANGULAR (Tejado / Roof), estirados y pintados.", 20, True))
B.append(par("Piezas: %d (%d cubos + %d prismas triangulares) en %d pasos. "
             "Medidas totales: 197.3 x 148.6 x 38.0 mm (cancha 105 x 68 mm)."
             % (len(PIEZAS), NCUB, NPRIS, len(PASOS)), 20))
B.append(img_docx("cap-detalle-norte.png", 1))
B.append(par("Captura 1. Vista general: cancha con franjas y lineas, 4 tribunas con asientos "
             "rojos/azules, 4 techos de prisma triangular, columnas, torres de luz, marcador, "
             "tunel, bancos y entrada monumental.", 16))
B.append(par("1. CAPTURAS DEL MODELO", 26, True))
B.append(img_docx("cap-arriba.png", 2))
B.append(par("Captura 2. Vista superior: franjas de cesped, lineas, circulo central y areas.", 16))
B.append(img_docx("cap-frente.png", 3))
B.append(par("Captura 3. Vista frontal: fachadas, entrada monumental y torres de luz.", 16))
B.append(img_docx("cap-detalle-este.png", 4))
B.append(par("Captura 4. Detalle este: asientos, techo de prisma triangular y marcador gigante.", 16))
B.append(par("2. CONSTRUCCION PASO A PASO", 26, True))
B.append(img_docx("cap-paso03.png", 5))
B.append(par("Captura 5. Pasos 1-4: base verde, franjas, líneas blancas y porterías.", 16))
B.append(img_docx("cap-paso08.png", 6))
B.append(par("Captura 6. Pasos 5-8: tribunas con gradas escalonadas 6/10/14/18 mm y asientos.", 16))
B.append(img_docx("cap-paso10.png", 7))
B.append(par("Captura 7. Pasos 9-10: 18 columnas de 4x4x22 y 4 techos de prisma triangular.", 16))
B.append(img_docx("cap-detalle-sur.png", 8))
B.append(par("Captura 8. Detalle sur: entrada monumental, tunel de jugadores y bancos de suplentes.", 16))
B.append(par("3. ARCHIVOS STL POR COLOR (importar en orden, sin moverlos)", 26, True))
B.append(tabla([["#", "Archivo", "Color hex", "Piezas", "Que pinta"]] +
               [[str(i), g["archivo"] + ".stl", g["color"], str(por_grupo[g["archivo"]]), g["nombre"]]
                for i, g in enumerate(GRUPOS, start=1)],
               [500, 2600, 1200, 900, 4160]))
B.append(par("4. LOS 18 PASOS", 26, True))
for i, nombre in enumerate(PASOS, start=1):
    B.append(par("%2d. %s (%d piezas)" % (i, nombre, por_paso.get(i, 0)), 18))
B.append(par("5. MEDIDAS DE LAS PIEZAS PRINCIPALES (mm)", 26, True))
B.append(tabla([["Pieza", "Figura", "Largo", "Ancho", "Alto", "Base Z"]] +
               [[p["n"], "cubo" if p["tipo"] == "Cubo" else "tejado",
                 "%.1f" % p["d"][0], "%.1f" % p["d"][1], "%.1f" % p["d"][2], "%.1f" % p["base"]]
                for p in tabla_clave],
               [3300, 1000, 1100, 1100, 1000, 1100]))
B.append(par("6. VERIFICACION Y COMO IMPORTAR", 26, True))
for t in ["- Cada pieza es un sólido cerrado (watertight): 0 aristas sueltas, 0 normales invertidas.",
          "- Ninguna pieza atraviesa a otra (0 cruces de volumen).",
          "- Solo 2 figuras: %d cubos y %d prismas triangulares." % (NCUB, NPRIS),
          "- Importar los 10 STL en orden SIN moverlos; las 4 marcas de 0.6 mm alinean solas.",
          "- Pintar cada pieza con su hex; luego Ctrl+A, Ctrl+G y nombre: Estadio - [tu nombre].",
          "- El STL no guarda colores (limitacion del formato): por eso van agrupados por color."]:
    B.append(par(t, 18))

doc_xml = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
           '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" '
           'xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing" '
           'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
           '<w:body>%s<w:sectPr/></w:body></w:document>' % "".join(B))

ct = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
      '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
      '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
      '<Default Extension="xml" ContentType="application/xml"/>'
      '<Default Extension="png" ContentType="image/png"/>'
      '<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
      '</Types>')
rels = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>'
        '</Relationships>')
doc_rels = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            + "".join('<Relationship Id="rId%d" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="media/%s"/>' % (i, n) for i, n in enumerate(IMGS, start=1))
            + "</Relationships>")

with zipfile.ZipFile(os.path.join(HERE, "estadio-documento.docx"), "w", zipfile.ZIP_DEFLATED) as z:
    z.writestr("[Content_Types].xml", ct)
    z.writestr("_rels/.rels", rels)
    z.writestr("word/document.xml", doc_xml)
    z.writestr("word/_rels/document.xml.rels", doc_rels)
    for i, n in enumerate(IMGS, start=1):
        z.write(os.path.join(CAP, n), "word/media/%s" % n)
print("DOCX listo: %d KB" % (os.path.getsize(os.path.join(HERE, "estadio-documento.docx")) // 1024))

# ============================================================================
# 3) HTML (un solo archivo, imagenes en base64)
# ============================================================================
def b64(nombre):
    return base64.b64encode(open(os.path.join(CAP, nombre), "rb").read()).decode()

filas_color = "".join(
    "<tr><td>%d</td><td><code>%s.stl</code></td><td><span class='chip' style='background:%s'></span> <code>%s</code></td><td>%d</td><td>%s</td></tr>"
    % (i, g["archivo"], g["color"], g["color"], por_grupo[g["archivo"]], g["nombre"])
    for i, g in enumerate(GRUPOS, start=1))
filas_med = "".join(
    "<tr><td>%s</td><td>%s</td><td class='n'>%.1f</td><td class='n'>%.1f</td><td class='n'>%.1f</td><td class='n'>%.1f</td></tr>"
    % (p["n"], "cubo" if p["tipo"] == "Cubo" else "tejado", p["d"][0], p["d"][1], p["d"][2], p["base"])
    for p in tabla_clave)
pasos_li = "".join("<li><b>Paso %d.</b> %s <span class='badge'>%d piezas</span></li>"
                   % (i, n, por_paso.get(i, 0)) for i, n in enumerate(PASOS, start=1))

html = """<!DOCTYPE html>
<html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Documento EPT - Estadio 3D en Tinkercad</title>
<style>
body{margin:0;background:#f2f5f8;color:#1d2733;font:15px/1.6 system-ui,Arial,sans-serif}
.pag{max-width:860px;margin:18px auto;background:#fff;border:1px solid #dfe6ee;border-radius:14px;padding:34px 40px;box-shadow:0 2px 10px rgba(20,40,80,.08)}
h1{font-size:26px;margin:0 0 4px}
h2{font-size:19px;margin:26px 0 10px;border-left:5px solid #43A047;padding-left:10px}
.meta{color:#5b6b7c}
img{width:100%;border-radius:10px;border:1px solid #dfe6ee;margin:8px 0 4px}
figcaption{color:#5b6b7c;font-size:13px;margin-bottom:14px}
table{width:100%;border-collapse:collapse;font-size:13.5px;margin:10px 0}
th,td{border:1px solid #dfe6ee;padding:6px 8px;text-align:left}
th{background:#eaf3ea}
td.n{text-align:right}
.chip{display:inline-block;width:15px;height:15px;border-radius:4px;border:1px solid #0003;vertical-align:-3px}
.badge{background:#eaf3ea;border:1px solid #cfe6cf;border-radius:14px;padding:1px 8px;font-size:12px;color:#2c6e31}
code{background:#eef2f6;padding:1px 5px;border-radius:5px}
.reglas{background:#fff8e1;border:1px solid #f0dca0;border-radius:10px;padding:10px 14px}
ul li{margin:4px 0}
@media print{.pag{box-shadow:none;border:none;margin:0;max-width:none;border-radius:0}}
</style></head><body>
<div class="pag">
<h1>Dise&ntilde;o 3D en Tinkercad &mdash; Estadio de f&uacute;tbol</h1>
<div class="meta">Curso: EPT &middot; Grado: 4.&ordm; de secundaria &middot; Fecha: ____________<br>
Estudiante: ______________________________________________</div>
<p class="reglas"><b>REGLA DE LA TAREA:</b> todo el modelo usa solamente <b>2 figuras</b> de
Tinkercad: el <b>CUBO</b> y el <b>PRISMA TRIANGULAR</b> (&ldquo;Tejado&rdquo; / Roof), estirados y pintados.
Son <b>__N__ piezas</b> (__NC__ cubos + __NP__ prismas) en <b>18 pasos</b>.
Medidas totales: <b>197.3 &times; 148.6 &times; 38.0 mm</b> (cancha oficial a escala 105 &times; 68 mm).</p>
<figure><img src="data:image/png;base64,__I0__" alt="Vista general">
<figcaption>Captura 1. Vista general: cancha con franjas y l&iacute;neas, 4 tribunas con asientos rojos/azules,
4 techos de prisma triangular, columnas, torres de luz, marcador gigante, t&uacute;nel, bancos y entrada monumental.</figcaption></figure>

<h2>1. Capturas del modelo</h2>
<figure><img src="data:image/png;base64,__I1__" alt="Vista superior">
<figcaption>Captura 2. Vista superior: franjas de c&eacute;sped, l&iacute;neas, c&iacute;rculo central y &aacute;reas.</figcaption></figure>
<figure><img src="data:image/png;base64,__I2__" alt="Vista frontal">
<figcaption>Captura 3. Vista frontal: fachadas, entrada monumental y torres de luz.</figcaption></figure>
<figure><img src="data:image/png;base64,__I3__" alt="Detalle este">
<figcaption>Captura 4. Detalle este: asientos, techo de prisma triangular y marcador gigante.</figcaption></figure>

<h2>2. Construcci&oacute;n paso a paso</h2>
<figure><img src="data:image/png;base64,__I4__" alt="Pasos 1-4">
<figcaption>Captura 5. Pasos 1&ndash;4: base verde, franjas, l&iacute;neas blancas y porter&iacute;as.</figcaption></figure>
<figure><img src="data:image/png;base64,__I5__" alt="Pasos 5-8">
<figcaption>Captura 6. Pasos 5&ndash;8: tribunas con gradas escalonadas 6/10/14/18 mm y asientos.</figcaption></figure>
<figure><img src="data:image/png;base64,__I6__" alt="Pasos 9-10">
<figcaption>Captura 7. Pasos 9&ndash;10: 18 columnas de 4&times;4&times;22 y 4 techos de prisma triangular.</figcaption></figure>
<figure><img src="data:image/png;base64,__I7__" alt="Detalle sur">
<figcaption>Captura 8. Detalle sur: entrada monumental, t&uacute;nel de jugadores y bancos de suplentes.</figcaption></figure>

<h2>3. Archivos STL por color (importar en orden, sin moverlos)</h2>
<table><thead><tr><th>#</th><th>Archivo</th><th>Color</th><th>Piezas</th><th>Qu&eacute; pinta</th></tr></thead>
<tbody>__FC__</tbody></table>

<h2>4. Los 18 pasos</h2>
<ul>__PL__</ul>

<h2>5. Medidas de las piezas principales (mm)</h2>
<table><thead><tr><th>Pieza</th><th>Figura</th><th>Largo</th><th>Ancho</th><th>Alto</th><th>Base Z</th></tr></thead>
<tbody>__FM__</tbody></table>

<h2>6. Verificaci&oacute;n y c&oacute;mo importar</h2>
<ul>
<li>Cada pieza es un s&oacute;lido cerrado (watertight): 0 aristas sueltas, 0 normales invertidas.</li>
<li>Ninguna pieza atraviesa a otra: 0 cruces de volumen (verificador propio).</li>
<li>Solo 2 figuras: __NC__ cubos y __NP__ prismas triangulares.</li>
<li>Importar los 10 STL en orden <b>SIN moverlos</b>: las 4 marcas de 0.6 mm de las esquinas alinean solas.</li>
<li>Pintar cada pieza con su c&oacute;digo hex (2 clics) y luego <code>Ctrl+A</code> &rarr; <code>Ctrl+G</code>, nombre: <b>Estadio &mdash; [tu nombre]</b>.</li>
<li>El STL no guarda colores (limitaci&oacute;n del formato): por eso van agrupados por color.</li>
</ul>
</div>
</body></html>
"""
html = (html.replace("__N__", str(len(PIEZAS))).replace("__NC__", str(NCUB)).replace("__NP__", str(NPRIS))
        .replace("__FC__", filas_color).replace("__FM__", filas_med).replace("__PL__", pasos_li))
for i, n in enumerate(IMGS):
    html = html.replace("__I%d__" % i, b64(n))
open(os.path.join(HERE, "estadio-documento.html"), "w").write(html)
print("HTML listo: %d KB" % (len(html) // 1024))
