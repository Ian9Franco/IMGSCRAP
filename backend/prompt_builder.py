def build_prompt(nicho: str, data: dict) -> str:
    """Construye un prompt único optimizado para modelos Rioplatenses."""
    title = data.get("title", "")
    address = data.get("address", "")
    location = data.get("location", "")
    price = data.get("price", "")
    features = data.get("features", [])
    desc = data.get("description", "")
    op_type = data.get("operation_type", "venta")
    property_type = data.get("property_type", "propiedad")

    # Aseguramos que features sea una lista
    if isinstance(features, str):
        features_list = [f.strip() for f in features.split(",") if f.strip()]
    else:
        features_list = features if isinstance(features, list) else []

    features_str = "\n".join(f"- {f}" for f in features_list)

    return f"""
Actuá como copywriter inmobiliario argentino experto en marketing digital.

TAREA:
Generar un copy persuasivo para Instagram/Facebook.

FORMATO OBLIGATORIO:
1. Título con emoji (impactante)
2. Ubicación (📍 {address} – {location})
3. Intro (2-3 líneas con gancho emocional)
4. ✨ Lo que tiene (lista de puntos clave)
5. 📐 Ficha técnica (datos de m2, ambientes, etc.)
6. ---
7. 💰 Precio: {price}
8. CTA (Llamado a la acción claro)
9. Hashtags (en una sola línea al final)

DATOS DE LA PROPIEDAD:
- Tipo: {property_type}
- Operación: {op_type}
- Dirección: {address}
- Zona: {location}
- Precio: {price}

Características detectadas:
{features_str if features_str else "(Sin características específicas detectedas)"}

Descripción original:
{desc}

REGLAS ESTRICTAS:
- Usá español rioplatense (voseo: "visitalo", "vení", "comprobalo").
- No inventes datos que no están arriba.
- Sé profesional pero cálido.
- Máximo 300 palabras.

OUTPUT:
Solo el copy final formateado. Sin introducciones ni comentarios adicionales.
"""
