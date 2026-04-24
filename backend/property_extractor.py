"""
property_extractor.py — Extrae datos estructurados de páginas de propiedades.

Estrategia multi-nivel:
1. OG tags (og:title, og:description) — funciona en casi cualquier portal
2. Selectores específicos por dominio para más precisión
3. Heurísticas genéricas como fallback final

Portales soportados:
- Tokko Broker (urbanoprop, remax, century21, etc.)
- ZonaProp
- Argenprop
- MercadoLibre Inmuebles
- Properati
- Inmuebles.com
- LaGrilla / portales genéricos

Devuelve un dict normalizado:
{ title, address, price, location, features, description, operation_type, property_type, extracted }
"""

import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urlparse

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept-Language": "es-AR,es;q=0.9,en;q=0.8",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

# ─── PATRONES DE PRECIO ─────────────────────────────────────────────────────────
PRICE_PATTERNS = [
    r'U\$[Ss]?\s*[\d.,]+',       # U$S 270.000
    r'USD\s*[\d.,]+',             # USD 270.000
    r'US\$\s*[\d.,]+',            # US$ 270.000
    r'\$\s*[\d.,]+',              # $ 1.200.000
    r'[\d.,]+\s*USD',             # 270.000 USD
    r'[\d.,]+\s*U\$[Ss]',        # 270.000 U$S
]

# ─── TIPOS DE PROPIEDAD ─────────────────────────────────────────────────────────
PROPERTY_TYPE_KEYWORDS = {
    "casa": ["casa", "chalet", "vivienda unifamiliar"],
    "departamento": ["departamento", "depto", "dpto", "piso", "apartamento"],
    "ph": [" ph ", "ph ", "planta alta"],
    "local": ["local", "comercial"],
    "oficina": ["oficina", "oficinas"],
    "terreno": ["terreno", "lote", "fracción"],
    "galpon": ["galpón", "galpon", "depósito", "deposito", "nave industrial"],
    "campo": ["campo", "chacra", "establecimiento"],
    "cochera": ["cochera", "garage", "garaje"],
}

# ─── HELPERS ────────────────────────────────────────────────────────────────────

def _og_meta(soup, prop):
    tag = soup.find("meta", property=prop) or soup.find("meta", attrs={"name": prop})
    return tag["content"].strip() if tag and tag.get("content") else ""


def _normalize_price(raw_text: str) -> str:
    """Extrae y normaliza precio. Ej: 'u$s 270.000.- - Casa' → 'USD 270.000'"""
    if not raw_text:
        return ""
    for pattern in PRICE_PATTERNS:
        match = re.search(pattern, raw_text, re.IGNORECASE)
        if match:
            val = match.group(0).upper().strip()
            val = re.sub(r'U\$S?', 'USD', val, flags=re.IGNORECASE)
            val = re.sub(r'US\$', 'USD', val, flags=re.IGNORECASE)
            val = re.sub(r'(USD|\$)([\d.,]+)', r'\1 \2', val)
            val = " ".join(val.split())
            return val
    return ""


def _find_price(soup, text_fallback="") -> str:
    """Busca precio en el DOM y como fallback en texto libre."""
    selectors = [
        "[class*='price']", "[class*='precio']", "[itemprop='price']",
        "[class*='valor']", "[class*='monto']", "[data-testid*='price']",
        "span.price", "div.price", "[class*='Price']",
    ]
    for selector in selectors:
        el = soup.select_one(selector)
        if el:
            raw = el.get_text(strip=True)
            norm = _normalize_price(raw)
            if norm:
                return norm

    norm_fallback = _normalize_price(text_fallback)
    if norm_fallback:
        return norm_fallback

    return "Consultar"


def _detect_operation_type(text: str) -> str:
    """Detecta si es venta, alquiler o alquiler temporario."""
    tl = text.lower()
    if "temporario" in tl or "temporada" in tl or "vacacional" in tl:
        return "alquiler_temporario"
    if "alquiler" in tl or "alquilar" in tl or "renta" in tl or "arrendar" in tl:
        return "alquiler"
    if "venta" in tl or "vender" in tl or "en venta" in tl:
        return "venta"
    return "venta"  # default


def _detect_property_type(text: str) -> str:
    """Detecta el tipo de propiedad desde el texto."""
    tl = text.lower()
    for prop_type, keywords in PROPERTY_TYPE_KEYWORDS.items():
        if any(k in tl for k in keywords):
            return prop_type
    return "propiedad"


