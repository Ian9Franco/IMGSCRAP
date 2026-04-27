from llm_local import generate_local
from llm_cloud import generate_gemini
from agent_logger import agent_log

def generate_with_engine(prompt: str, engine: str = "local_phi3", api_key: str = "", no_fallback: bool = False) -> str:
    """Selector de motor de IA con fallback opcional."""
    if engine == "local_phi3":
        result = generate_local(prompt, model="phi3")
        if not result and api_key and not no_fallback:
            agent_log.log("BRAIN", "Motor Phi-3 falló. Intentando fallback a Gemini...", "WARNING")
            return generate_gemini(prompt, api_key)
        return result
        
    elif engine == "local_gemma3":
        result = generate_local(prompt, model="gemma3")
        if not result and api_key and not no_fallback:
            agent_log.log("BRAIN", "Motor Gemma-3 falló. Intentando fallback a Gemini...", "WARNING")
            return generate_gemini(prompt, api_key)
        return result
        
    elif engine == "cloud_gemini":
        result = generate_gemini(prompt, api_key)
        if not result and not no_fallback:
            agent_log.log("BRAIN", "Motor Cloud falló. Intentando fallback a Gemma-3 local...", "WARNING")
            return generate_local(prompt, model="gemma3")
        return result
        
    else:
        agent_log.log("BRAIN", f"Engine desconocido '{engine}'. Usando local.", "ERROR")
        return generate_local(prompt)
