# Referencia de API — scrap.io

El backend de scrap.io expone una API REST construida con FastAPI en `http://localhost:8000`.

---

## 📸 1. Imágenes y Scraping

### Iniciar Scrapeo
`POST /api/scrape/start`
Inicia la descarga y clasificación asíncrona.
*   **Body**: `{ "url": str, "dest_folder": str, "use_ai": bool, "nicho": str }`

### Estado del Scrapeo
`GET /api/scrape/status/{job_id}`
Devuelve el progreso y las imágenes encontradas hasta el momento.

### Clasificación Retroactiva
`POST /api/images/classify-existing`
Clasifica imágenes que ya están en el disco (útil para sesiones antiguas).

---

## ✍️ 2. Inteligencia Artificial (Copy)

### Extraer Metadatos
`POST /api/property/extract`
Analiza una URL y extrae Título, Precio, Dirección y Características.
*   **Response**: `{ "title": str, "price": str, "features": list, ... }`

### Generar Copy
`POST /api/copy/generate`
Genera una publicación completa usando Gemini o Plantillas Locales.
*   **Body**: `{ "nicho": str, "data": dict, "property_folder": str }`

### Editar con IA
`POST /api/copy/edit`
Modifica un texto existente basado en una instrucción del usuario.
*   **Body**: `{ "current_copy": str, "prompt": str }`

---

## 📂 3. Sistema y Archivos

### Sugerir Nombre de Carpeta
`GET /api/folder/suggest?address=CALLE`
Calcula el siguiente serial y versión para una nueva propiedad.

### Abrir Selector Nativo
`GET /api/browse/folder`
Abre el diálogo de carpetas de Windows (via PowerShell).

### Consultar Logs (Real-time)
`GET /api/logs`
Devuelve los últimos eventos del sistema para la Agent Console.

---
* scrap.io API Docs v4.0 *