def _clean_title(og_title: str) -> str:
    """Limpia el título removiendo el nombre del portal al final."""
    if not og_title: return ""
    # Quitar "| Portal XYZ", "- Portal XYZ", "– Portal XYZ" al final
    # Soporta guiones normales, en-dash (\u2013) y em-dash (\u2014)
    title = re.sub(r'\s*[\-\|\u2013\u2014]\s*[A-Z][a-zA-Z .]{3,}$', '', og_title).strip()
    return title


# ─── PARSEO DE DIRECCIÓN Y UBICACIÓN ────────────────────────────────────────────

def _parse_address_and_location(og_title: str, soup) -> tuple[str, str]:
    """
    Separa la dirección (calle + número) de la ubicación (barrio/zona).
    Soporta múltiples formatos de portales argentinos.
    """
    address = ""
    location = ""

    if og_title:
        # Formato Tokko: "Casa en Venta en Ramos Mejia Sur - Marmol 1426"
        match = re.match(r'.+?\sen\s(.+?)\s-\s(.+)$', og_title)
        if match:
            location = match.group(1).strip()
            address  = match.group(2).strip()

        # Formato MercadoLibre: "Casa 3 Ambientes en Palermo, Capital Federal"
        elif "," in og_title and not address:
            parts = og_title.rsplit(",", 1)
            if len(parts) == 2:
                location = parts[1].strip()
                # La dirección puede venir mezclada con el tipo en la primera parte
                address = re.sub(r'^(Casa|Depto|Departamento|Local|Oficina|Terreno|PH)\s*\d*\s*Ambientes?\s*en\s*', '', parts[0], flags=re.IGNORECASE).strip()

        # Formato con separador "|": "Dirección | Zona"
        elif "|" in og_title and not address:
            parts = og_title.split("|")
            address  = parts[0].strip()
            location = parts[1].strip() if len(parts) > 1 else ""

        # Fallback: parte después del último guion es la dirección
        if not address:
            parts = og_title.rsplit("-", 1)
            if len(parts) == 2:
                address = parts[1].strip()

    # Selectores DOM como respaldo
    if not address:
        for sel in [
            "[itemprop='streetAddress']", "[class*='address']",
            "[class*='direccion']", "[data-testid*='address']", "[class*='street']"
        ]:
            el = soup.select_one(sel)
            if el:
                address = el.get_text(strip=True)
                break

    if not location:
        for sel in [
            "[itemprop='addressLocality']", "[class*='barrio']",
            "[class*='location']", "[class*='zona']",
            "[data-testid*='location']", "[class*='neighborhood']"
        ]:
            el = soup.select_one(sel)
            if el:
                text = el.get_text(strip=True)
                if text.lower() not in ["ubicación", "ubicacion", "location", "zona", "barrio"]:
                    location = text
                    break

    # Limpiar pisos/departamentos de la dirección si quedaron pegados
    address = re.sub(r'\s+(Piso\s*\d+|[0-9]+[°º]\s*[A-Z]|Dpto\.?\s*\w+)', '', address, flags=re.IGNORECASE).strip()

    # Si la dirección quedó vacía, intentar usar el título limpio
    if not address and og_title:
        clean_t = _clean_title(og_title)
        if len(clean_t) < 100:
            address = clean_t
            
            # Intentar detectar localidad al principio (común en títulos de inmobiliarias)
            COMMON_LOCS = [
                "RAMOS MEJIA", "HAEDO", "MORON", "MORÓN", "CASTELAR", "ITUZAINGO", 
                "SAN JUSTO", "LOMAS DEL MIRADOR", "CIUDADELA", "CASEROS", "EL PALOMAR"
            ]
            for loc in COMMON_LOCS:
                if address.upper().startswith(loc):
                    if not location:
                        location = loc.title()
                    # Si el resto del string tiene algo útil, lo dejamos como dirección
                    rest = address[len(loc):].strip()
                    # Quitar palabras de unión como "en", "sur", "norte"
                    rest = re.sub(r'^(sur|norte|centro|en|de)\s+', '', rest, flags=re.IGNORECASE).strip()
                    if rest:
                        address = rest
                    break

    return address, location


# ─── EXTRACCIÓN DE FEATURES POR PORTAL ──────────────────────────────────────────

