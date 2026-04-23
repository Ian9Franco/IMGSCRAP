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


def _parse_address_and_location(og_title: str, soup) -> tuple[str, str]:
    """
    Separa la dirección (calle + número) de la ubicación (barrio/zona).

    Ej: "Casa en Venta en Ramos Mejia Sur - Marmol 1426"
      → address="Marmol 1426", location="Ramos Mejia Sur"
    """
    address = ""
    location = ""

    if og_title:
        # Patrón Tokko Broker: "Tipo en Operacion en [Zona] - [Calle Numero]"
        match = re.match(r'.+?\sen\s(.+?)\s-\s(.+)$', og_title)
        if match:
            location = match.group(1).strip()
            address  = match.group(2).strip()
        else:
            # Fallback: la parte después del último guion es la dirección
            parts = og_title.rsplit("-", 1)
            if len(parts) == 2:
                address = parts[1].strip()

    # Selectores DOM para casos donde no hay og:title limpio
    if not address:
        for sel in ["[itemprop='streetAddress']", "[class*='address']", "[class*='direccion']"]:
            el = soup.select_one(sel)
            if el:
                address = el.get_text(strip=True)
                break

    if not location:
        for sel in ["[itemprop='addressLocality']", "[class*='barrio']", "[class*='location']"]:
            el = soup.select_one(sel)
            if el:
                location = el.get_text(strip=True)
                break

    return address, location



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

        # 2. Título + Address + Location
        og_title = _og_meta(soup, "og:title")
        og_desc  = _og_meta(soup, "og:description")

        title = og_title
        title = re.sub(r'\s*[\-\|]\s*[A-Z][a-zA-Z ]{3,}$', '', title).strip()

        address, location = _parse_address_and_location(og_title, soup)

        # 3. Precio
        price = _find_price(soup, full_text)

        # 4. Features — detectar portal
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

        extracted = bool(address or title or price != "Consultar" or location or features)

        # Detectar tipo de operación (Venta / Alquiler)
        operation_type = "venta"
        if "alquiler" in title.lower() or "alquiler" in og_desc.lower():
            operation_type = "alquiler"
        elif "venta" in title.lower() or "venta" in og_desc.lower():
            operation_type = "venta"

        return {
            "title":       title,
            "address":     address,
            "price":       price,
            "location":    location,
            "features":    features,
            "description": og_desc,
            "operation_type": operation_type,
            "extracted":   extracted
        }

    except Exception as e:
        print(f"[Extractor] Error al procesar {url}: {e}")
        return empty
