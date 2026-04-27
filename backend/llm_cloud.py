import google.generativeai as genai
from agent_logger import agent_log

def generate_gemini(prompt: str, api_key: str) -> str:
    """Genera texto usando Google Gemini Flash 1.5."""
    if not api_key or not api_key.strip():
        agent_log.log("GEMINI", "Falta API Key para Gemini Cloud.", "ERROR")
        return ""
        
    try:
        agent_log.log("GEMINI", "Solicitando redacción a la nube (Gemini 1.5 Flash)...")
        genai.configure(api_key=api_key)
        # Usamos el modelo flash por su rapidez y eficiencia en costos/tokens
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        resp = model.generate_content(prompt)
        if not resp or not hasattr(resp, 'text') or not resp.text:
            agent_log.log("GEMINI", "Respuesta vacía de Gemini Cloud.", "WARNING")
            return ""
            
        response_text = resp.text.strip()
        preview = (response_text[:120] + "...") if len(response_text) > 120 else response_text
        agent_log.log("GEMINI-RESPONSE", f"\"{preview}\"")
        
        return response_text
    except Exception as e:
        agent_log.log("GEMINI", f"Error en motor cloud: {e}", "ERROR")
        return ""
