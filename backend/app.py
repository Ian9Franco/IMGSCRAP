from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os
import uuid
import threading
import shutil
import subprocess
import json
from scraper import ImageScraper
from image_classifier import load_model, is_model_ready, classify_image, NICHO_TAGS
from copy_generator import generate_copy
from document_generator import generate_property_doc
from property_extractor import extract_property_data

CONFIG_FILE = "config.json"
DEFAULT_BASE_DIR = "D:\\Dev\\imgscrap"

def get_config():
    if not os.path.exists(CONFIG_FILE):
        return {"base_dir": DEFAULT_BASE_DIR, "openai_api_key": ""}
    try:
        with open(CONFIG_FILE, "r") as f:
            config = json.load(f)
            return {
                "base_dir": config.get("BASE_DIR", DEFAULT_BASE_DIR),
                "openai_api_key": config.get("OPENAI_API_KEY", "")
            }
    except:
        return {"base_dir": DEFAULT_BASE_DIR, "openai_api_key": ""}

def set_config(new_dir: str, api_key: str = ""):
    data = {}
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                data = json.load(f)
        except:
            pass
    data["BASE_DIR"] = new_dir
    if api_key:
        data["OPENAI_API_KEY"] = api_key
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f)
    os.makedirs(new_dir, exist_ok=True)
    return data

os.makedirs(get_config()["base_dir"], exist_ok=True)  # Me aseguro de que mi carpeta base siempre exista

app = FastAPI(title="Image Scraper API")

# Cargo el modelo CLIP en background al arrancar para que esté listo cuando el usuario lo necesite
_clip_thread = threading.Thread(target=load_model, daemon=True)
_clip_thread.start()

# Configuro CORS para que mi frontend en Next.js se pueda conectar sin problemas
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Si lo fuera a subir a internet, acá pondría solo mi localhost, pero como es local lo dejo abierto
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Guardo acá temporalmente en memoria los procesos de extracción que están corriendo
jobs = {}

class ScrapeRequest(BaseModel):
    url: str
    dest_folder: str
    only_large: bool = False
    nicho: str = "inmobiliaria"   # nicho para el auto-tagging CLIP
    use_ai: bool = False          # activar clasificación IA (requiere modelo cargado)

class RenameRequest(BaseModel):
    old_path: str
    new_tag: str

class ExportRequest(BaseModel):
    property_name: str   # El nombre de la carpetita que voy a crear
    target_folder: str

class ConfigRequest(BaseModel):
    base_dir: str
    openai_api_key: str = ""

class CopyRequest(BaseModel):
    nicho: str
    data: dict
    property_folder: str

class ExtractRequest(BaseModel):
    url: str
    nicho: str = "inmobiliaria"

def start_scrape_job(job_id: str, url: str, dest_folder: str, only_large: bool, use_ai: bool, nicho: str):
    min_res = (600, 600) if only_large else (300, 300)
    scraper = ImageScraper(
        callback_progress=lambda curr, tot, msg: update_job_progress(job_id, curr, tot, msg),
        callback_thumbnail=lambda path, thumb, w, h, tag: add_job_image(job_id, path, w, h, tag),
        callback_finished=lambda msg: finish_job(job_id, msg),
        min_resolution=min_res,
        use_ai=use_ai,
        nicho=nicho,
    )
    jobs[job_id]["scraper"] = scraper
    # Le paso la misma ruta a los dos campos para que no me arme subcarpetas innecesarias
    scraper.start_scraping(url, dest_folder, dest_folder)

def update_job_progress(job_id: str, current: int, total: int, message: str):
    if job_id in jobs:
        jobs[job_id]["current"] = current
        jobs[job_id]["total"] = total
        jobs[job_id]["message"] = message

def add_job_image(job_id: str, path: str, width: int, height: int, ai_tag: str | None = None):
    if job_id in jobs:
        jobs[job_id]["images"].append({
            "path": path,
            "width": width,
            "height": height,
            "ai_tag": ai_tag,
        })

def finish_job(job_id: str, message: str):
    if job_id in jobs:
        jobs[job_id]["is_running"] = False
        jobs[job_id]["message"] = message

@app.get("/api/config")
def api_get_config():
    return get_config()

@app.post("/api/config")
def api_set_config(req: ConfigRequest):
    new_config = set_config(req.base_dir, req.openai_api_key)
    return {"status": "success", "config": new_config}

@app.get("/api/ai/status")
def api_ai_status():
    """Informa si el modelo CLIP ya está cargado y listo para clasificar."""
    return {"ready": is_model_ready()}

@app.get("/api/ai/nichos")
def api_ai_nichos():
    """Devuelve los nichos disponibles para el auto-tagging."""
    return {"nichos": list(NICHO_TAGS.keys())}

@app.post("/api/scrape/start")
def api_start_scrape(req: ScrapeRequest):
    job_id = str(uuid.uuid4())
    jobs[job_id] = {
        "is_running": True,
        "current": 0,
        "total": 0,
        "message": "Inicializando...",
        "images": [],
        "scraper": None
    }
    
    thread = threading.Thread(target=start_scrape_job, args=(job_id, req.url, req.dest_folder, req.only_large, req.use_ai, req.nicho))
    thread.daemon = True
    thread.start()
    
    return {"job_id": job_id}

