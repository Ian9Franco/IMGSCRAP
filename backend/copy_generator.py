"""
copy_generator.py — Genera textos publicitarios para redes sociales.

📌 GUÍA PARA OPTIMIZACIÓN MANUAL:
---------------------------------
1. HASHTAGS: Modificá los tags por nicho y tipo de operación.
2. OP_EMOJIS / PROPERTY_EMOJIS: Cambiá emojis por tipo de propiedad/operación.
3. generate_copy_local: Reordenás secciones editando la lista `partes` al final.
4. Prompt de Gemini: Buscá la sección "PROMPT GEMINI" para ajustar el tono/formato.
"""

import re
import requests

# ─── CLASIFICADORES DE FEATURES (Inmobiliaria) ─────────────────────────────────
FICHA_KEYS = [
    "ambientes", "dormitorios", "baños", "cocheras", "plantas", "antigüedad",
    "situación", "superficie", "terreno", "cubierta", "descubierta",
    "total construido", "frente", "fondo", "condición", "orientación",
    "m²", "expensas", "crédito", "apto crédito", "metros"
]

SERVICIOS_KEYS = [
    "agua corriente", "gas natural", "electricidad", "cloaca", "pavimento",
    "internet", "cable", "telefono", "natural gas", "cloacas"
]

DISTRIBUCION_KEYS = [
    "cocina", "lavadero", "escritorio", "galería", "comedor", "living",
    "jardín", "terraza", "vestidor", "patio", "altillo", "laundry",
    "balcón", "quincho", "pileta", "luminoso", "parrilla", "playroom",
    "sum ", "sauna", "jacuzzi", "solarium", "baulera", "suite", "toilette",
    "galería", "deck", "fogón", "asador"
]

# ─── HASHTAGS ────────────────────────────────────────────────────────────────────
HASHTAGS = {
    "inmobiliaria_venta": (
        "#inmobiliaria #propiedades #venta #realstate #argentina "
        "#hogar #bienesraices #departamentos #casas #oportunidad "
        "#inversion #vivienda #inmuebles #ramosmejia #haedo #morón #oesteGBA"
    ),
    "inmobiliaria_alquiler": (
        "#alquiler #departamentoenalquiler #alquileres #argentina "
        "#propiedades #inmobiliaria #buscoalquiler #vivienda #alquilamos "
        "#mudate #haedo #ramosmejia #morón #oesteGBA"
    ),
    "inmobiliaria_alquiler_temporario": (
        "#alquilertemporario #alquilervacacional #temporada #turismo "
        "#argentina #propiedades #airbnb #vacaciones #escapada "
        "#alquilersemanal #casadevacaciones"
    ),
    "gastronomia": (
        "#gastronomia #restaurante #comida #foodie #chef #argentina "
        "#foodstagram #delivery #gourmet #dondecomer #salida"
    ),
    "ecommerce": (
        "#tiendaonline #compraonline #calidad #envio #argentina "
        "#shopping #oferta #productonuevo #enviosatodoelpais #pagosonline"
    ),
}

# ─── EMOJIS POR TIPO DE OPERACIÓN ────────────────────────────────────────────────
OP_EMOJIS = {
    "venta":               "🔥 ¡OPORTUNIDAD DE VENTA!",
    "alquiler":            "🏠 ¡NUEVO ALQUILER DISPONIBLE!",
    "alquiler_temporario": "🌴 ¡ALQUILER TEMPORARIO!",
    "default":             "✨ PROPIEDAD DISPONIBLE",
}

# ─── EMOJIS POR TIPO DE PROPIEDAD ────────────────────────────────────────────────
PROPERTY_EMOJIS = {
    "casa":         "🏡",
    "departamento": "🏢",
    "ph":           "🏠",
    "local":        "🏪",
    "oficina":      "🖥️",
    "terreno":      "🌿",
    "galpon":       "🏭",
    "campo":        "🌾",
    "cochera":      "🚗",
    "propiedad":    "🏘️",
}


# ─── HELPERS ─────────────────────────────────────────────────────────────────────

def _classify_features(features: list[str]) -> dict:
    """Agrupa features en categorías lógicas para estructurar el copy."""
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

    distribucion.extend(otras)
    return {"ficha": ficha, "servicios": servicios, "distribucion": distribucion}


def _bullets(items: list[str], prefix: str = "• ") -> str:
    return "\n".join(f"{prefix}{item}" for item in items)


