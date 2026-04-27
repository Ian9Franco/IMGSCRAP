import re

def apply_rules(data: dict) -> dict:
    """Aplica transformaciones automáticas a los datos antes de enviarlos a la IA."""
    instr = data.get("instructions", "").lower()

    # Regla: Duplicar precio si se solicita en instrucciones
    if "duplicar" in instr and data.get("price"):
        try:
            # Extrae solo números y decimales
            price_clean = data["price"].replace(".", "").replace(",", "")
            num_match = re.search(r"\d+", price_clean)
            if num_match:
                num = int(num_match.group())
                data["price"] = f"USD {num * 2:,}".replace(",", ".")
        except:
            pass

    # Regla: Corrección de ubicación específica
    if "ramos mejia sur" in instr:
        data["location"] = "Ramos Mejía Sur"

    return data
