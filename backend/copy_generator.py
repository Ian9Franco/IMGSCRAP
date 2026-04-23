"""
copy_generator.py — Genera textos publicitarios para redes sociales.

📌 GUÍA PARA OPTIMIZACIÓN MANUAL:
---------------------------------
Si querés cambiar cómo se ven los textos, buscá estas secciones:
1. HASHTAGS: Modificá los tags por nicho y tipo de operación.
2. OP_EMOJIS: Cambiá el título/emoji principal para Ventas y Alquileres.
3. generate_copy_local: Aquí podés reordenar las secciones (Encabezado, Descripción, etc.)
"""

import re
import requests

# ─── Clasificadores de features (Inmobiliaria) ─────────────────────────────────
FICHA_KEYS = [
    "ambientes", "dormitorios", "baños", "cocheras", "plantas", "antigüedad",
    "situación", "superficie", "terreno", "cubierta", "descubierta",
    "total construido", "frente", "fondo", "condición", "orientación",
    "m²", "expensas", "crédito"
]
SERVICIOS_KEYS = [
    "agua corriente", "gas natural", "electricidad", "cloaca", "pavimento",
    "internet", "cable", "telefono"
]
DISTRIBUCION_KEYS = [
    "cocina", "lavadero", "escritorio", "galería", "comedor", "living",
    "jardín", "terraza", "vestidor", "patio", "altillo", "laundry",
    "balcón", "quincho", "pileta", "luminoso", "parrilla", "playroom"
]

# --- CONFIGURACIÓN DE HASHTAGS ---
# --- 1. OPTIMIZACIÓN DE HASHTAGS (Modificá aquí los tags de tus redes) ---
HASHTAGS = {
    "inmobiliaria_venta": "#inmobiliaria #propiedades #venta #realstate #argentina #hogar #bienesraices #departamentos #casas #oportunidad #inversion #vivienda #inmuebles #ramosmejia #haedo",
    "inmobiliaria_alquiler": "#alquiler #departamentoenalquiler #alquileres #argentina #propiedades #inmobiliaria #buscoalquiler #vivienda #alquilamos #mudate #haedo #ramosmejia",
    "gastronomia": "#gastronomia #restaurante #comida #foodie #chef #argentina #foodstagram #delivery #gourmet #dondecomer #salida",
    "ecommerce": "#tiendaonline #compraonline #calidad #envio #argentina #shopping #oferta #productonuevo #enviosatodoelpais #pagosonline",
}

# --- 2. OPTIMIZACIÓN DE TÍTULOS Y EMOJIS (Cambiá el estilo de tus encabezados) ---
OP_EMOJIS = {
    "venta": "🔥 ¡OPORTUNIDAD DE VENTA! 🔥",
    "alquiler": "🏠 ¡NUEVO ALQUILER DISPONIBLE! 🏠",
    "default": "✨ PROPIEDAD DISPONIBLE ✨"
}

def _classify_features(features: list[str]) -> dict:
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

def _bullets(items: list[str], prefix: str = "- ") -> str:
    return "\n".join(f"{prefix}{item}" for item in items)

