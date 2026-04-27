# scrap.io — Automatización Inteligente de Contenidos (v4.5)

> [!NOTE]
> **Nota del Autor:** Estoy sumamente orgulloso del avance que estoy logrando con esta aplicación. La integración de modelos de IA locales y en la nube ha transformado por completo mi flujo de trabajo. Me entusiasma muchísimo ver cómo este proyecto sigue escalando y evolucionando.

![scrap.io Logo](https://img.icons8.com/fluency/96/bot.png)

**scrap.io** es una herramienta profesional diseñada para inmobiliarias y creadores de contenido que necesitan transformar una URL en un paquete publicitario completo en segundos. 

La aplicación automatiza el ciclo de vida del contenido: desde la extracción de imágenes y datos técnicos, hasta la clasificación con Inteligencia Artificial local y la redacción de copys optimizados con **Gemini 1.5 Flash** u **Ollama**.

---

## 🚀 Características Principales

### 🧠 Inteligencia Artificial de Vanguardia
*   **Brain Mode**: Activa un ecosistema de IA que clasifica fotos automáticamente (Cocina, Fachada, Baño, etc.) usando **CLIP** localmente.
*   **AI-Enhanced Extraction**: El motor seleccionado (Gemini, Gemma 3 o Phi-3) ayuda a limpiar y estructurar los datos técnicos extraídos de la web.
*   **Dual Engine (Local/Cloud)**: Capacidad de elegir entre **Ollama (Gemma 3 / Phi-3)** para redacción offline/privada o **Gemini 1.5 Flash** para máxima calidad.
*   **Edición Interactiva**: Chateá con la IA para ajustar el tono, longitud o emojis de tus publicaciones en tiempo real.

### 🔍 Extracción Potente (Smart Scraper)
*   **Multi-Portal**: Soporte avanzado para sitios complejos y WordPress (RealHomes, Olivieri, Zonaprop, etc.).
*   **Persistent URL**: El sistema guarda el link original para que puedas retomar cualquier sesión sin volver a copiar y pegar.
*   **Data Ingestion**: Extrae automáticamente precios, direcciones y características técnicas para alimentar a la IA.
*   **Deduplicación Global**: Evita descargar imágenes repetidas entre diferentes sesiones de trabajo.

### 💎 Experiencia de Usuario Premium
*   **Versionado de Documentos**: Guardado automático de versiones (V1, V2, V3...) en archivos Word (.docx) para no perder ningún borrador.
*   **Historial y Recuperación**: Carga sesiones antiguas y recupera automáticamente los metadatos y el link original.
*   **Skeleton Loaders**: Visualización dinámica de la redacción de la IA en tiempo real.
*   **Agent Console**: Terminal integrada para monitorear cada paso del proceso (extracción, logs de Gemini, tiempos de respuesta).
*   **Smart Folder Naming**: Organización automática con números de serie y versiones.

---

## 📂 Estructura de Documentación

Para profundizar en el uso y desarrollo de la plataforma:

*   [**Guía de Instalación**](./documentacion/Setup.md): Cómo poner en marcha scrap.io en tu máquina local.
*   [**Guía de Desarrollo**](./documentacion/readme_dev.md): Detalles técnicos sobre la arquitectura, el backend (FastAPI) y el frontend (Next.js).
*   [**Referencia de API**](./documentacion/API.md): Documentación de los endpoints del backend.
*   [**Guía de IA Local**](./documentacion/setup_ai_local.md): Cómo instalar Ollama y Phi-3 para redactar sin internet.
*   [**Roadmap de Proyecto**](./documentacion/roadmap.md): Estado actual del desarrollo y planes futuros.

---

## 🛠️ Requisitos del Sistema
*   **Python 3.10+** (para el cerebro del sistema).
*   **Node.js 18+** (para la interfaz moderna).
*   **Windows 10/11** (optimizado para el selector de archivos nativo).

---
*Versión 4.0.0-beta - Abril 2026*
