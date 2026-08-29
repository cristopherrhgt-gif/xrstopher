#!/usr/bin/env python3
# Mete el modelo 3D DENTRO del HTML: un solo documento que abre en cualquier
# parte (celular, sin internet, doble clic) con visor + tablas funcionando.
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
html = open(os.path.join(HERE, "estadio-tinkercad-guia.html")).read()
modelo = open(os.path.join(HERE, "estadio-modelo.json")).read().strip()
assert "</script" not in modelo.lower(), "el json no debe romper el script"

# todo el bloque fetch(...)...}); se convierte en boot(<modelo embebido>);
nuevo_html, n = re.subn(
    r"fetch\('estadio-modelo\.json'\)\.then[\s\S]*?\}\);",
    lambda m: "boot(" + modelo + ");",
    html,
    count=1,
)
assert n == 1, "no encontro el bloque fetch"

out = os.path.join(HERE, "estadio-tinkercad-guia-completa.html")
open(out, "w").write(nuevo_html)
print("documento unico listo: %d KB -> %s" % (len(nuevo_html) // 1024, os.path.basename(out)))
