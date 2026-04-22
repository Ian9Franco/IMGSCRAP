"""
property_extractor.py — Extrae datos estructurados de páginas de propiedades.

Estrategia multi-nivel:
1. OG tags (og:title, og:description) — funciona en casi cualquier portal
2. Selectores específicos por dominio para más precisión (Tokko Broker, ZonaProp, Argenprop)
3. Heurísticas genéricas como fallback final

Devuelve un dict normalizado: { title, price, location, features, description }
"""

import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urlparse

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
}

# Patrones de precio para Argentina
PRICE_PATTERNS = [
    r'U\$[Ss]?\s*[\d.,]+',      # USD, U$S, U$s
    r'USD\s*[\d.,]+',
    r'\$\s*[\d.,]+',             # Pesos
    r'[\d.,]+\s*USD',
]


def _og_meta(soup, prop):
    tag = soup.find("meta", property=prop) or soup.find("meta", attrs={"name": prop})
    return tag["content"].strip() if tag and tag.get("content") else ""


def _find_price(soup, text_fallback=""):
    """Busca precio en el DOM o en texto libre."""
    # Selectores comunes en portales inmobiliarios argentinos
    for selector in [
        "[class*='price']", "[class*='precio']", "[itemprop='price']",
        "[class*='valor']", "[class*='monto']", "span.price", "div.price"
    ]:
        el = soup.select_one(selector)
        if el and el.get_text(strip=True):
            return el.get_text(strip=True)

    # Búsqueda por regex en texto completo
    for pattern in PRICE_PATTERNS:
        match = re.search(pattern, text_fallback)
        if match:
            return match.group(0)

    return "Consultar"


def _find_location(soup, og_title="", og_desc=""):
    """Extrae la ubicación del título OG o del DOM."""
    # Selectores específicos
    for selector in [
        "[class*='location']", "[class*='ubicacion']", "[class*='barrio']",
        "[class*='address']", "[itemprop='addressLocality']"
    ]:
        el = soup.select_one(selector)
        if el:
            return el.get_text(strip=True)

    # Desde el título OG: "Casa en Venta en Ramos Mejia Sur - Marmol 1426"
    # Patrón: "en [Ubicación]"
    match = re.search(r'\ben\s+([A-ZÁÉÍÓÚÑ][^\-\|]+)', og_title)
    if match:
        return match.group(1).strip()

    return ""


def _find_features_tokko(soup):
    """
    Extrae features de portales basados en Tokko Broker (urbanoprop, etc.)
    Los datos vienen en listas <li> planas.
    """
    features = []

    # Buscar listas de características (ej: "Ambientes: 4", "Dormitorios: 3")
    for li in soup.find_all("li"):
        text = li.get_text(" ", strip=True)
        # Filtra elementos que parecen características (tienen ":" o son palabras clave)
        if re.match(r'.+:\s*\S+', text) or text in [
            "Agua Corriente", "Gas Natural", "Electricidad", "Pavimento",
            "Cloaca", "Luminoso", "Parrilla", "Jardín", "Terraza", "Cochera",
            "Pileta", "Balcón", "Seguridad", "Gimnasio", "Portero eléctrico",
            "Cocina", "Lavadero", "Galería", "Living comedor", "Comedor diario",
            "Patio", "Vestidor", "Altillo"
        ]:
            if text and len(text) < 80:  # evita párrafos enteros
                features.append(text)

    return features[:20]  # máximo 20 características


def _find_features_zonaprop(soup):
    """Selectores específicos para ZonaProp."""
    features = []
    for el in soup.select("[class*='feature'], [class*='amenity'], [data-qa*='feature']"):
        text = el.get_text(strip=True)
        if text and len(text) < 60:
            features.append(text)
    return features[:20]


def extract_property_data(url: str, nicho: str = "inmobiliaria") -> dict:
    """
    Extrae datos estructurados de la URL de una propiedad.

    Retorna:
        {
            "title": str,
            "price": str,
            "location": str,
            "features": list[str],
            "description": str,
            "extracted": bool   # True si se pudo extraer algo útil
        }
    """
    empty = {
        "title": "", "price": "", "location": "",
        "features": [], "description": "", "extracted": False
    }

    if nicho != "inmobiliaria":
        return empty  # Por ahora solo inmobiliaria tiene extracción avanzada

    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        full_text = soup.get_text(" ")

        # 1. OG Tags (funcionan en Tokko Broker, MercadoLibre Inmuebles, etc.)
        og_title = _og_meta(soup, "og:title")
        og_desc  = _og_meta(soup, "og:description")

        # 2. Título limpio
        title = og_title
        # Limpiar sufijos comunes: "- Inmobiliaria X" / "| Portal X"
        title = re.sub(r'\s*[\-\|]\s*[A-Z][a-zA-Z ]{3,}$', '', title).strip()

        # 3. Precio
        price = _find_price(soup, full_text)

        # 4. Ubicación
        location = _find_location(soup, og_title, og_desc)

        # 5. Características — detectar portal
        domain = urlparse(url).netloc.lower()
        if any(p in domain for p in ["tokko", "urbanoprop", "remax", "century21"]):
            features = _find_features_tokko(soup)
        elif "zonaprop" in domain:
            features = _find_features_zonaprop(soup)
        elif "argenprop" in domain:
            features = _find_features_zonaprop(soup)  # estructura similar
        else:
            features = _find_features_tokko(soup)  # intenta Tokko como genérico

        # Si el OG description tiene datos y no encontramos features, usarlo
        if not features and og_desc:
            # Parsear "4 amb. - 3 dorm. - cocina - jardín" del OG description
            parts = [p.strip() for p in og_desc.split("-") if p.strip() and len(p.strip()) < 60]
            features = parts[:15]

        # 6. Descripción: OG description como base
        description = og_desc

        extracted = bool(title or price != "Consultar" or location or features)

        return {
            "title": title,
            "price": price,
            "location": location,
            "features": features,
            "description": description,
            "extracted": extracted
        }

    except Exception as e:
        print(f"[Extractor] Error al procesar {url}: {e}")
        return empty
