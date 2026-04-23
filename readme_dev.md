# Guía de Desarrollo - IMG Scraper Pro

Este documento detalla el funcionamiento interno de la aplicación, su arquitectura y los componentes técnicos que la integran.

## Descripción General
**IMG Scraper Pro** es una herramienta de escritorio diseñada para automatizar la extracción, organización y exportación de imágenes desde sitios web. Está construida con una arquitectura desacoplada: un **backend** potente en Python y un **frontend** moderno en React/Next.js, todo empaquetado como una aplicación nativa mediante `pywebview`.

---

## Cómo funciona (Arquitectura)
La aplicación utiliza un modelo cliente-servidor local:
1.  **Lanzador (main.py):** Orquestador inicial que levanta los servicios de backend y frontend en hilos separados y abre la ventana principal.
2.  **Comunicación:** El frontend se comunica con el backend mediante una API REST (FastAPI).
3.  **Procesamiento Asíncrono:** La descarga de imágenes se realiza en hilos (threads) secundarios para no bloquear la interfaz de usuario.
4.  **Persistencia:** La configuración (como la carpeta base) se guarda en un archivo `config.json` local.

---

## Componentes del Backend (Python)

### 1. `main.py` (Entry Point)
Es el punto de entrada de la aplicación. Sus responsabilidades incluyen:
- Iniciar el servidor de **FastAPI** (`app.py`).
- Iniciar el servidor de desarrollo de **Next.js** (o servir la build).
- Crear y gestionar la ventana de escritorio usando `pywebview`.
- Asegurar el cierre limpio de todos los procesos secundarios al salir.

### 2. `backend/app.py` (API REST & Orquestador)
El corazón lógico del sistema. Utiliza **FastAPI** para exponer endpoints que el frontend consume:
- **Gestión de Scrapeo:** Inicia, detiene y consulta el estado de las tareas de extracción.
- **Explorador de Archivos:** Implementa un selector de carpetas nativo mediante scripts de PowerShell.
- **Gestión de Imágenes:** Endpoints para renombrar archivos (evitando duplicados) y servirlos localmente.
- **Exportación:** Lógica para mover archivos procesados a carpetas de destino final.

### 3. `backend/scraper.py` (Lógica de Extracción)
Contiene la clase `ImageScraper`, encargada de:
- Analizar el HTML de las URLs usando **BeautifulSoup**.
- Identificar imágenes de alta resolución (buscando en atributos como `srcset`, `data-src`, etc.).
- Filtrar contenido irrelevante (SVG, iconos, logos).
- Descargar y convertir imágenes a formato JPEG usando **Pillow (PIL)** para optimizar espacio y compatibilidad.
- Generar miniaturas (thumbnails) en tiempo real para la previsualización.

### 4. `backend/document_generator.py` (Generador de Documentos)
Un componente especializado que utiliza `python-docx` para:
- Crear documentos de Microsoft Word (`.docx`).
- Formatear automáticamente títulos, listas de características y descripciones extraídas.
- Guardar estos reportes junto a las imágenes descargadas.

---

## Componentes del Frontend (Next.js)

El frontend es una Single Page Application (SPA) moderna enfocada en la experiencia de usuario (UX):

-   **Tecnologías:** Next.js, TypeScript y Tailwind CSS.
-   **Interfaz:** Diseño premium, minimalista y monocromático.
-   **Dashboard:** Un panel central que muestra el progreso de descarga con barras de estado y miniaturas dinámicas.
-   **Sidebar:** Navegación persistente entre los modos de "Extracción", "Historial" y "Configuración".
-   **Configuración Dinámica:** Permite al usuario cambiar la ruta base de almacenamiento global de la app sin reiniciar.

---

## Flujo de Trabajo Típico
1.  El usuario ingresa una URL y selecciona una carpeta.
2.  `app.py` recibe la petición e instancia un `ImageScraper` en un hilo nuevo.
3.  `scraper.py` descarga las imágenes, las convierte y las guarda.
4.  El frontend consulta `/api/scrape/status` periódicamente para actualizar la UI.
6.  **Exportación:** Al mover a la carpeta final, el sistema calcula automáticamente el siguiente número de serie para mantener el orden.

---

## Estructura de Sesión y Exportación

### Carpeta de Sesión (Local)
Cada vez que se inicia un scrapeo, se crea una carpeta con la siguiente estructura:
- `recursos/fotos/`: Contiene todas las imágenes descargadas y procesadas (.jpg).
- `copy_propiedad.docx`: Documento Word con la información de la propiedad.
- `copy_propiedad.txt`: Versión en texto plano del copy para carga rápida en la app.

### Lógica de Exportación (Smart Numbering)
Al exportar una sesión a una carpeta de destino final, la aplicación aplica una lógica de nomenclatura profesional:
1. **Escaneo de Destino:** Analiza la carpeta destino en busca de carpetas que comiencen con números (ej: `15-...`, `16-...`).
2. **Cálculo de Serial:** Determina el número más alto y le suma 1 (ej: `17`).
3. **Renombrado Automático:** Mueve la sesión completa y la renombra siguiendo el patrón `NN-Direccion-V1`.