@app.get("/api/scrape/status/{job_id}")
def api_get_status(job_id: str):
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = jobs[job_id]
    # No devuelvo el objeto scraper entero, solo los datos que me importan para la interfaz
    return {
        "is_running": job["is_running"],
        "current": job["current"],
        "total": job["total"],
        "message": job["message"],
        "images": job["images"]
    }

@app.post("/api/scrape/stop/{job_id}")
def api_stop_scrape(job_id: str):
    if job_id in jobs and jobs[job_id]["scraper"]:
        jobs[job_id]["scraper"].stop_scraping()
        jobs[job_id]["is_running"] = False
        jobs[job_id]["message"] = "Cancelado por el usuario"
        return {"status": "stopped"}
    raise HTTPException(status_code=404, detail="Job not found")

@app.post("/api/images/rename")
def api_rename_image(req: RenameRequest):
    if not os.path.exists(req.old_path):
        raise HTTPException(status_code=404, detail="Archivo original no encontrado")
        
    dir_name = os.path.dirname(req.old_path)
    ext = os.path.splitext(req.old_path)[1]
    
    base_new_name = req.new_tag.lower().replace(" ", "_")
    new_name = f"{base_new_name}{ext}"
    new_path = os.path.join(dir_name, new_name)
    
    counter = 1
    while os.path.exists(new_path):
        new_name = f"{base_new_name}_{counter}{ext}"
        new_path = os.path.join(dir_name, new_name)
        counter += 1
        
    try:
        os.rename(req.old_path, new_path)
        return {"old_path": req.old_path, "new_path": new_path, "new_name": new_name}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al renombrar: {str(e)}")

@app.post("/api/copy/generate")
def api_generate_copy(req: CopyRequest):
    config = get_config()
    api_key = config.get("openai_api_key", "")
    # Si no hay API key usa el template local automáticamente (no bloquea)
    copy_text = generate_copy(req.nicho, req.data, api_key)
    
    if not copy_text.startswith("⚠️"):
        folder_path = os.path.join(config["base_dir"], req.property_folder)
        if os.path.exists(folder_path):
            generate_property_doc(
                folder_path,
                req.data.get("title", "Propiedad"),
                copy_text,
                req.data.get("features", [])
            )
    return {"copy": copy_text}

@app.post("/api/property/extract")
def api_extract_property(req: ExtractRequest):
    """Extrae metadatos (título, precio, ubicación, características) de la URL de la propiedad."""
    data = extract_property_data(req.url, req.nicho)
    return data

@app.post("/api/images/export")
def api_export_images(req: ExportRequest):
    source_folder = os.path.join(get_config()["base_dir"], req.property_name)
    if not os.path.exists(source_folder):
        raise HTTPException(
            status_code=404,
            detail=f"Carpeta origen no encontrada: {source_folder}"
        )
    try:
        os.makedirs(req.target_folder, exist_ok=True)
        moved_count = 0
        for item in os.listdir(source_folder):
            s = os.path.join(source_folder, item)
            d = os.path.join(req.target_folder, item)
            if os.path.isfile(s):
                shutil.move(s, d)
                moved_count += 1
        return {"status": "success", "moved": moved_count, "target": req.target_folder}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al exportar: {str(e)}")

@app.get("/api/browse/folder")
def api_browse_folder():
    """Abre el explorador de carpetas nativo de Windows y devuelve la ruta elegida."""
    try:
        ps_script = (
            "Add-Type -AssemblyName System.Windows.Forms; "
            "$dlg = New-Object System.Windows.Forms.FolderBrowserDialog; "
            "$dlg.Description = 'Seleccioná la carpeta'; "
            "$dlg.UseDescriptionForTitle = $true; "
            "$dlg.ShowNewFolderButton = $true; "
            "if ($dlg.ShowDialog() -eq [System.Windows.Forms.DialogResult]::OK) "
            "{ Write-Output $dlg.SelectedPath }"
        )
        result = subprocess.run(
            ["powershell", "-NoProfile", "-NonInteractive", "-Command", ps_script],
            capture_output=True, text=True, timeout=120, encoding="utf-8"
        )
        path = result.stdout.strip()
        return {"path": path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/images/serve")
def api_serve_image(path: str):
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Imagen no encontrada")
    return FileResponse(path)

@app.get("/api/images/history")
def api_get_history():
    base_dir = get_config()["base_dir"]
    if not os.path.exists(base_dir):
        return {"folders": []}
    folders = sorted([
        item for item in os.listdir(base_dir)
        if os.path.isdir(os.path.join(base_dir, item))
    ])
    return {"folders": folders}

@app.get("/api/images/history/folder")
def api_get_history_folder(name: str):
    folder_path = os.path.join(get_config()["base_dir"], name)
    if not os.path.exists(folder_path):
        raise HTTPException(status_code=404, detail=f"Carpeta no encontrada: {folder_path}")
    images = sorted([
        os.path.join(folder_path, item)
        for item in os.listdir(folder_path)
        if item.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))
    ])
    return {"images": images, "folder": folder_path}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=False)
