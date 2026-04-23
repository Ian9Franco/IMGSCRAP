import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from PIL import Image
from io import BytesIO
import threading
import time
import imagehash
from concurrent.futures import ThreadPoolExecutor, as_completed

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
        self.dedup_file = None
        self.global_hashes = set()

    def start_scraping(self, url, base_path, image_path):
        self.is_running = True
        self.thread = threading.Thread(target=self._scrape_logic, args=(url, base_path, image_path))
        self.thread.daemon = True
        self.thread.start()

    def stop_scraping(self):
        self.is_running = False

    def _get_best_image_url(self, img_tag, base_url):
        # Prioridad 0: Si está envuelta en un link a la imagen original (común en galerías)
        parent_a = img_tag.find_parent('a')
        if parent_a and parent_a.get('href'):
            href = parent_a.get('href')
            if any(href.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.webp']):
                return urljoin(base_url, href)

        # Busco en estos atributos porque ahí suelen guardar las imágenes en alta resolución
        candidates = [
            img_tag.get('data-big'),
            img_tag.get('data-original'),
            img_tag.get('data-src-huge'),
            img_tag.get('data-src-large'),
            img_tag.get('data-src'),
            img_tag.get('data-lazy-src'),
            img_tag.get('data-lazy'),
            img_tag.get('srcset'),
            img_tag.get('src')
        ]
        
        best_url = None
        for candidate in candidates:
            if not candidate:
                continue
                
            # Si la imagen es responsive (srcset), intentamos quedarnos con la más grande
            if ',' in candidate:
                try:
                    # Formato: "url1 300w, url2 600w" o "url1, url2 2x"
                    parts = [p.strip().split(' ') for p in candidate.split(',')]
                    # Ordenamos por el descriptor de ancho si existe, sino tomamos el último
                    # Si el descriptor es como '1024w', sacamos la 'w' y convertimos a int
                    def get_width(p):
                        if len(p) > 1 and p[1].endswith('w'):
                            try: return int(p[1][:-1])
                            except: return 0
                        return 0
                    parts.sort(key=get_width, reverse=True)
                    candidate = parts[0][0]
                except:
                    # Fallback al último si falla el parseo
                    candidate = candidate.split(',')[-1].strip().split(' ')[0]
            
            if candidate:
                best_url = urljoin(base_url, candidate)
                break
                
        return best_url

    def _find_images_in_scripts(self, soup):
        """Busca URLs de imágenes dentro de bloques de script (JSON de estado inicial)."""
        import re
        found_urls = []
        for script in soup.find_all("script"):
            if script.string and len(script.string) > 100: # Solo scripts grandes (posibles JSON)
                # Regex para encontrar URLs de imágenes directas (Zonaprop y otros)
                # Buscamos patrones comunes de servidores de imágenes
                urls = re.findall(r'https?://[^\s"\'<>]+?\.(?:jpg|jpeg|png|webp)', script.string)
                for u in urls:
                    # Filtrar logos, iconos y trackers comunes
                    low = u.lower()
                    if any(x in low for x in ['logo', 'icon', 'marker', 'avatar', 'google', 'facebook', 'tracker']):
                        continue
                    found_urls.append(u)
        return list(set(found_urls))

    def _download_image(self, img_url: str):
        """
        Descarga una imagen y valida resolucín + hash.
        Retorna (img, img_data, width, height) si es válida, o None si hay que descartarla.
        Se ejecuta en un thread del pool — sin clasificación CLIP (no es thread-safe).
        """
        try:
            img_resp = requests.get(img_url, headers=self.headers, timeout=10)
            if img_resp.status_code != 200:
                return None
            img_data = img_resp.content
            img = Image.open(BytesIO(img_data))
            width, height = img.size
            if width < self.min_resolution[0] or height < self.min_resolution[1]:
                return None
            return img, img_data, width, height
        except Exception:
            return None

    def _scrape_logic(self, url, base_path, image_path):
        try:
            if not os.path.exists(image_path):
                os.makedirs(image_path)

            # Cargar hashes globales para deduplicación entre sesiones
            import json
            self.dedup_file = os.path.join(base_path, "dedup_index.json")
            if os.path.exists(self.dedup_file):
                try:
                    with open(self.dedup_file, "r") as f:
                        self.global_hashes = set(json.load(f))
                except:
                    self.global_hashes = set()

            response = requests.get(url, headers=self.headers, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            img_tags = soup.find_all('img')
            total = len(img_tags)

            if self.callback_progress:
                self.callback_progress(0, total, "Analizando imágenes...")

            # Recolecto todas las URLs válidas primero
            candidate_urls = []
            seen_urls = set()
            for tag in img_tags:
                img_url = self._get_best_image_url(tag, url)
                if not img_url:
                    continue
                lower_url = img_url.lower()
                if lower_url.endswith('.svg') or 'logo' in lower_url or 'icon' in lower_url:
                    continue
                if img_url in seen_urls:
                    continue
                seen_urls.add(img_url)
                candidate_urls.append(img_url)

            # Fallback: si no encontramos casi nada en <img> (posible SPA como Zonaprop), buscamos en scripts
            if len(candidate_urls) < 5:
                script_urls = self._find_images_in_scripts(soup)
                for s_url in script_urls:
                    if s_url not in seen_urls:
                        candidate_urls.append(s_url)
                        seen_urls.add(s_url)

            seen_hashes = set()
            downloaded_count = 0

            # Descarga paralela: 4 workers para no saturar la red
            with ThreadPoolExecutor(max_workers=4) as executor:
                futures = {
                    executor.submit(self._download_image, img_url): img_url
                    for img_url in candidate_urls
                }

                processed = 0
                for future in as_completed(futures):
                    if not self.is_running:
                        executor.shutdown(wait=False, cancel_futures=True)
                        break

                    processed += 1
                    img_url = futures[future]
                    result = future.result()

                    if self.callback_progress:
                        self.callback_progress(
                            processed, len(candidate_urls),
                            f"Descargando... ({downloaded_count} listas)"
                        )

                    if result is None:
                        continue

                    img, img_data, width, height = result

                    # Deduplicación perceptual (Global y Local)
                    img_hash = str(imagehash.average_hash(img))
                    if img_hash in seen_hashes or img_hash in self.global_hashes:
                        continue
                    seen_hashes.add(img_hash)
                    self.global_hashes.add(img_hash)

                    # Clasificación IA (en hilo principal — model.encode no es thread-safe)
                    ai_tag = None
                    if self.use_ai:
                        try:
                            from image_classifier import classify_image, is_model_ready
                            if is_model_ready():
                                clf_result = classify_image(img, self.nicho)
                                if clf_result["is_irrelevant"]:
                                    continue
                                ai_tag = clf_result["top_tag"]
                        except Exception as e:
                            print(f"[CLIP] Error en clasificación: {e}")

                    # Nombre del archivo
                    if self.use_ai and ai_tag:
                        tag_slug = ai_tag.lower().replace(" ", "_")
                        count = self._tag_counters.get(tag_slug, 0) + 1
                        self._tag_counters[tag_slug] = count
                        filename = f"{tag_slug}_{count}.jpg"
                    else:
                        filename = f"image_{int(time.time() * 1000)}_{downloaded_count}.jpg"
                    filepath = os.path.join(image_path, filename)

                    # Guardo la imagen
                    if img.mode in ("RGBA", "P"):
                        img = img.convert("RGB")
                    img.save(filepath, "JPEG", quality=95)

                    if self.callback_thumbnail:
                        self.callback_thumbnail(filepath, img, width, height, ai_tag)

                    downloaded_count += 1

            # Guardar hashes actualizados
            if self.dedup_file:
                try:
                    with open(self.dedup_file, "w") as f:
                        import json
                        json.dump(list(self.global_hashes), f)
                except:
                    pass

            if self.callback_finished:
                self.callback_finished("Completado con éxito" if self.is_running else "Cancelado por el usuario")

        except Exception as e:
            if self.callback_finished:
                self.callback_finished(f"Error: {str(e)}")
        finally:
            self.is_running = False
