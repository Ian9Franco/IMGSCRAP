# Roadmap — scrap.io (v4.0 Beta)

## 🎯 Visión General
scrap.io ha evolucionado de un simple scraper de imágenes a un sistema de automatización de contenidos de extremo a extremo. La versión 4.0 marca la transición a una plataforma impulsada por IA (Brain Mode).

---

## ✅ Módulos Completados (v1.0 - v4.0)

### 🚀 Módulo 1: Core de Scraping
- [x] Estructura desacoplada FastAPI + Next.js.
- [x] Motor de extracción de imágenes multihilo.
- [x] Deduplicación global por hash (evita duplicados entre sesiones).
- [x] Soporte avanzado para WordPress (RealHomes) y sitios antiguos.

### 🧠 Módulo 2: Inteligencia Artificial (Brain Mode)
- [x] Integración de **CLIP local** para clasificación automática de ambientes.
- [x] Redacción de copys optimizados con **Gemini 1.5 Flash**.
- [x] **Smart Copy Editor**: Edición de texto mediante chat con la IA.
- [x] Auto-tagging inteligente durante la descarga.

### 💎 Módulo 3: Experiencia de Usuario & UX
- [x] **Skeleton Loaders Premium**: Feedback visual de "escritura" en tiempo real.
- [x] **Agent Console**: Terminal de logs para monitorear procesos técnicos.
- [x] **Exportación Inteligente**: Autogeneración de nombres de carpeta con seriales y versiones.
- [x] **Manual vs Brain Mode**: Interfaz dinámica que cambia colores y herramientas según el modo.

### 📄 Módulo 4: Documentación y Salida
- [x] Generación automática de documentos **Word (.docx)**.
- [x] Guardado persistente de metadatos en `property_data.json`.
- [x] Previsualización de texto enriquecido con edición manual.

---

## 🛠️ Próximos Pasos (En Desarrollo / Futuro)

### 🟢 Corto Plazo (v4.1 - v4.5)
- [ ] **Drag & Drop Reordering**: Permitir ordenar las fotos manualmente antes de generar el Word.
- [ ] **AI-Powered Image Selection**: La IA elige las mejores 10 fotos para Instagram automáticamente.
- [ ] **Soporte para Redes Sociales**: Botón de publicación directa o presets específicos para Reels/Stories.

### 🟡 Mediano Plazo (v5.0)
- [ ] **Empaquetado Nativo (.EXE)**: Convertir la aplicación en un ejecutable para Windows que no requiera consola ni instalaciones previas.
- [ ] **Multi-agente**: Un agente que navega la web para encontrar datos de la zona (colegios, transporte) y sumarlos al copy.
- [ ] **Editor de Imágenes Integrado**: Recorte (crop) y filtros básicos sin salir de la app.
- [ ] **Cloud Sync**: Sincronización opcional de sesiones en la nube.
- [ ] **SligLip Mode**: Reemplazar Clip por SligLip para clasificación de imágenes.

*Roadmap actualizado al 24 de Abril de 2026*