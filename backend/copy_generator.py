"""
copy_generator.py — Módulo para generar textos publicitarios usando LLMs (Fase 1)

Este módulo se encarga de:
- Armar el prompt estructurado según el nicho.
- Llamar a una API externa (por defecto OpenAI) para obtener el texto.
- Retornar el copy limpio y listo para exportar.
"""

import requests
import json

def generate_copy(nicho: str, data: dict, api_key: str) -> str:
    """
    Genera un copy publicitario estructurado.
    
    data debe contener:
    - title
    - price
    - location
    - features (lista o string)
    """
    
    # Prompt base según la estructura del roadmap
    features_str = data.get("features", "")
    if isinstance(features_str, list):
        features_str = ", ".join(features_str)

    prompt = f"""
    Actuá como un especialista en marketing {nicho}.
    Generá un copy para Instagram atractivo y profesional basado en los siguientes datos:

    - Título/Propiedad: {data.get('title', 'N/A')}
    - Ubicación: {data.get('location', 'N/A')}
    - Precio: {data.get('price', 'Consultar')}
    - Características clave: {features_str}

    La estructura DEBE ser:
    1. Hook inicial (1 línea potente)
    2. Descripción breve y vendedora
    3. Lista de características (puntos claros)
    4. Cierre con llamado a la acción (CTA)
    5. Hashtags relevantes

    Escribí el texto en español. No incluyas comentarios extra, solo el copy.
    """

    # Por ahora usamos OpenAI como estándar, pero se podría cambiar fácilmente a Claude
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    payload = {
        "model": "gpt-4o-mini", # Usamos mini por velocidad y costo
        "messages": [
            {"role": "system", "content": "Sos un experto en copywriting para redes sociales."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7
    }

    try:
        if not api_key or api_key == "TU_API_KEY_AQUI":
            return "⚠️ Error: Falta configurar la API KEY de OpenAI en la configuración."

        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        return result["choices"][0]["message"]["content"].strip()
        
    except Exception as e:
        return f"⚠️ Error al generar el copy: {str(e)}"
