# Documentación de la API Backend

El backend está construido con **FastAPI** y se ejecuta en `http://localhost:8000`.

## Endpoints

### 1. Iniciar Extracción
**`POST /api/scrape/start`**
Inicia el proceso de descarga de imágenes en segundo plano.
- **Body**:
  ```json
  {
    "url": "https://ejemplo.com/propiedad",
    "dest_folder": "D:/MisPropiedades/Malabia648"
  }
  ```
- **Response**: `{ "job_id": "uuid-string" }`

### 2. Estado del Trabajo
**`GET /api/scrape/status/{job_id}`**
Devuelve el progreso del trabajo y la lista de fotos descargadas.
- **Response**:
  ```json
  {
    "is_running": true,
    "current": 5,
    "total": 10,
    "message": "Descargando: imagen.jpg...",
    "images": ["D:/.../image_1.jpg", "D:/.../image_2.jpg"]
  }
  ```

### 3. Renombrar Imagen
**`POST /api/images/rename`**
Cambia el nombre físico de una foto en el disco duro.
- **Body**:
  ```json
  {
    "old_path": "D:/.../image_1.jpg",
    "new_tag": "Cocina"
  }
  ```
- **Response**: `{ "old_path": "...", "new_path": "...", "new_name": "cocina.jpg" }`

### 4. Servir Imágenes (Estático)
**`GET /api/images/serve?path=D:/ruta/absoluta.jpg`**
Sirve la imagen para que el frontend pueda visualizarla como miniatura.
