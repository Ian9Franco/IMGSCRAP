# Guía de Desarrollo — scrap.io (v4.0)

Este documento detalla la arquitectura técnica de **scrap.io**, orientada a desarrolladores que deseen extender la funcionalidad de la plataforma.

---

## 🏗️ Arquitectura General

La aplicación utiliza un stack moderno de alto rendimiento:
*   **Lanzador (`main.py`)**: Script orquestador que gestiona los procesos del backend y frontend simultáneamente.
*   **Backend (`FastAPI`)**: Motor de procesamiento asíncrono en Python.
*   **Frontend (`Next.js 14`)**: Interfaz SPA con Tailwind CSS y Framer Motion para animaciones.
*   **IA de Visión (`CLIP`)**: Procesamiento local de imágenes.
*   **IA de Lenguaje (`Gemini 1.5 Flash`)**: Motor de generación de contenido via API.

---

## 📂 Componentes del Backend

### 1. Sistema de Logs (`agent_logger.py`)
Implementa un logger global thread-safe que alimenta la **Agent Console** en el frontend.
*   **Uso**: `agent_log.log(source, message, level)`
*   **Observabilidad**: Permite al usuario ver el "Chain of Thought" de la IA y los tiempos de respuesta de los servicios externos.

### 2. Extractor de Propiedades (`property_extractor.py`)
Especializado en el parseo de HTML complejo.
*   **Heurísticas**: Detecta automáticamente si un sitio usa WordPress (temas como RealHomes) y aplica selectores específicos.
*   **Fallback Logic**: Si los metadatos `og:tags` faltan, escanea el DOM buscando el título de la página y el primer párrafo descriptivo largo.
*   **Localidad**: Incluye un motor de detección de localidades (Ramos Mejía, Morón, etc.) para limpiar y separar la zona de la dirección.

### 3. Generador de Copys (`copy_generator.py`)
Gestiona la lógica de redacción inteligente.
*   **Prompt Engineering**: Construye instrucciones dinámicas basadas en el nicho (Inmobiliaria, Gastronomía, Ecommerce).
*   **Modo Híbrido**: Si la API de Gemini falla o no está configurada, activa automáticamente un generador de plantillas local para asegurar que el usuario siempre tenga un resultado.
*   **Optimización**: El modelo `gemini-1.5-flash-latest` está pre-configurado para minimizar la latencia.

### 4. Clasificador de Imágenes (`image_classifier.py`)
Utiliza el modelo **CLIP (ViT-B/32)**.
*   **Performance**: Los pesos del modelo se cargan en un hilo separado al inicio para no bloquear la interfaz.
*   **Auto-Download**: El sistema utiliza `sentence-transformers`, que gestiona la descarga automática del modelo `ViT-B-32` en el primer uso. El modelo se cachea en la carpeta de usuario (habitualmente `~/.cache/torch`).
*   **Filtrado Irrelevante**: Algoritmo que descarta fotos de mala calidad o logos basado en la distancia coseno contra etiquetas de control.

---

## 🎨 Componentes del Frontend

### 1. UI Dinámica
*   **Personalidades**: El estado `activeTab` cambia drásticamente el CSS (colores, sombras, iconos) entre el modo Manual y el Brain Mode.
*   **Skeleton Loaders**: Implementados con Framer Motion en `CopyPanel.tsx`, simulan la escritura staggered para mejorar la percepción de velocidad.

### 2. Hooks de Estado
*   `useScrapingJob.ts`: Orquestación de la sesión de descarga.
*   `useCopyGenerator.ts`: Gestión de metadatos técnicos y sincronización con el editor de IA.

---

## 🛠️ Desarrollo Local

### Instalación de Dependencias
```bash
# Backend
pip install fastapi uvicorn beautifulsoup4 pillow sentence-transformers torch python-docx google-generativeai

# Frontend
cd frontend && npm install
```

### Ejecución en Modo Debug
Para ver logs detallados en la terminal del sistema:
```bash
python main.py
```
*(Los servidores abrirán en los puertos 3000 y 8000 por defecto).*

---
* scrap.io Core Development Team - Abril 2026 *
