# Roadmap — IMG Scraper Pro

## Módulo 1 – Base y Scraping (Completado)
- [x] Estructura FastAPI + Next.js
- [x] Scraper de imágenes con BeautifulSoup
- [x] Descarga y guardado local
- [x] Deduplicación básica por hash perceptual

## Módulo 2 – Inteligencia y Persistencia (Completado)
- [x] Integración de CLIP (ViT-B/32) para clasificación
- [x] Auto-tagging por nicho (Inmobiliaria)
- [x] Generación de documentos Word (.docx)
- [x] Generación de Copy con GPT-4o-mini o Template Local

## Módulo 3 – Optimizaciones y UX (Completado)

### ✅ Optimizaciones de performance
- [x] **Cache de embeddings de texto CLIP**: los labels se calculan una sola vez.
- [x] **Procesamiento paralelo**: `ThreadPoolExecutor` para descargas.
- [x] **Deduplicación global entre sesiones**: `dedup_index.json` evita duplicados en toda la carpeta base.
- [x] **Estructura Organizada**: Las imágenes se guardan automáticamente en `recursos/fotos`.

### ✅ Mejoras de UX
- [x] **Exportación Inteligente**: Al mover una sesión a la carpeta destino, la app detecta el serial más alto (ej: 16) y renombra la carpeta al siguiente (ej: 17-Direccion-V1).
- [x] **Toast notifications** con `sonner`.
- [x] **Indicador visual de renombrado** (badge ✅).
- [x] **Contador de imágenes por tag IA** en sidebar.
- [x] **Copy se carga automáticamente** al recuperar una sesión.
- [x] **Boton "Limpiar Todo"**: para resetear la vista y permitir nueva auto-extracción.
- [x] **Vista Previa en Pantalla Completa**: click en imagen para ampliar (Lightbox).
- [x] **Filtros por Tag IA**: barra superior para filtrar la grilla por categoría (Fachada, Cocina, etc.).

### ✅ Mejoras de código
- [x] **Arquitectura modular**: `Sidebar`, `ImageGrid`, `CopyPanel` separados.
- [x] **Custom hooks**: `useScrapingJob`, `useCopyGenerator`, `useConfig`.
- [x] **Validación Pydantic**: `AppConfig` centralizado para manejar settings con tipos.
- [x] **Variable de entorno `API_BASE`**: configurada en `.env.local`.

## Módulo 4 – Multicho y Presets (Completado)

### ✅ Nichos adicionales
- [x] **Gastronomía**: clasificación IA específica y templates de copy (local/AI).
- [x] **Ecommerce**: clasificación IA específica y templates de copy (local/AI).

### ✅ Presets de Copy
- [x] **Multi-formato**: presets para Instagram/Facebook, Web y LinkedIn.
- [x] **Emojis automáticos**: adaptados según el nicho seleccionado.

---

## Próximos Pasos (Ideas Futuras)
- [ ] **Drag & Drop de orden**: reordenar imágenes antes de exportar el Word.
- [ ] **Editor de imagen básico**: crop/resize antes de guardar.
- [ ] **Soporte para más sitios**: optimizar extractores para portales específicos (Argenprop, Zonaprop, PedidosYa, etc.).