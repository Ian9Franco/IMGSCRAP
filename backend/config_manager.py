from pydantic import BaseModel, Field
import json
import os

CONFIG_FILE = "config.json"
DEFAULT_BASE_DIR = "D:\\Dev\\imgscrap"

class AppConfig(BaseModel):
    base_dir: str = Field(default=DEFAULT_BASE_DIR, alias="BASE_DIR")
    openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")

    class Config:
        populate_by_name = True

def get_config_obj() -> AppConfig:
    if not os.path.exists(CONFIG_FILE):
        return AppConfig()
    try:
        with open(CONFIG_FILE, "r") as f:
            data = json.load(f)
            return AppConfig(**data)
    except Exception as e:
        print(f"[Config] Error cargando config, usando defaults: {e}")
        return AppConfig()

def save_config_obj(config: AppConfig):
    with open(CONFIG_FILE, "w") as f:
        # Guardamos usando los alias (BASE_DIR, OPENAI_API_KEY) para mantener compatibilidad
        json.dump(config.model_dump(by_alias=True), f, indent=4)
    os.makedirs(config.base_dir, exist_ok=True)
