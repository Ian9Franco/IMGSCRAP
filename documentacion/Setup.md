# Guía de Instalación y Uso — scrap.io

La aplicación está dividida en un **Backend (FastAPI)** y un **Frontend (Next.js)**. Para asegurar el correcto funcionamiento de las funciones de IA y scraping, seguí estos pasos.

---

## 🛠️ 1. Preparación del Envío

### Requisitos Previos
*   **Python 3.10 o superior**: Asegurate de tenerlo instalado y agregado al PATH.
*   **Node.js 18 o superior**: Necesario para compilar la interfaz de Next.js.
*   **Git**: Para clonar el repositorio (opcional).

---

## 🚀 2. Instalación Paso a Paso

### Backend (Cerebro)
Abrí una terminal en la carpeta raíz del proyecto:
```powershell
cd backend
pip install -r requirements.txt
```

### Frontend (Interfaz)
Abrí otra terminal (o usá una nueva pestaña) en la raíz:
```powershell
cd frontend
npm install
```

---

## ⚡ 3. Ejecución Rápida

Para facilitar el inicio, contamos con un script lanzador en la raíz:
```powershell
python main.py
```
Este comando levantará ambos servidores automáticamente. 
*   **Frontend**: [http://localhost:3000](http://localhost:3000)
*   **Backend API**: [http://localhost:8000](http://localhost:8000)

---

## ⚙️ 4. Configuración Inicial

Una vez abierta la aplicación:
1.  Andá al icono de engranaje (Configuración) en la parte superior.
2.  **Base Directory**: Definí la carpeta donde querés que se guarden tus trabajos.
3.  **Gemini API Key**: Ingresá tu clave de Google AI Studio para habilitar la redacción inteligente.

---

## 🔄 5. Clonado en una Máquina Nueva

Si acabás de clonar el repositorio en una PC nueva, recordá:
1.  **Instalar dependencias**: Ejecutá los pasos de la Sección 2 (`pip install` y `npm install`).
2.  **Configurar de nuevo**: La API Key de Gemini y la carpeta base son locales de cada máquina. Configuralas desde la interfaz de la app.
3.  **Descarga de IA**: La primera vez que uses el **Brain Mode**, scrap.io descargará automáticamente el modelo CLIP (~350MB). No te asustes si la primera clasificación tarda un poquito más de lo normal mientras se baja el modelo.

---

## 💡 Tips de Uso
*   **Brain Mode**: Activá el switch de IA para que las fotos se clasifiquen solas al descargarse.
*   **Smart Extract**: Solo pegá la URL de la propiedad y esperá a que el panel izquierdo se complete automáticamente.
*   **Exportar**: Al terminar, usá el botón de exportar para mover todo a tu carpeta de clientes con el nombre ya formateado.

---
* scrap.io v4.0 Beta *
