# 🏟️ ESTADIO para Tinkercad — solución final (v2.0)

Trabajo de EPT (4.º de secundaria): estadio de fútbol en Tinkercad.
**Regla: solo CUBOS y PRISMAS TRIANGULARES ("Tejado")** — todo el estadio
está construido con esas 2 figuras, estiradas, moldeadas y pintadas.

## Qué hay aquí

| Archivo | Qué es |
|---|---|
| `generar_estadio.py` | Script que construye el estadio completo (solo cubos + prismas) y exporta las 9 piezas STL por color. Se regenera todo con un comando. |
| `render_previews.py` | Genera las imágenes de vista previa de cada pieza. |
| `generar_svgs.py` | Genera los kits SVG (vistas superiores con colores). |
| `estadio-piezas/` | **La solución final: 9 archivos STL agrupados por color** (más 1 opcional). Todos watertight (sólidos cerrados) verificados, con 4 marcas de posición (cubitos de 0.6 mm en ±97, ±74) para que en Tinkercad caigan alineados solos. |
| `estadio-piezas.zip` | Los 9 STL comprimidos para descargar/transferir. |
| `estadio-tinkercad.stl` / `-ascii.stl` / `.obj` | Estadio completo en 1 sola pieza (respaldo). |
| `estadio-full.png` / `estadio-full-top.png` | Vistas previas del estadio completo. |
| `estadio-importar.html` | **Guía paso a paso** para importar las 9 piezas, pintarlas con su código hex, agruparlas y nombrar el diseño. Ábrela en el navegador. |
| `kit-1-cancha.svg`, `kit-2-graderias.svg`, `cancha-lineas.svg` | Kits SVG con colores (por si tu dispositivo los importa mejor que STL). |

## Contenido del diseño (148 piezas equivalentes en Tinkercad)

- Cancha 100×64 con franjas de césped en 2 verdes (`#43A047`/`#388E3C`)
- Líneas de cancha + círculo central con cubitos + áreas penales y metas
- 2 porterías con postes, travesaño y red
- 4 tribunas con gradas escalonadas (cubos de altura 6/10/14/18)
- 16 filas de asientos rojos (`#E53935`) y azules (`#1E88E5`)
- 18 columnas 4×4×22 (`#546E7A`) sosteniendo 4 techos de PRISMA triangular
  (98×46×10 y 50×74×10 girado 90°) (`#CFD8DC`)
- Vallas publicitarias, túnel de jugadores, 2 bancos de suplentes con techito
- Marcador gigante colgado bajo el techo norte
- 4 torres de luz con luces amarillas (`#FFF176`), mástil con bandera del Perú
- Entrada monumental con frontón, banderines de córner

## Cómo regenerar todo

```bash
python3 generar_estadio.py   # crea las 9 piezas + zip + estadio completo (verifica watertight y solapes)
python3 render_previews.py   # actualiza las vistas previas PNG
python3 generar_svgs.py      # actualiza los kits SVG
```

## Plan de importación (resumen)

1. Importar las 9 piezas EN ORDEN, sin moverlas de donde caen (las marcas las alinean).
2. Pintar cada una con su código hex (2 clics).
3. `Ctrl+A` → `Ctrl+G` para agrupar → nombrar "Estadio — [Jamón de barrio]".

Detalles en **`estadio-importar.html`**.