def _build_intro_sentence(op_type: str, prop_type: str, location: str, address: str) -> str:
    """Genera una frase introductoria variada según el contexto."""
    loc = location or address or "la zona"
    prop = prop_type if prop_type != "propiedad" else ""

    intros = {
        "venta": [
            f"Encontraste lo que buscabas: {'un ' + prop if prop else 'esta propiedad'} en {loc} que combina ubicación, confort y valor.",
            f"Una oportunidad real en el corazón de {loc}. {'Este ' + prop if prop else 'Esta propiedad'} está lista para ser tu próximo hogar.",
            f"Invertí en calidad de vida. {'Un ' + prop if prop else 'Esta propiedad'} en {loc} con todo lo que necesitás.",
        ],
        "alquiler": [
            f"Tu nuevo hogar te espera en {loc}. {'Un ' + prop if prop else 'Esta propiedad'} con excelentes condiciones para mudarte ya.",
            f"Calidad y comodidad en {loc}. {'Un ' + prop if prop else 'Esta propiedad'} disponible para alquilar de inmediato.",
            f"Sin más búsquedas: {'un ' + prop if prop else 'esta propiedad'} en {loc} ideal para quienes valoran el buen vivir.",
        ],
        "alquiler_temporario": [
            f"El lugar perfecto para tu estadía en {loc}. {'Un ' + prop if prop else 'Esta propiedad'} equipado y listo para recibir.",
            f"Viví {loc} de otra manera. {'Un ' + prop if prop else 'Esta propiedad'} disponible por días, semanas o meses.",
        ],
    }
    options = intros.get(op_type, intros["venta"])
    # Usar hash del string para elegir siempre la misma frase para la misma propiedad
    idx = hash(f"{loc}{prop}") % len(options)
    return options[idx]


# ─── TEMPLATE LOCAL (Sin IA) ─────────────────────────────────────────────────────

def generate_copy_local(nicho: str, data: dict) -> str:
    """
    Genera un copy usando templates enriquecidos. Fallback cuando no hay IA.
    Para cambiar el ORDEN, editá la lista `partes` al final de cada bloque.
    """
    address       = data.get("address", "").strip()
    location      = data.get("location", "").strip()
    price         = data.get("price", "").strip()
    desc          = data.get("description", "").strip()
    features      = data.get("features", [])
    op_type       = data.get("operation_type", "venta")
    property_type = data.get("property_type", "propiedad")

    if isinstance(features, str):
        features = [f.strip() for f in re.split(r",|\n", features) if f.strip()]

    # ── TEMPLATE INMOBILIARIA ─────────────────────────────────────────────────
    if nicho == "inmobiliaria":
        cats = _classify_features(features)
        prop_emoji = PROPERTY_EMOJIS.get(property_type, "🏘️")

        # 1. ENCABEZADO
        op_header = f"{prop_emoji} **{OP_EMOJIS.get(op_type, OP_EMOJIS['default'])}**"
        loc_parts = [p for p in [address, location] if p]
        loc_header = f"📍 {' – '.join(loc_parts)}" if loc_parts else "📍 Propiedad disponible"

        # 2. INTRO personalizada
        intro = _build_intro_sentence(op_type, property_type, location, address)

        # 3. DESCRIPCIÓN del portal (si existe y tiene info útil)
        desc_block = ""
        if desc and len(desc) > 40:
            desc_clean = desc if len(desc) < 350 else desc[:347] + "..."
            # Evitar repetir info que ya está en intro
            if desc_clean.lower() not in intro.lower():
                desc_block = f"_{desc_clean}_"

        # 4. DISTRIBUCIÓN (lo que tiene la propiedad: ambientes, living, etc.)
        secciones = []
        if cats["distribucion"]:
            secciones.append("**✨ Distribución y amenities:**\n" + _bullets(cats["distribucion"][:10]))

        # 5. DATOS CLAVE (dormitorios, baños, cocheras)
        dorm_banos = [f for f in cats["ficha"] if any(
            k in f.lower() for k in ["dormitorio", "baño", "cochera", "ambiente"]
        )]
        if dorm_banos:
            secciones.append("**🛏️ Datos clave:**\n" + _bullets(dorm_banos))

        # 6. SERVICIOS
        if cats["servicios"]:
            secciones.append("**🔌 Servicios:**\n" + _bullets(cats["servicios"]))

        caracteristicas_block = "\n\n".join(secciones) if secciones else ""

        # 7. FICHA TÉCNICA (superficies, expensas, etc.)
        ficha_rest = [f for f in cats["ficha"] if f not in dorm_banos]
        ficha_block = "**📐 Ficha técnica:**\n" + _bullets(ficha_rest[:10]) if ficha_rest else ""

        # 8. APTO CRÉDITO (si aplica)
        credito_features = [f for f in features if "crédito" in f.lower() or "credito" in f.lower()]
        credito_line = "✅ **Apto crédito hipotecario**" if credito_features else ""

        # 9. PRECIO Y CTA
        if price and price.lower() != "consultar":
            precio_linea = f"💰 **Precio: {price}**"
        else:
            precio_linea = "💰 **Precio: A consultar**"

        cta_lines = [
            "📲 **¿Querés visitarlo? Contactanos:**",
            "• WhatsApp / llamada para coordinar visita",
            "• Respondemos consultas por DM",
            "• 🌐 www.urbanoprop.com",
        ]
        cta = "\n".join(cta_lines)

        # 10. HASHTAGS
        tags_key = f"inmobiliaria_{op_type}"
        tags = HASHTAGS.get(tags_key, HASHTAGS["inmobiliaria_venta"])

        # ENSAMBLADO FINAL
        partes = [op_header, loc_header, intro]
        if desc_block:          partes.append(desc_block)
        if caracteristicas_block: partes.append(caracteristicas_block)
        if ficha_block:         partes.append(ficha_block)
        if credito_line:        partes.append(credito_line)
        partes.append("─" * 38)
        partes.append(precio_linea)
        partes.append(cta)
        partes.append(tags)
        return "\n\n".join(partes)

    # ── TEMPLATE GASTRONOMÍA ──────────────────────────────────────────────────
    elif nicho == "gastronomia":
        title = data.get("title", "Nuestro Local").strip()
        header = f"🍴 **{title}**"
        loc_line = f"📍 {address or location}" if (address or location) else ""
        desc_clean = (desc[:380] + "...") if len(desc) > 380 else desc
        desc_out = desc_clean or "Vení a disfrutar de la mejor experiencia gastronómica del barrio."
        features_block = "**✨ Destacados:**\n" + _bullets(features[:10]) if features else ""
        cta = "📲 **Reservas y delivery:**\n• Link en bio o WhatsApp\n• ¡Te esperamos!"

        partes = [header, desc_out]
        if loc_line:       partes.append(loc_line)
        if features_block: partes.append(features_block)
        partes.extend(["─" * 38, cta, HASHTAGS["gastronomia"]])
        return "\n\n".join(partes)

    # ── TEMPLATE ECOMMERCE ────────────────────────────────────────────────────
    else:
        title = data.get("title", "Producto Imperdible").strip()
        header = f"📦 **{title}**"
        desc_clean = (desc[:380] + "...") if len(desc) > 380 else desc
        desc_out = desc_clean or "Calidad garantizada al mejor precio del mercado."
        features_block = "**✨ Especificaciones:**\n" + _bullets(features[:10]) if features else ""
        precio_linea = f"💰 **Precio: {price}**" if price else "💰 **Precio: Consultar**"
        cta = "🛒 **¡Pedí el tuyo ahora!**\n• Envíos a todo el país\n• Cuotas sin interés"

        partes = [header, desc_out]
        if features_block: partes.append(features_block)
        partes.extend(["─" * 38, precio_linea, cta, HASHTAGS["ecommerce"]])
        return "\n\n".join(partes)


