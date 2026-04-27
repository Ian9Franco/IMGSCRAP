# Referencia de API — scrap.io
## v4.5 (Abril 2026)

El backend de scrap.io expone una API REST construida con FastAPI en `http://localhost:8000`.

---

## 📸 1. Imágenes y Scraping

### Iniciar Scrapeo
`POST /api/scrape/start`
Inicia la descarga y clasificación asíncrona.
*   **Body**: `{ "url": str, "dest_folder": str, "use_ai": bool, "nicho": str }`
*   *Nota*: Crea automáticamente `property_data.json` con la URL para persistencia.

### Estado del Scrapeo
`GET /api/scrape/status/{job_id}`
Devuelve el progreso y las imágenes encontradas hasta el momento.

---

## ✍️ 2. Inteligencia Artificial (Copy)

### Extraer Metadatos (AI-Enhanced)
`POST /api/property/extract`
Analiza una URL y extrae Título, Precio, Dirección y Características.
*   **Body**: `{ "url": str, "nicho": str, "engine": str }`
*   *Engine*: Puede ser `cloud_gemini`, `local_phi3` o `local_gemma3` para mejorar la extracción con IA.

### Generar Copy
`POST /api/copy/generate`
Genera una publicación completa y guarda automáticamente un `.docx` versionado.
*   **Body**: `{ "nicho": str, "data": dict, "property_folder": str, "engine": str }`

### Cargar Copy y Versiones
`GET /api/copy/load`
Carga el contenido de una carpeta.
*   **Params**: `folder_name: str`, `filename: str (opcional)`
*   **Response**: `{ "copy": str, "versions": list[str], "filename": str, "raw_data": dict }`

### Editar con IA
`POST /api/copy/edit`
Modifica un texto existente basado en una instrucción del usuario.
*   **Body**: `{ "current_copy": str, "prompt": str, "engine": str }`

### Guardar Documento (Versioning)
`POST /api/copy/save-docx`
Guarda el estado actual del copy en un archivo Word.
*   *Lógica*: Si ya existe `copy_propiedad.docx`, genera `copy_propiedad_V2.docx`, etc.

---

## 📂 3. Sistema y Archivos

### Sugerir Nombre de Carpeta
`GET /api/folder/suggest?address=CALLE`
Calcula el siguiente serial y versión para una nueva propiedad.

### Abrir Selector Nativo
`GET /api/browse/folder`
Abre el diálogo de carpetas de Windows.

### Consultar Logs
`GET /api/logs`
Devuelve los eventos del sistema para la Agent Console.

---
* scrap.io API Docs v4.5 *
