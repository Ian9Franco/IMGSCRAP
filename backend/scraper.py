import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from PIL import Image
from io import BytesIO
import threading
import time

class ImageScraper:
    def __init__(self, callback_progress=None, callback_thumbnail=None, callback_finished=None):
        self.callback_progress = callback_progress
        self.callback_thumbnail = callback_thumbnail
        self.callback_finished = callback_finished
        self.is_running = False
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
            downloaded_count = 0

            for i, tag in enumerate(img_tags):
                if not self.is_running:
                    break
                
                img_url = self._get_best_image_url(tag, url)
                if not img_url:
                    continue
                    
                # Ignoro los vectores, logos e iconos chiquitos que no me sirven
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
                        
                        # La paso a JPEG para que pese menos y sea más compatible
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
                            self.callback_thumbnail(filepath, thumb)
                        
                        downloaded_count += 1
                            
                    if self.callback_progress:
                        self.callback_progress(i + 1, total, f"Descargando: {os.path.basename(img_url)[:30]}...")

                except Exception as e:
                    print(f"Error downloading {img_url}: {e}")

            if self.callback_finished:
                self.callback_finished("Completado con éxito" if self.is_running else "Cancelado por el usuario")

        except Exception as e:
            if self.callback_finished:
                self.callback_finished(f"Error: {str(e)}")
        finally:
            self.is_running = False