def _find_features_tokko(soup) -> list[str]:
    """Tokko Broker (urbanoprop, remax, century21, etc.)"""
    features = []
    AMENITIES_KEYWORDS = [
        "Agua Corriente", "Gas Natural", "Electricidad", "Pavimento",
        "Cloaca", "Luminoso", "Parrilla", "Jardín", "Terraza", "Cochera",
        "Pileta", "Balcón", "Seguridad", "Gimnasio", "Portero eléctrico",
        "Cocina", "Lavadero", "Galería", "Living comedor", "Comedor diario",
        "Patio", "Vestidor", "Altillo", "Quincho", "Playroom", "Sum",
        "Sauna", "Jacuzzi", "Solarium", "Baulera", "Apto crédito",
    ]
    for li in soup.find_all("li"):
        text = li.get_text(" ", strip=True)
        if re.match(r'.+:\s*\S+', text) or text in AMENITIES_KEYWORDS:
            if text and len(text) < 80:
                features.append(text)

    # También buscar en spans y divs con clases específicas de Tokko
    for el in soup.select("[class*='feature'], [class*='amenity'], [class*='caracteristica']"):
        text = el.get_text(strip=True)
        if text and len(text) < 60 and text not in features:
            features.append(text)

    return features[:25]


def _find_features_zonaprop(soup) -> list[str]:
    """ZonaProp y Argenprop (estructura similar)."""
    features = []
    for el in soup.select(
        "[class*='feature'], [class*='amenity'], [data-qa*='feature'], "
        "[class*='Feature'], [class*='Amenity'], [class*='caracteristica']"
    ):
        text = el.get_text(strip=True)
        if text and len(text) < 60:
            features.append(text)

    # ZonaProp específico: datos en spans de "strongbox"
    for el in soup.select("[class*='strongbox'], [class*='description-preview']"):
        text = el.get_text(" ", strip=True)
        parts = [p.strip() for p in text.split("|") if p.strip() and len(p.strip()) < 50]
        features.extend(parts)

    return list(dict.fromkeys(features))[:25]  # deduplicar manteniendo orden


def _find_features_mercadolibre(soup) -> list[str]:
    """MercadoLibre Inmuebles."""
    features = []

    # Tabla de specs de MeliProp
    for el in soup.select(
        ".ui-pdp-specs__table tr, [class*='specs'] tr, "
        "[class*='attributes'] li, [class*='highlighted-specs'] li"
    ):
        text = el.get_text(" ", strip=True)
        if text and len(text) < 80:
            features.append(text)

    # Características destacadas (iconos + texto)
    for el in soup.select("[class*='highlighted'] li, [class*='description-list'] li"):
        text = el.get_text(strip=True)
        if text and len(text) < 60 and text not in features:
            features.append(text)

    return features[:25]


def _find_features_properati(soup) -> list[str]:
    """Properati."""
    features = []
    for el in soup.select(
        "[class*='feature'], [class*='amenity'], [class*='tag'], "
        "[class*='property-feature'], [class*='detail']"
    ):
        text = el.get_text(strip=True)
        if text and 2 < len(text) < 60:
            features.append(text)

    return list(dict.fromkeys(features))[:25]


def _find_features_inmuebles(soup) -> list[str]:
    """Inmuebles.com."""
    features = []
    for el in soup.select(
        "[class*='feature'], [class*='amenity'], [class*='caracteristica'], "
        "[class*='attribute'], li[class*='icon']"
    ):
        text = el.get_text(strip=True)
        if text and 2 < len(text) < 60:
            features.append(text)

    return list(dict.fromkeys(features))[:25]


def _find_features_realhomes(soup) -> list[str]:
    """WordPress themes como RealHomes (ej: Olivieri Propiedades)."""
    features = []
    # Lista de características
    for el in soup.select(".rh_property__features_wrap li, .property-features li, .features li"):
        text = el.get_text(strip=True)
        if text and len(text) < 60:
            features.append(text)
            
    # Metadatos como Dormitorios, Baños, etc.
    for el in soup.select(".rh_property__meta_wrap .rh_meta_titles, .rh_property__meta_wrap .rh_meta_title"):
        parent = el.find_parent()
        if parent:
            val_el = parent.select_one(".figure")
            if val_el:
                features.append(f"{val_el.get_text(strip=True)} {el.get_text(strip=True)}")
                
    return list(dict.fromkeys(features))[:25]


def _features_from_og_description(og_desc: str) -> list[str]:
    """
    Parsea features del og:description cuando no se encontraron en el DOM.
    Ej: "4 amb. - 3 dorm. - 2 baños - jardín - cochera"
    """
    if not og_desc:
        return []
    # Intentar separar por " - " primero, luego por " | ", luego por ","
    for sep in [" - ", " | ", ","]:
        if sep in og_desc:
            parts = [p.strip() for p in og_desc.split(sep) if p.strip() and len(p.strip()) < 60]
            if len(parts) >= 2:
                return parts[:15]
    return []


# ─── FUNCIÓN PRINCIPAL ───────────────────────────────────────────────────────────

