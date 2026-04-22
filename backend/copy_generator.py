"""
copy_generator.py — Genera textos publicitarios para redes sociales.

Modo 1 (con API Key): Llama a OpenAI GPT-4o-mini con prompt estructurado.
Modo 2 (sin API Key): Template engine local — genera copy de calidad sin IA externa.
                      Funciona offline, instantáneo, 0 dependencias adicionales.

Estructura del copy (basada en ejemplo de Urbano Propiedades):
  📍 Dirección – Barrio
  [Descripción]
  ✨ Características Principales:
      • Distribución: ...
      • Dormitorios y Baños: ...
      • Servicios e Instalaciones: ...
  🔍 Ficha Técnica: ...
  💰 Precio: ...
  📲 Contacto
"""

import re
import requests

# ─── Clasificadores de features ───────────────────────────────────────────────

# Features que van a la Ficha Técnica (datos numéricos / técnicos)
FICHA_KEYS = [
    "ambientes", "dormitorios", "baños", "cocheras", "plantas", "antigüedad",
    "situación", "superficie", "terreno", "cubierta", "descubierta",
    "total construido", "frente", "fondo", "condición", "orientación",
    "m²", "expensas", "crédito"
]

# Features de servicios e instalaciones
SERVICIOS_KEYS = [
    "agua corriente", "gas natural", "electricidad", "cloaca", "pavimento",
    "internet", "cable", "telefono"
]

# Features de distribución (ambientes / espacios de la propiedad)
DISTRIBUCION_KEYS = [
    "cocina", "lavadero", "escritorio", "galería", "comedor", "living",
    "jardín", "terraza", "vestidor", "patio", "altillo", "laundry",
    "balcón", "quincho", "pileta", "luminoso", "parrilla", "playroom"
]

HASHTAGS = {
    "inmobiliaria": "#inmobiliaria #propiedades #venta #alquiler #realstate #argentina #hogar #bienesraices #departamentos #casas",
    "gastronomia": "#gastronomia #restaurante #comida #foodie #chef #argentina #foodstagram",
    "ecommerce": "#tiendaonline #compraonline #calidad #envio #argentina #shopping",
}


def _classify_features(features: list[str]) -> dict:
    """Clasifica las features en tres categorías: ficha, servicios, distribución."""
    ficha = []
    servicios = []
    distribucion = []
    otras = []

    for f in features:
        fl = f.lower()
        if any(k in fl for k in FICHA_KEYS):
            ficha.append(f)
        elif any(k in fl for k in SERVICIOS_KEYS):
            servicios.append(f)
        elif any(k in fl for k in DISTRIBUCION_KEYS):
            distribucion.append(f)
        else:
            otras.append(f)

    # Lo que no encaja en ninguna categoría va a distribución
    distribucion.extend(otras)

    return {"ficha": ficha, "servicios": servicios, "distribucion": distribucion}


def _bullets(items: list[str], prefix: str = "\t•\t") -> str:
    return "\n".join(f"{prefix}{item}" for item in items)


