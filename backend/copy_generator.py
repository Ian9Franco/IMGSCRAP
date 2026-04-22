"""
copy_generator.py — Genera textos publicitarios para redes sociales.

Modo 1 (con API Key): Llama a OpenAI GPT-4o-mini con prompt estructurado.
Modo 2 (sin API Key): Template engine local — genera copy de calidad sin IA externa.
                      Funciona offline, instantáneo, 0 dependencias adicionales.
"""

import requests

# ─── Templates por nicho ──────────────────────────────────────────────────────

HOOKS = {
    "inmobiliaria": [
        "🏠 ¿Buscás tu próximo hogar? Encontraste el indicado.",
        "✨ Oportunidad única en {location}. No dejes pasar esta propiedad.",
        "🔑 Tu nueva vida empieza acá. Conocé esta propiedad en {location}.",
        "📍 {location} — Una propiedad que habla por sí sola.",
    ],
    "gastronomia": [
        "🍽️ Una experiencia gastronómica que no podés perderte.",
        "✨ Sabores únicos, ambiente inigualable.",
        "🔥 Donde cada plato cuenta una historia.",
        "🌟 La mejor mesa de {location} te está esperando.",
    ],
    "ecommerce": [
        "🛍️ Calidad premium al precio que buscabas.",
        "✨ Diseñado para vos. Hecho para durar.",
        "⚡ Stock limitado — no lo dejes para después.",
        "🌟 El producto que cambia el juego.",
    ],
}

CTAS = {
    "inmobiliaria": [
        "📲 Escribinos y coordinamos una visita sin compromiso.",
        "📞 Contactanos hoy — las consultas no cuestan nada.",
        "💬 DM o WhatsApp para más info y fotos adicionales.",
    ],
    "gastronomia": [
        "📲 Reservá tu mesa por DM o llamándonos.",
        "📞 Contactanos y asegurá tu lugar esta semana.",
        "💬 DM para reservas y menú del día.",
    ],
    "ecommerce": [
        "🛒 Comprá ahora con envío a todo el país.",
        "📲 Escribinos y te asesoramos sin compromiso.",
        "💬 DM para consultas y precios especiales.",
    ],
}

HASHTAGS = {
    "inmobiliaria": "#inmobiliaria #propiedades #casas #venta #alquiler #realstate #argentina #hogar #inversión #departamentos",
    "gastronomia": "#gastronomia #restaurante #comida #foodie #chef #argentina #buenasaida #foodstagram #cocina",
    "ecommerce": "#tiendaonline #compraonline #moda #calidad #envio #argentina #shopping #novedades #tendencia",
}


def _pick(options: list, seed: str = "") -> str:
    """Elige una opción de la lista de forma determinista según el seed."""
    idx = (sum(ord(c) for c in seed) % len(options)) if seed else 0
    return options[idx]


def generate_copy_local(nicho: str, data: dict) -> str:
    """
    Genera copy estructurado usando templates. No requiere API key ni internet.

    data debe tener: title, price, location, features (list o str), description
    """
    nicho = nicho if nicho in HOOKS else "inmobiliaria"

    title     = data.get("title", "").strip()
    price     = data.get("price", "").strip()
    location  = data.get("location", "").strip()
    features  = data.get("features", [])
    desc      = data.get("description", "").strip()

    if isinstance(features, str):
        features = [f.strip() for f in features.split(",") if f.strip()]

    # ── Hook ──
    hook_template = _pick(HOOKS[nicho], seed=title)
    hook = hook_template.replace("{location}", location or "esta zona")

    # ── Descripción ──
    if desc:
        # Acortar el og:description si es muy largo
        descripcion = desc[:280] + ("..." if len(desc) > 280 else "")
    elif title:
        descripcion = f"{title}."
        if location:
            descripcion += f" Ubicada en {location}."
        if price and price != "Consultar":
            descripcion += f" Precio: {price}."
    else:
        descripcion = "Una propiedad excepcional con todo lo que buscás."

    # ── Precio ──
    precio_linea = f"💰 Precio: {price}" if price and price != "Consultar" else "💰 Precio a consultar"

    # ── Features ──
    if features:
        features_text = "\n".join(f"  ✅ {f}" for f in features[:10])
    else:
        features_text = "  ✅ Consultá características completas"

    # ── CTA ──
    cta = _pick(CTAS[nicho], seed=location)

    # ── Hashtags ──
    hashtags = HASHTAGS.get(nicho, "")

    # ── Armado final ──
    copy = f"""{hook}

{descripcion}

{precio_linea}

🏡 Características:
{features_text}

{cta}

{hashtags}"""

    return copy.strip()


def generate_copy(nicho: str, data: dict, api_key: str = "") -> str:
    """
    Punto de entrada principal. Usa OpenAI si hay API key, template local si no.
    """
    # Si no hay API key, usamos el generador local directamente
    if not api_key or api_key.strip() == "":
        return generate_copy_local(nicho, data)

    features_str = data.get("features", "")
    if isinstance(features_str, list):
        features_str = ", ".join(features_str)

    prompt = f"""Actuá como un especialista en marketing {nicho}.
Generá un copy para Instagram atractivo y profesional basado en estos datos:

- Título/Propiedad: {data.get('title', 'N/A')}
- Ubicación: {data.get('location', 'N/A')}
- Precio: {data.get('price', 'Consultar')}
- Características clave: {features_str}
- Descripción: {data.get('description', '')}

La estructura DEBE ser:
1. Hook inicial (1 línea potente con emoji)
2. Descripción breve y vendedora (2-3 oraciones)
3. Lista de características principales (con emojis)
4. Precio destacado
5. Cierre con llamado a la acción (CTA)
6. Hashtags relevantes

Escribí en español rioplatense. No incluyas comentarios extra, solo el copy."""

    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": "Sos un experto en copywriting para redes sociales en Argentina."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.75
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        # Si falla la API, caemos al template local como fallback
        print(f"[Copy] OpenAI falló ({e}), usando template local.")
        return generate_copy_local(nicho, data)
