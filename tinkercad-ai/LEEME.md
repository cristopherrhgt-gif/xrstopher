# 🤖 Tinkercad + IA en tu Galaxy S25 Ultra

Guía para que un agente de IA (tipo Claude Code) haga tus trabajos de
**Tinkercad 3D** desde tu S25 Ultra: tú le pides el diseño en lenguaje
natural y la IA genera el modelo **listo para importar a Tinkercad**.

---

## ✅ Lo que ya está hecho (prueba real en esta carpeta)

Generé **3 modelos 3D reales** con código, para que los pruebes hoy mismo:

| Archivo | Pieza | Qué es |
|---|---|---|
| `engranaje.stl` | ⚙️ Engranaje de 12 dientes (Ø80 mm, 8 mm alto, agujero Ø20 mm) | 288 triángulos |
| `caja_base.stl` | 📦 Caja hueca 60×40×20 mm, pared de 2 mm | lista para imprimir |
| `caja_tapa.stl` | 🔝 Tapa a medida de la caja (con ajuste) | encaja con la base |

**Cómo probarlos AHORA (sin instalar nada):**

1. Entra a [tinkercad.com](https://www.tinkercad.com) → **Diseños 3D**
2. Botón **Importar** → elige uno de estos `.stl`
3. ¡Listo! Lo puedes editar, combinar con formas de Tinkercad y exportar.

El generador está en `generar.py` — es el mismo "cerebro" que usará la IA
para crear tus piezas. Puedes pedir cualquier variación:

```bash
python3 generar.py --part engranaje --teeth 16 --thickness 10 --hole 12 --out mi_engranaje.stl
python3 generar.py --part caja --length 80 --width 50 --height 30 --wall 3 --out caja_grande.stl
python3 generar.py --part tapa --length 80 --width 50 --out tapa_grande.stl
```

---

## 📱 Opción 1 (RECOMENDADA): Claude Code en tu S25 Ultra con Termux

El S25 Ultra tiene 12 GB de RAM y Android 15 — suficiente para correr un
agente de IA completo en el teléfono.

### Paso 1 — Instala Termux
1. Ve a **Galaxy Store** (no Google Play, la versión de Play está desactualizada)
2. Busca **Termux** e instálalo
3. Ábrelo y ejecuta:
```bash
termux-setup-storage        # da permisos a tus archivos
pkg update && pkg upgrade -y
pkg install nodejs git python python-pip -y
```

### Paso 2 — Instala Claude Code
```bash
npm install -g @anthropic-ai/claude-code
claude
```
- Inicia sesión con tu cuenta de Claude (opcional: usa tu plan Max/Pro)
- O usa API key: `export ANTHROPIC_API_KEY=sk-...`

### Paso 3 — Descarga el generador a tu teléfono
```bash
cd ~/storage/downloads
git clone https://github.com/tu-repo/tinkercad-ai  # o copia los archivos de esta carpeta
cd tinkercad-ai
pip install numpy-stl
```

### Paso 4 — ¡Pídele tu diseño!
Dentro de Claude Code, escribe por ejemplo:

> *"Genera un engranaje con 16 dientes, 90 mm de diámetro, 10 mm de grosor
> y un agujero central de 15 mm. Guárdalo como mi_pieza.stl"*

La IA editará/ejecutará `generar.py` y te dejará el `.stl` listo.

### Paso 5 — Importa a Tinkercad
1. Abre el `.stl` desde la app de **Archivos** del Samsung → cómpratelo en
   Tinkercad (tinkercad.com desde el navegador del teléfono funciona bien)
2. **Importar** → elige el archivo → ajusta escala si hace falta

> 💡 **Tip Samsung**: con **DeX** (móvil + monitor/televisor) o con el **S Pen**
> tendrás mejor control al editar en Tinkercad.

---

## 🖥️ Opción 2: Claude Code en tu PC, controlando tu S25 Ultra

Si prefieres trabajar desde computadora, Claude Code puede **manejar tu
teléfono** y hacer el trabajo directamente (abrir Tinkercad, mover formas,
etc.):

- **zerotap / android-mcp-server** — app en el S25 Ultra, Claude Code en el
  PC se conecta por WiFi y controla todo (sin ADB ni root):
  ```bash
  claude mcp add zerotap -- npx mcp-remote http://TU_IP:8485/mcp --allow-http
  ```
- **claude-in-android** — MCP server open-source vía ADB (USB):
  ```bash
  claude mcp add --transport stdio android -- npx -y claude-in-android
  ```

Con esto puedes decirle: *"Abre Tinkercad, crea un cilindro, ponle un
agujero en el centro..."* y verás el teléfono haciendo los clics solo.

---

## 🎓 Cómo "hablarle" para un buen diseño 3D

Sé específico — el modelo funciona mejor con datos concretos:

| Mal ejemplo | Buen ejemplo |
|---|---|
| "Hazme una caja" | "Caja hueca de 60×40×20 mm con pared de 2 mm" |
| "Un engranaje" | "Engranaje de 12 dientes, Ø80 mm, 8 mm alto, agujero Ø20 mm" |
| "Una tapa" | "Tapa que encaje: 60.8×40.8 mm, 3 mm de grosor" |

### Ideas de proyectos Tinkercad que la IA puede generarte:
- ⚙️ Engranajes con distintos dientes (para un mecanismo)
- 📦 Cajas, estuches y soportes (para impresión 3D)
- 🏠 Maquetas de casas (caja + techo + ventanas = importar y combinar)
- 🔑 Llaveros con tu nombre (texto en Tinkercad + pieza generada)
- 🧩 Piezas de ensamble (base + tapa a medida, como el ejemplo)

---

## 🛡️ Seguridad

- Da a la IA solo los permisos que necesita (en Termux, corre los comandos
  que entiendas; no pegues nada de fuentes desconocidas)
- Revisa siempre los `.stl` antes de imprimir o entregar (usa las imágenes
  de vista previa: `python3 render.py pieza.stl vista.png "Mi pieza"`)
- Para compras/descargas de APK, usa siempre las tiendas oficiales

---

## 📁 Archivos de esta carpeta

```
tinkercad-ai/
├── generar.py        ← generador de modelos 3D (el "cerebro" de la IA)
├── render.py         ← crea imagen de vista previa de cualquier .stl
├── engranaje.stl     ← ejemplo listo para Tinkercad
├── caja_base.stl     ← ejemplo listo para Tinkercad
├── caja_tapa.stl     ← ejemplo listo para Tinkercad
├── engranaje.png     ← vista previa
├── caja_base.png     ← vista previa
└── caja_tapa.png     ← vista previa
```