# ─── GENERADOR CON IA (Gemini) ────────────────────────────────────────────────────

def _build_gemini_prompt(nicho: str, data: dict) -> str:
    """
    PROMPT GEMINI — Acá se define el tono, estructura y personalidad del copy con IA.
    Modificá las REGLAS DE FORMATO para cambiar cómo escribe la IA.
    """
    title         = data.get("title", "Propiedad")
    address       = data.get("address", "A consultar")
    location      = data.get("location", "Zona Oeste").replace("Venta en ", "").replace("Alquiler en ", "").strip()
    price         = data.get("price", "Consultar")
    features      = data.get("features", [])
    desc          = data.get("description", "")
    op_type       = data.get("operation_type", "venta")
    property_type = data.get("property_type", "propiedad")

    features_str = "\n".join(f"- {f}" for f in features) if isinstance(features, list) else features

    hashtags_key = f"inmobiliaria_{op_type}"
    hashtags = HASHTAGS.get(hashtags_key, HASHTAGS["inmobiliaria_venta"])

    op_label = {
        "venta": "VENTA",
        "alquiler": "ALQUILER",
        "alquiler_temporario": "ALQUILER TEMPORARIO",
    }.get(op_type, "VENTA")

    prop_emoji = PROPERTY_EMOJIS.get(property_type, "🏘️")

    if nicho == "inmobiliaria":
        return f"""
Sos un copywriter experto en Real Estate argentino con más de 10 años de experiencia.
Tu especialidad es crear publicaciones para Instagram y Facebook que generan consultas reales.

DATOS DE LA PROPIEDAD:
- Tipo de operación: {op_label}
- Tipo de propiedad: {property_type} {prop_emoji}
- Título original: {title}
- Dirección: {address}
- Zona / Barrio: {location}
- Precio: {price}
- Descripción del portal: {desc}
- Características extraídas:
{features_str if features_str else "  (sin características detectadas — inferí desde el título y descripción)"}

INSTRUCCIONES DE ESCRITURA:
- Escribí en español rioplatense natural (vos, hacé, visitalo, coordinar).
- Evitá frases genéricas como "hermosa propiedad" o "no te pierdas esta oportunidad".
- Sé específico: mencioná la dirección, la zona, los ambientes, los detalles únicos.
- El tono es cálido y profesional, como un asesor inmobiliario de confianza.
- Si la descripción original tiene info útil, usala (pero reescribila con tu estilo).
- Si hay características, clasificalas inteligentemente en las secciones.

ESTRUCTURA DEL COPY (Markdown):
1. **Línea de título**: Emoji de propiedad + tipo de operación en negrita. Ejemplo: "{prop_emoji} ¡{op_label}! 🔥"
2. **Ubicación**: 📍 {address} – {location}
3. **Párrafo gancho** (2-3 oraciones): Presentá la propiedad con un dato específico y atractivo. Conectá emocionalmente con el lector.
4. **Párrafo descriptivo** (opcional, si hay descripción rica): Expandí los detalles más interesantes.
5. **### ✨ Lo que tiene:**
   - Listá distribución y amenities (jardín, pileta, cochera, etc.) con viñetas (•)
   - Agrupá de forma lógica: espacios interiores, exteriores, servicios
6. **### 📐 Ficha técnica:**
   - Datos duros: m², ambientes, dormitorios, baños, expensas, etc.
   - Si aplica: Apto crédito ✅
7. **Separador**: ---
8. **Precio**: 💰 **{price}** (si es "Consultar", escribí "💰 Precio a convenir – ¡Consultanos!")
9. **CTA**: 📲 ¿Te interesa? Escribinos por DM o WhatsApp. Coordinar una visita es muy fácil. 🌐 www.urbanoprop.com
10. **Hashtags** (en una línea al final):
{hashtags}

REGLAS FINALES:
- Devolvé SOLO el copy formateado. Sin comentarios, sin explicaciones, sin texto extra.
- Si faltan datos, inferí de forma coherente (no inventes datos de precio o dirección).
- Máximo 500 palabras en el copy (sin contar hashtags).
"""
    else:
        return f"""Sos un experto en marketing de {nicho} en Argentina.
Generá un copy persuasivo y estructurado para: {title}.
Precio: {price}. Descripción: {desc}. Características: {features_str}.
Escribí en español rioplatense, tono cálido y profesional. Solo el copy, sin comentarios."""