def extract_property_data(url: str, nicho: str = "inmobiliaria") -> dict:
    """
    Extrae datos estructurados de la URL de una propiedad.

    Retorna:
        {
            "title":          str,
            "address":        str,
            "price":          str,
            "location":       str,
            "features":       list[str],
            "description":    str,
            "operation_type": str,   # "venta" | "alquiler" | "alquiler_temporario"
            "property_type":  str,   # "casa" | "departamento" | "ph" | etc.
            "extracted":      bool
        }
    """
    empty = {
        "title": "", "address": "", "price": "", "location": "",
        "features": [], "description": "", "operation_type": "venta",
        "property_type": "propiedad", "extracted": False
    }

    if nicho != "inmobiliaria":
        return empty

    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        full_text = soup.get_text(" ")
        domain = urlparse(url).netloc.lower()

        # ── 1. OG TAGS Y FALLBACKS ────────────────────────────────────────────
        og_title = _og_meta(soup, "og:title")
        if not og_title and soup.title:
            og_title = soup.title.string or ""

        og_desc  = _og_meta(soup, "og:description")
        if not og_desc:
            # Buscar el primer párrafo largo que parezca una descripción
            for p in soup.find_all("p"):
                text = p.get_text(" ", strip=True)
                if len(text) > 80:
                    og_desc = text
                    break

        # ── 2. TÍTULO LIMPIO ──────────────────────────────────────────────────
        title = _clean_title(og_title)

        # ── 3. DIRECCIÓN Y UBICACIÓN ──────────────────────────────────────────
        address, location = _parse_address_and_location(og_title, soup)

        # ── 4. PRECIO ─────────────────────────────────────────────────────────
        price = _find_price(soup, full_text)

        # ── 5. FEATURES — dispatcher por portal ───────────────────────────────
        features = []

        if "mercadolibre" in domain or "meli" in domain:
            features = _find_features_mercadolibre(soup)

        elif "properati" in domain:
            features = _find_features_properati(soup)

        elif "inmuebles.com" in domain:
            features = _find_features_inmuebles(soup)

        elif "zonaprop" in domain:
            features = _find_features_zonaprop(soup)

        elif "argenprop" in domain:
            features = _find_features_zonaprop(soup)  # estructura compatible
            
        elif "olivieri" in domain or soup.select_one(".rh_property__features_wrap"):
            features = _find_features_realhomes(soup)

        elif any(p in domain for p in ["tokko", "urbanoprop", "remax", "century21", "coldwell", "keller"]):
            features = _find_features_tokko(soup)

        else:
            # Fallback genérico: intentar Tokko primero, luego ZonaProp
            features = _find_features_tokko(soup)
            if not features:
                features = _find_features_zonaprop(soup)

        # Si no encontramos features en el DOM, parsear el og:description
        if not features and og_desc:
            features = _features_from_og_description(og_desc)

        # ── 6. DETECCIÓN AUTOMÁTICA ───────────────────────────────────────────
        combined_text = f"{og_title} {og_desc}"
        operation_type = _detect_operation_type(combined_text)
        property_type  = _detect_property_type(combined_text)

        # ── 7. DESCRIPCIÓN ────────────────────────────────────────────────────
        # Preferir og:description; si es muy corta, buscar en el DOM
        description = og_desc
        if len(description) < 80:
            for sel in [
                "[itemprop='description']", "[class*='description']",
                "[data-testid*='description']", "[class*='detail-description']"
            ]:
                el = soup.select_one(sel)
                if el:
                    candidate = el.get_text(" ", strip=True)
                    if len(candidate) > len(description):
                        description = candidate
                        break

        extracted = bool(address or title or price != "Consultar" or location or features)

        # Debug: imprime en consola del backend para facilitar ajuste de selectores
        print(f"[Extractor] Portal: {domain}")
        print(f"[Extractor] og:title -> {og_title}")
        print(f"[Extractor] Dirección: {address} | Zona: {location}")
        print(f"[Extractor] Precio: {price} | Operación: {operation_type} | Tipo: {property_type}")
        print(f"[Extractor] Features ({len(features)}): {features[:5]}")

        return {
            "title":          title,
            "address":        address,
            "price":          price,
            "location":       location,
            "features":       features,
            "description":    description,
            "operation_type": operation_type,
            "property_type":  property_type,
            "extracted":      extracted,
        }

    except requests.exceptions.Timeout:
        print(f"[Extractor] Timeout al procesar {url}")
        return empty
    except requests.exceptions.HTTPError as e:
        print(f"[Extractor] HTTP {e.response.status_code} al procesar {url}")
        return empty
    except Exception as e:
        print(f"[Extractor] Error al procesar {url}: {e}")
        return empty
