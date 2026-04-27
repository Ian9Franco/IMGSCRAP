import requests
from agent_logger import agent_log

def generate_local(prompt: str, model: str = "phi3") -> str:
    """Genera texto usando Ollama local. Soporta phi3, gemma3, etc."""
    try:
        # Mapeo simple por si vienen nombres amigables
        model_name = "gemma3" if "gemma" in model.lower() else "phi3"
        
        agent_log.log("OLLAMA", f"Solicitando generación a modelo local: {model_name}")
        res = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": model_name,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.3,
                    "num_predict": 500
                }
            },
            timeout=90 # Gemma puede ser más lento
        )
        res.raise_for_status()
        data = res.json()
        response = data.get("response", "").strip()
        if response:
            # Mostramos un fragmento en la consola para feedback visual
            preview = (response[:120] + "...") if len(response) > 120 else response
            agent_log.log("OLLAMA-RESPONSE", f"\"{preview}\"")
        else:
            agent_log.log("OLLAMA", "Respuesta vacía de Ollama", "WARNING")
        return response
    except Exception as e:
        agent_log.log("OLLAMA", f"Error en motor local (¿está Ollama encendido?): {e}", "ERROR")
        return ""