import os
import time
import google.generativeai as genai
from agent_logger import agent_log

# Configuración global para evitar re-inicializar
os.environ["GOOGLE_API_USE_MTLS_ENDPOINT"] = "never"

def generate_copy(nicho: str, data: dict, api_key: str = "", use_ai: bool = True) -> str:
    """
    PUNTO DE ENTRADA PRINCIPAL.
    Si hay API Key y use_ai es True, usa Gemini. 
    De lo contrario (o si Gemini falla), usa el template local.
    """
    if not use_ai or not api_key or not api_key.strip():
        if not use_ai:
            agent_log.log("BRAIN", "IA desactivada por el usuario. Generando copy local.")
        else:
            agent_log.log("GEMINI", "No se detectó API Key. Usando generador local.", "WARNING")
        return generate_copy_local(nicho, data)

    start_time = time.time()
    try:
        agent_log.log("BRAIN", "Iniciando proceso de redacción inteligente...")
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(model_name="models/gemini-2.5-flash") 

        # Paso 1: Analizar datos
        agent_log.log("BRAIN", f"Analizando datos de la propiedad ({len(data.get('features', []))} características encontradas).")
        
        # Paso 2: Construir Prompt
        agent_log.log("BRAIN", "Construyendo instrucciones de marketing y estructura de publicación...")
        prompt = _build_gemini_prompt(nicho, data)
        
        # Paso 3: Llamar a Gemini
        agent_log.log("GEMINI", f"Solicitando redacción a {model.model_name}... (Esto puede demorar 5-10 segundos)")
        agent_log.log("GEMINI-PROMPT", f"Prompt enviado (longitud: {len(prompt)} caracteres)")
        
        response = model.generate_content(prompt)
        
        # Validar respuesta
        if not response.text:
            raise Exception("Gemini devolvió una respuesta vacía.")

        # Paso 4: Finalizar
        elapsed = time.time() - start_time
        agent_log.log("GEMINI-RESPONSE", f"Publicación generada exitosamente en {elapsed:.2f}s.")
        agent_log.log("BRAIN", "Gemini 2.5 finalizó. Volviendo a modo Standby (1.5).")
        agent_log.log("BRAIN", "Guardando copia y actualizando documento Word...")
        
        return response.text.strip()

    except Exception as e:
        agent_log.log("GEMINI", f"Error crítico en la comunicación con la IA: {e}", "ERROR")
        agent_log.log("BRAIN", "Activando modo de emergencia: Generando copy basado en templates locales.", "WARNING")
        return generate_copy_local(nicho, data)
