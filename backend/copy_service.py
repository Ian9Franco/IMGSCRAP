from prompt_builder import build_prompt
from business_rules import apply_rules
from copy_engine import generate_with_engine
from agent_logger import agent_log

def generate_copy_v2(nicho: str, data: dict, api_key: str = "", engine: str = "local_phi3") -> str:
    """
    Orquestador principal de generación de copys.
    Aplica reglas -> Construye Prompt -> Llama al Motor.
    """
    try:
        agent_log.log("BRAIN", f"Iniciando flujo de redacción ({engine})...")
        
        # 1. Aplicar reglas de negocio (ej: duplicar precio si se pide)
        data = apply_rules(data)
        
        # 2. Construir el prompt único
        prompt = build_prompt(nicho, data)
        
        # 3. Generar con el motor elegido
        result = generate_with_engine(prompt, engine, api_key)
        
        if not result:
            return "⚠️ No se pudo generar el copy. Verificá si Ollama está corriendo o si la API Key es válida."
            
        return result

    except Exception as e:
        agent_log.log("BRAIN", f"Error crítico en el flujo: {e}", "ERROR")
        return f"⚠️ Error inesperado: {str(e)}"