def generate_copy_local(nicho: str, data: dict) -> str:
    """
    Genera copy estructurado usando templates. No requiere API key ni internet.

    data debe tener: title, address, price, location, features (list o str), description
    """
    address  = data.get("address", "").strip()
    location = data.get("location", "").strip()
    price    = data.get("price", "").strip()
    desc     = data.get("description", "").strip()
    features = data.get("features", [])

    if isinstance(features, str):
        features = [f.strip() for f in re.split(r",|\n", features) if f.strip()]

    cats = _classify_features(features)

    # ── Encabezado de ubicación ──
    if address and location:
        header = f"📍 {address} – {location}"
    elif address:
        header = f"📍 {address}"
    elif location:
        header = f"📍 {location}"
    else:
        header = "📍 Propiedad en venta"

    # ── Párrafo de descripción ──
    if desc:
        # Usar og:description pero acortado y en tono más amigable
        desc_clean = desc[:300] + ("..." if len(desc) > 300 else "")
        descripcion = desc_clean
    else:
        descripcion = f"Propiedad disponible en {location or 'la zona'}. Consultá más detalles."

    # ── Características Principales ──
    secciones = []

    if cats["distribucion"]:
        secciones.append(
            "•\tDistribución:\n" + _bullets(cats["distribucion"][:8], prefix="\to\t")
        )

    # Separar dormitorios y baños de la ficha si están disponibles
    dorm_banos = [f for f in cats["ficha"] if any(k in f.lower() for k in ["dormitorio", "baño", "cochera"])]
    if dorm_banos:
        secciones.append(
            "•\tDormitorios y Baños:\n" + _bullets(dorm_banos, prefix="\to\t")
        )

    if cats["servicios"]:
        secciones.append(
            "•\tServicios e Instalaciones:\n" + _bullets(cats["servicios"], prefix="\to\t")
        )

    caracteristicas_block = ""
    if secciones:
        caracteristicas_block = "✨ Características Principales:\n" + "\n".join(secciones)

    # ── Ficha Técnica ──
    ficha_rest = [f for f in cats["ficha"] if f not in dorm_banos]
    ficha_block = ""
    if ficha_rest:
        ficha_block = "🔍 Ficha Técnica:\n" + _bullets(ficha_rest[:12])

    # ── Precio ──
    precio_linea = f"💰 Precio: {price}" if price and price.lower() != "consultar" else "💰 Precio: Consultar"

    # ── CTA ──
    cta = "📲 ¿Querés visitarlo? Contactanos:\n\t•\tWhatsApp o llamada para coordinar una visita."

    # ── Hashtags ──
    hashtags = HASHTAGS.get(nicho, HASHTAGS["inmobiliaria"])

    # ── Armado final ──
    partes = [header, descripcion]
    if caracteristicas_block:
        partes.append(caracteristicas_block)
    if ficha_block:
        partes.append(ficha_block)
    partes.append("─" * 40)
    partes.append(precio_linea)
    partes.append(cta)
    partes.append(hashtags)

    return "\n\n".join(partes)


def generate_copy(nicho: str, data: dict, api_key: str = "") -> str:
    """
    Punto de entrada principal. Usa OpenAI si hay API key, template local si no.
    """
    if not api_key or not api_key.strip():
        return generate_copy_local(nicho, data)

    address  = data.get("address", "")
    location = data.get("location", "")
    price    = data.get("price", "Consultar")
    features = data.get("features", "")
    desc     = data.get("description", "")

    if isinstance(features, list):
        features_str = "\n".join(f"- {f}" for f in features)
    else:
        features_str = features

    prompt = f"""Actuá como un especialista en marketing inmobiliario argentino.
Generá una PROPUESTA DE COPY para publicaciones profesionales basada en estos datos:

- Dirección: {address}
- Barrio/Zona: {location}
- Precio: {price}
- Descripción: {desc}
- Características:
{features_str}

La estructura EXACTA debe ser:
1. Encabezado: "📍 [Dirección] – [Barrio]"
2. Párrafo de descripción (2-3 oraciones, tono profesional y vendedor)
3. Sección "✨ Características Principales:" con subsecciones:
   • Distribución (espacios de la propiedad)
   • Dormitorios y Baños
   • Servicios e Instalaciones
4. Sección "🔍 Ficha Técnica:" con los datos numéricos (m², ambientes, antigüedad, expensas, etc.)
5. Línea "💰 Precio: [precio]"
6. Sección "📲 ¿Querés visitarlo? Contactanos:" con bullet de WhatsApp/llamada
7. Hashtags inmobiliarios argentinos

Escribí en español rioplatense. Tono profesional pero cercano. Solo el copy, sin comentarios."""

    url = "https://api.openai.com/v1/chat/completions"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}
    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": "Sos un experto en marketing inmobiliario en Argentina."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print(f"[Copy] OpenAI falló ({e}), usando template local.")
        return generate_copy_local(nicho, data)
