# Estadio de fútbol para Tinkercad (tarea EPT)

Diseño 3D hecho **solo con 2 figuras**: el CUBO y el PRISMA TRIANGULAR
("Tejado" / Roof en Tinkercad), estirados y pintados. Nada más.

## Qué hay aquí

| Archivo | Qué es |
|---|---|
| `estadio-tinkercad-guia.html` | Guía interactiva: visor 3D (sin internet), slider de 18 pasos y tablas con medidas exactas (mm), centro X/Y, altura de base Z y color hex de cada pieza |
| `estadio-importar.html` | Cómo importar los 10 STL en Tinkercad y pintarlos (incluye tips para celular) |
| `index.html` | Índice con todos los enlaces |
| `estadio-piezas/01..10-*.stl` | **10 STL agrupados por color** (ver tabla abajo). Cada uno trae 4 marcas de posición de 0.6 mm en las esquinas (±97, ±74) para que al importarlos caigan alineados solos |
| `estadio-piezas.zip` | Los 10 STL comprimidos |
| `estadio-tinkercad.stl` / `-ascii.stl` / `.obj` | Estadio completo en 1 sola pieza (respaldo) |
| `svg/kit-*.svg`, `svg/cancha-lineas.svg` | SVG con colores (plan B para celular: sí importan, entran planos) |
| `estadio-render.png` | Render de referencia del modelo |
| `generar_estadio.py` | Fuente: genera toda la geometría |
| `verificar.py` | Chequeos: sólidos cerrados, sin cruces, cotas |

## Los 10 colores (orden de importación 1→10)

1. `01-verde-cancha` #43A047 · 2. `02-verde-franjas` #388E3C ·
3. `03-gris-gradas` #90A4AE · 4. `04-blanco-lineas` #FFFFFF ·
5. `05-columnas-pizarra` #546E7A · 6. `06-techos-plateado` #CFD8DC ·
7. `07-rojo-asientos` #E53935 · 8. `08-azul-asientos` #1E88E5 ·
9. `09-oscuro` #212121 · 10. `10-amarillo-luces` #FFF176

## Regenerar / verificar

```bash
python3 generar_estadio.py   # reconstruye STL, zip, json y svg
python3 verificar.py         # watertight + sin cruces + cotas  (debe decir TODO OK)
python3 armar_guias.py       # regenera los HTML con las tablas
node servidor.mjs            # sirve todo en http://0.0.0.0:4321
```

## Datos del modelo

- 208 piezas: 202 cubos + 6 prismas triangulares (4 techos + 2 techitos de banco).
- Cancha 105 × 68 mm; modelo completo 197.3 × 148.6 × 38.0 mm.
- Gradas escalonadas 6/10/14/18 mm · 18 columnas 4×4×22 · techos de 10 mm de alto.
- Verificado: cada pieza cierra (0 aristas sueltas), 0 normales invertidas,
  0 piezas atravesadas entre sí (las uniones cara a cara son normales en Tinkercad).
