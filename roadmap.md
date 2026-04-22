# IMG Scraper Pro — Roadmap

> **Visión:** "Extraé y generá contenido listo para redes en segundos."
> No es un scraper con cositas. Es un procesador inteligente de contenido.

---

## Filosofía del producto

- El usuario quiere apretar un botón y tener imágenes listas. **Si todavía tiene que pensar, la app no terminó el trabajo.**
- No vendas "scraper de imágenes". Vendé **"imágenes listas para usar"**. Es otra liga.
- No uses 10 modelos. Usá 3 cosas bien hechas.

---

## Módulo 1 — Scraping + Procesamiento de imágenes

### ✅ Fase 1 – De herramienta a usable *(completada)*

- [x] Deduplicación automática por hash perceptual (ImageHash)
- [x] Filtro por resolución mínima (300px por defecto)
- [x] Selector "Solo imágenes grandes" (+600px)
- [x] Preview ordenado por calidad (mayor resolución primero)
- [x] Badge de dimensiones al hacer hover en cada foto

### ✅ Fase 2 – IA mínima viable *(completada)*

- [x] Integrar SigLIP/CLIP vía `sentence-transformers` (modelo `clip-ViT-B-32`)
- [x] Carga del modelo en background al arrancar el backend (sin bloquear el inicio)
- [x] Clasificación binaria: **relevante vs basura** — descartar logos, banners, íconos
- [x] Auto-tagging básico por nicho (inmobiliaria, gastronomía, ecommerce)
- [x] El tag se muestra como badge en cada imagen de la grilla
- [x] Selector de nicho en la sidebar
- [x] Indicador de estado del modelo (CARGANDO... → LISTO)
- [x] El filtrado IA es opt-in por checkbox (se puede usar sin IA)

### 🟠 Fase 3 – Renombrado inteligente

- [ ] Renombrar automáticamente usando tags de IA + contexto del sitio (title, H1)
- [ ] De `img_9384.jpg` a `casa-cocina-1.jpg`

### 🔴 Fase 4 – Modo vertical (escalado por nicho)

Elegir **un solo nicho** primero:

| Nicho | Tags clave |
|---|---|
| Inmobiliaria | fachada, cocina, baño, dormitorio, jardín |
| Gastronomía | plato, detalle, ambiente, bebida |
| Ecommerce | producto, detalle, lifestyle |

### 🔥 Feature estrella — Modo Auto

Un solo botón: **"Procesar automáticamente"**. Hace todo:
1. Filtra basura
2. Elimina duplicados
3. Clasifica y tagea
4. Renombra

Sin preguntas.

---

## Módulo 2 — Generador de Copy

### ✅ Fase 1 – Integración básica *(completada)*

- [x] Módulo nuevo "Generador de Copy" en el backend (`copy_generator.py`)
- [x] Integración con OpenAI GPT-4o-mini
- [x] Prompt estructurado (Hook, Descripción, Specs, CTA)
- [x] Exportación automática a Word (.docx)
- [x] Interfaz de usuario con visor de copy y botón de copiar

**Estructura de prompt fija:**
```
Actuá como especialista en marketing {nicho}.
Generá un copy para Instagram con:
1. Hook inicial (1 línea)
2. Descripción breve
3. Lista de características
4. Cierre con CTA
5. Hashtags

Datos: tipo={tipo}, ubicación={ubicacion}, precio={precio}, features={features}
```

**Flujo de usuario:**
`Scrapeás → Extraés datos → "Generar copy" → Seleccionás nicho → Click → Magia`

### 🟠 Fase 2 – Templates por nicho

- [ ] Inmobiliaria
- [ ] Gastronomía

### 🔴 Fase 3 – Multi-copy y presets

- [ ] Versión Instagram / Facebook / Web desde el mismo input
- [ ] Presets guardados por usuario

### 🔥 Feature diferenciador — Copy + imágenes alineadas

- imagen 1 → fachada → el texto menciona la ubicación
- imagen 2 → cocina → el texto menciona la cocina

Posible con los tags generados por IA en Módulo 1.

---

## Lo que NO hacer

- ❌ Mezclar copy dentro del scraper
- ❌ Dejar que el usuario escriba prompts
- ❌ Captions largos tipo GPT para clasificar imágenes
- ❌ LLM local para clasificación de imágenes
- ❌ Clasificación hiper compleja
- ❌ UI con 200 opciones

---

## Transformación del producto

| Antes | Después |
|---|---|
| Descargo imágenes | Proceso y clasifico imágenes automáticamente |
| Renombro a mano | Renombrado automático con IA |
| Escribo copy | Copy generado y listo para pegar |
| Exporto a mano | DOCX armado automáticamente |