def generate_copy_local(nicho: str, data: dict) -> str:
    """
    Genera copy estructurado usando templates locales.
    Fácil de optimizar cambiando las secciones aquí.
    """
    address  = data.get("address", "").strip()
    location = data.get("location", "").strip()
    price    = data.get("price", "").strip()
    desc     = data.get("description", "").strip()
    features = data.get("features", [])
    op_type  = data.get("operation_type", "venta") # venta o alquiler

    if isinstance(features, str):
        features = [f.strip() for f in re.split(r",|\n", features) if f.strip()]

    # --- TEMPLATE INMOBILIARIA ---
    if nicho == "inmobiliaria":
        cats = _classify_features(features)
        
        # 1. ENCABEZADO
        op_header = OP_EMOJIS.get(op_type, OP_EMOJIS["venta"])
        loc_header = f"📍 {address} – {location}" if address and location else f"📍 {address or location or 'Propiedad'}"
        
        # 2. DESCRIPCIÓN
        # Usamos la descripción completa si es corta, o extraemos un fragmento más natural.
        descripcion = desc if len(desc) < 400 else desc[:397] + "..."
        if not descripcion:
             descripcion = f"Excelente propiedad en {location or 'la zona'}. Consultá más detalles."
        
        # 3. CARACTERÍSTICAS
        secciones = []
        if cats["distribucion"]:
            secciones.append("**Distribución:**\n" + _bullets(cats["distribucion"][:8]))
        
        dorm_banos = [f for f in cats["ficha"] if any(k in f.lower() for k in ["dormitorio", "baño", "cochera"])]
        if dorm_banos:
            secciones.append("**Dormitorios y Baños:**\n" + _bullets(dorm_banos))
        
        if cats["servicios"]:
            secciones.append("**Servicios e Instalaciones:**\n" + _bullets(cats["servicios"]))

        caracteristicas_block = "### ✨ Características Principales:\n" + "\n\n".join(secciones) if secciones else ""
        
        # 4. FICHA TÉCNICA
        ficha_rest = [f for f in cats["ficha"] if f not in dorm_banos]
        ficha_block = "### 🔍 Ficha Técnica:\n" + _bullets(ficha_rest[:12]) if ficha_rest else ""
        
        # 5. PRECIO Y CTA
        precio_linea = f"💰 **Precio: {price}**" if price and price.lower() != "consultar" else "💰 **Precio: Consultar**"
        cta = "📲 **¿Querés visitarlo? Contactanos ahora:**\n- WhatsApp o llamada para coordinar una visita.\n- Web: www.urbanoprop.com"
        
        # 6. HASHTAGS
        tags = HASHTAGS.get(f"inmobiliaria_{op_type}", HASHTAGS["inmobiliaria_venta"])

        partes = [op_header, loc_header, descripcion]
        if caracteristicas_block: partes.append(caracteristicas_block)
        if ficha_block: partes.append(ficha_block)
        partes.extend(["─" * 40, precio_linea, cta, tags])
        return "\n\n".join(partes)

    # --- TEMPLATE GASTRONOMÍA ---
    elif nicho == "gastronomia":
        header = f"🍴 {data.get('title', 'Nuestro Local').strip()}"
        location_line = f"📍 Ubicación: {address or location}" if address or location else ""
        descripcion = desc[:400] + ("..." if len(desc) > 400 else "") if desc else "Vení a disfrutar de la mejor experiencia gastronómica."
        
        features_block = "✨ Destacados de hoy:\n" + _bullets(features[:10]) if features else ""
        cta = "📲 Hacé tu reserva o pedí delivery:\n\t•\tLink en bio o WhatsApp."
        
        partes = [header, descripcion]
        if location_line: partes.append(location_line)
        if features_block: partes.append(features_block)
        partes.extend(["─" * 40, cta, HASHTAGS["gastronomia"]])
        return "\n\n".join(partes)

    # --- TEMPLATE ECOMMERCE ---
    else:
        header = f"📦 {data.get('title', 'Producto Imperdible').strip()}"
        descripcion = desc[:400] + ("..." if len(desc) > 400 else "") if desc else "Calidad garantizada y el mejor precio del mercado."
        
        features_block = "✨ Especificaciones:\n" + _bullets(features[:10]) if features else ""
        precio_linea = f"💰 Precio: {price}" if price else "💰 Precio: Consultar"
        cta = "🛒 ¡Pedí el tuyo ahora!\n\t•\tEnvíos a todo el país.\n\t•\tCuotas sin interés."
        
        partes = [header, descripcion]
        if features_block: partes.append(features_block)
        partes.extend(["─" * 40, precio_linea, cta, HASHTAGS["ecommerce"]])
        return "\n\n".join(partes)

def generate_copy(nicho: str, data: dict, api_key: str = "") -> str:
    if not api_key or not api_key.strip():
        return generate_copy_local(nicho, data)

    title    = data.get("title", "Propiedad")
    address  = data.get("address", "A consultar")
    location = data.get("location", "Zona Oeste").replace("Venta en ", "").replace("Alquiler en ", "").strip()
    price    = data.get("price", "Consultar")
    features = data.get("features", [])
    desc     = data.get("description", "")
    op_type  = data.get("operation_type", "venta")

    features_str = "\n".join(f"- {f}" for f in features) if isinstance(features, list) else features

    import google.generativeai as genai
    import os
    try:
        os.environ["GOOGLE_API_USE_MTLS_ENDPOINT"] = "never"
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-flash-latest')

        if nicho == "inmobiliaria":
            prompt = f"""
            Sos un Copywriter experto en Real Estate de Argentina. 
            Transformá estos datos en un texto publicitario persuasivo y ordenado.
            
            DATOS:
            - Operación: {op_type}
            - Título: {title}
            - Dirección: {address}
            - Zona: {location}
            - Precio: {price}
            - Descripción Original: {desc}
            - Características Crudas: {features_str}

            REGLAS DE FORMATO (Markdown):
            1. H2 para el título con un emoji.
            2. 📍 **[{address or location}]**.
            3. Un párrafo introductorio vendedor.
            4. ### ✨ Características Principales: (agrupadas con viñetas lógicas).
            5. ### 🔍 Ficha Técnica: (datos duros).
            6. Separador ---
            7. 💰 **Precio: {price}**
            8. 📲 **Contactanos:** (Incluir WhatsApp y web www.urbanoprop.com)
            
            Escribí en español rioplatense. Devolvé SOLO el copy formateado.
            """
        else:
            prompt = f"""Sos un experto en marketing de {nicho} en Argentina. 
            Generá un copy persuasivo y estructurado para: {title}.
            Precio: {price}
            Descripción: {desc}
            Características: {features_str}
            Escribí en español rioplatense. Solo el copy, sin comentarios."""

        from agent_logger import agent_log
        agent_log.log("GEMINI", "Generando nuevo copy...")
        agent_log.log("GEMINI-PROMPT", prompt)

        response = model.generate_content(prompt)
        
        agent_log.log("GEMINI-RESPONSE", response.text.strip())
        return response.text.strip()
    except Exception as e:
        from agent_logger import agent_log
        agent_log.log("GEMINI", f"Error con Gemini: {e}", "ERROR")
        return generate_copy_local(nicho, data)
