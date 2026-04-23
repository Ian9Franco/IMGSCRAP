# Guía de Desarrollo - AGENT.IO

Este documento detalla el funcionamiento interno de la aplicación, su arquitectura y los componentes técnicos que la integran.

## Descripción General
**AGENT.IO** es una plataforma de automatización de contenidos inmobiliarios y comerciales. Combina la extracción masiva de imágenes con Inteligencia Artificial para clasificar fotos, extraer metadatos de propiedades y generar copys publicitarios optimizados.

---

## Arquitectura del Sistema
La aplicación utiliza un modelo cliente-servidor local desacoplado:
1.  **Lanzador (main.py):** Orquestador que levanta el backend (FastAPI) y el frontend (Next.js) en hilos separados.
2.  **Backend (Python):** Gestiona el procesamiento pesado (scraping, IA, manejo de archivos).
3.  **Frontend (React/Next.js):** Interfaz de usuario moderna con dos personalidades dinámicas: **Manual** y **Brain**.
4.  **IA Local (CLIP):** Modelo de visión artificial cargado en memoria para clasificar imágenes sin depender de la nube.
5.  **IA en la Nube (Gemini):** Integración con Google Generative AI para redacción creativa y edición de texto.

---

## Componentes del Backend (Python)

### 1. `app.py` (El Orquestador API)
Es el núcleo de comunicación. Define todos los endpoints REST que consume el frontend.
*   **Gestión de Jobs:** Maneja el estado de las tareas de scraping mediante un diccionario en memoria (`jobs`).
*   **Nuevos Endpoints IA:** Incluye `/api/images/classify-existing` para procesamiento retroactivo y `/api/copy/edit` para edición interactiva con Gemini.
*   **Browser de Carpetas:** Implementa un bridge con PowerShell para abrir selectores de carpetas nativos de Windows.

### 2. `scraper.py` (Extracción de Imágenes)
Encargado de la "fuerza bruta" del scraping.
*   **Identificación:** Busca imágenes en etiquetas `<img>`, `<a>` y atributos `srcset` o `data-src`.
*   **Optimización:** Convierte todo a `.jpg` (RGB) y genera miniaturas para la UI.
*   **Integración CLIP:** Si el modo IA está activo, llama a `image_classifier.py` durante la descarga para descartar basura y asignar etiquetas.

### 3. `image_classifier.py` (Visión Artificial)
Gestiona el modelo **CLIP (Contrastive Language-Image Pretraining)**.
*   **Carga Lazy:** El modelo (~350MB) se descarga la primera vez y se mantiene en memoria.
*   **Clasificación por Nicho:** Utiliza similitud coseno para comparar imágenes con etiquetas de texto (ej: "Fachada", "Cocina", "Baño").
*   **Filtrado de Relevancia:** Descarta automáticamente logos, banners y capturas de pantalla si su "score" de irrelevancia es alto.

### 4. `copy_generator.py` (Redacción con IA)
El cerebro creativo de la aplicación.
*   **Modo Gemini:** Utiliza el modelo `gemini-1.5-flash` para generar publicaciones con formato Markdown, hashtags y emojis.
*   **Modo Offline:** Si no hay API Key configurada, utiliza un motor de plantillas local (`local_templates`) para generar un copy básico pero funcional.

### 5. `property_extractor.py` (Extracción de Datos)
Scraper especializado en capturar la información técnica de la propiedad.
*   **Scraping Selectivo:** Extrae Título, Precio, Ubicación y Características (ambientes, m2, etc.) directamente del HTML de la URL.
*   **Normalización:** Limpia y formatea los datos para que el usuario no tenga que escribirlos manualmente en el Generador de Copy.

### 6. `document_generator.py` (Manejo de Documentos)
*   **Word (.docx):** Crea documentos profesionales con formato enriquecido para exportación.
*   **Texto (.txt):** Guarda una versión plana del copy para permitir la previsualización y edición rápida en la aplicación.

### 7. `config_manager.py` (Persistencia)
Gestiona el archivo `config.json`.
*   Almacena la ruta del directorio base y la API Key de Gemini de forma persistente.

---

## Componentes del Frontend (Next.js)

### Modos de Interfaz
AGENT.IO cambia su comportamiento y estética según el modo seleccionado:

1.  **Manual Mode (Gris/Naranja):** Enfocado en la extracción pura y la gestión de sesiones históricas.
2.  **Brain Mode (Azul Eléctrico):** Activa las funciones de IA. Cambia la paleta de colores y habilita el Filtro IA y el Generador de Copy.

### Hooks Clave
*   `useScrapingJob.ts`: Controla el ciclo de vida de la extracción y ahora gestiona la **clasificación retroactiva** automática.
*   `useCopyGenerator.ts`: Maneja el estado de los metadatos de la propiedad y la comunicación con el editor de Gemini.

---

## Estructura de Sesión y Exportación

### Jerarquía de Carpetas
Cada sesión de trabajo se organiza así:
- `recursos/fotos/`: Imágenes descargadas, ya clasificadas y renombradas.
- `property_data.json`: Datos técnicos crudos de la propiedad (permite regenerar copys).
- `copy_propiedad.txt`: Copy actual para visualización.
- `copy_propiedad.docx`: Archivo final listo para enviar al cliente.

### Lógica de Exportación (Smart Serial)
Al hacer clic en **Exportar Sesión**, el backend:
1.  Busca el número de serie más alto en la carpeta de destino elegida.
2.  Calcula el siguiente serial (ej: de `10-` a `11-`).
3.  Crea la nueva estructura de carpetas y mueve únicamente lo esencial (fotos y documento Word).

---

## Guía de Instalación para Desarrolladores

1.  **Requisitos:** Python 3.10+, Node.js 18+.
2.  **Backend:**
    ```bash
    pip install fastapi uvicorn beautifulsoup4 pillow sentence-transformers torch python-docx google-generativeai
    ```
3.  **Frontend:**
    ```bash
    cd frontend
    npm install
    ```
4.  **Ejecución:**
    ```bash
    python main.py
    ```

---
*Documentación actualizada al 23 de Abril de 2026 - AGENT.IO Core Team*
