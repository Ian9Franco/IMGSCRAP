import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from PIL import Image
from io import BytesIO
import threading
import time
import imagehash

class ImageScraper:
    def __init__(self, callback_progress=None, callback_thumbnail=None, callback_finished=None, min_resolution=(300, 300), use_ai=False, nicho="inmobiliaria"):
        self.callback_progress = callback_progress
        self.callback_thumbnail = callback_thumbnail
        self.callback_finished = callback_finished
        self.min_resolution = min_resolution
        self.use_ai = use_ai
        self.nicho = nicho
        self.is_running = False
        self._tag_counters = {}  # Cuenta cuántas fotos hay por cada tag: {"cocina": 2, "fachada": 1, ...}
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
        }

    def start_scraping(self, url, base_path, image_path):
        self.is_running = True
        self.thread = threading.Thread(target=self._scrape_logic, args=(url, base_path, image_path))
        self.thread.daemon = True
        self.thread.start()

    def stop_scraping(self):
        self.is_running = False

    def _get_best_image_url(self, img_tag, base_url):
        # Busco en estos atributos porque ahí suelen guardar las imágenes en alta resolución
        candidates = [
            img_tag.get('data-big'),
            img_tag.get('data-original'),
            img_tag.get('data-src-huge'),
            img_tag.get('data-src-large'),
            img_tag.get('data-src'),
            img_tag.get('srcset'),
            img_tag.get('src')
        ]
        
        best_url = None
        for candidate in candidates:
            if not candidate:
                continue
                
            # Si la imagen es responsive (srcset), me quedo con la última que casi siempre es la más grande
            if ',' in candidate and ' ' in candidate:
                parts = candidate.split(',')
                candidate = parts[-1].strip().split(' ')[0]
            
            if candidate:
                best_url = urljoin(base_url, candidate)
                break
                
        return best_url

    def _scrape_logic(self, url, base_path, image_path):
        try:
            if not os.path.exists(image_path):
                os.makedirs(image_path)

            response = requests.get(url, headers=self.headers, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            img_tags = soup.find_all('img')
            total = len(img_tags)
            
            if self.callback_progress:
                self.callback_progress(0, total, "Analizando imágenes...")

            seen_urls = set()
            seen_hashes = set()
            downloaded_count = 0

            for i, tag in enumerate(img_tags):
                if not self.is_running:
                    break
                
                img_url = self._get_best_image_url(tag, url)
                if not img_url:
                    continue
                    
                # Ignoro los vectores, logos e iconos chiquitos que no me sirven por nombre
                lower_url = img_url.lower()
                if lower_url.endswith('.svg') or 'logo' in lower_url or 'icon' in lower_url:
                    continue
                    
                if img_url in seen_urls:
                    continue
                seen_urls.add(img_url)

                try:
                    # Descargo la imagen de internet
                    img_resp = requests.get(img_url, headers=self.headers, timeout=10)
                    if img_resp.status_code == 200:
                        img_data = img_resp.content
                        img = Image.open(BytesIO(img_data))
                        
                        # Filtro por resolución mínima
                        width, height = img.size
                        if width < self.min_resolution[0] or height < self.min_resolution[1]:
                            # print(f"Imagen ignorada por tamaño: {width}x{height}")
                            continue

                        # Deduplicación perceptual (ImageHash)
                        img_hash = str(imagehash.average_hash(img))
                        if img_hash in seen_hashes:
                            # print(f"Imagen duplicada (hash) ignorada: {img_url}")
                            continue
                        seen_hashes.add(img_hash)

                        # Clasificación IA opcional (CLIP)
                        ai_tag = None
                        if self.use_ai:
                            try:
                                from image_classifier import classify_image, is_model_ready
                                if is_model_ready():
                                    result = classify_image(img, self.nicho)
                                    if result["is_garbage"]:
                                        # print(f"Imagen descartada por IA (basura): {img_url}")
                                        continue
                                    ai_tag = result["top_tag"]
                            except Exception as e:
                                print(f"[CLIP] Error en clasificación: {e}")

                        # Nombre del archivo: usa el ai_tag si hay IA activa, sino nombre genérico
                        if self.use_ai and ai_tag:
                            tag_slug = ai_tag.lower().replace(" ", "_")
                            count = self._tag_counters.get(tag_slug, 0) + 1
                            self._tag_counters[tag_slug] = count
                            filename = f"{tag_slug}_{count}.jpg"
                        else:
                            filename = f"image_{int(time.time() * 1000)}_{downloaded_count}.jpg"
                        filepath = os.path.join(image_path, filename)
                        
                        # La guardo con buena calidad para no perder detalles
                        if img.mode in ("RGBA", "P"):
                            img = img.convert("RGB")
                        
                        img.save(filepath, "JPEG", quality=95)
                        
                        # Genero una miniatura chiquita para que la interfaz cargue más rápido
                        thumb = img.copy()
                        thumb.thumbnail((100, 100))
                        
                        if self.callback_thumbnail:
                            self.callback_thumbnail(filepath, thumb, width, height, ai_tag)
                        
                        downloaded_count += 1
                            
                    if self.callback_progress:
                        self.callback_progress(i + 1, total, f"Analizando: {os.path.basename(img_url)[:20]}... ({downloaded_count} listas)")

                except Exception as e:
                    print(f"Error downloading {img_url}: {e}")

            if self.callback_finished:
                self.callback_finished("Completado con éxito" if self.is_running else "Cancelado por el usuario")

        except Exception as e:
            if self.callback_finished:
                self.callback_finished(f"Error: {str(e)}")
        finally:
            self.is_running = False
