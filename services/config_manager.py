import os
import json
from config import settings

CONFIG_PATH = "shio_runtime_config.json"

def get_runtime_config():
    if not os.path.exists(CONFIG_PATH):
        # Valores iniciales desde settings
        initial = {
            "pin": settings.pin,
            "ollama_model": settings.ollama_model,
            "ollama_host": settings.ollama_host,
            "cloud_api_key": settings.cloud_api_key
        }
        save_runtime_config(initial)
        return initial
    
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        config_data = json.load(f)
        # Sincronizar con settings al leer
        settings.pin = config_data.get("pin", settings.pin)
        settings.ollama_model = config_data.get("ollama_model", settings.ollama_model)
        settings.ollama_host = config_data.get("ollama_host", settings.ollama_host)
        settings.cloud_api_key = config_data.get("cloud_api_key", settings.cloud_api_key)
        return config_data

def save_runtime_config(config_data):
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config_data, f, indent=2)
    
    settings.pin = config_data.get("pin", settings.pin)
    settings.ollama_model = config_data.get("ollama_model", settings.ollama_model)
    settings.ollama_host = config_data.get("ollama_host", settings.ollama_host)
    settings.cloud_api_key = config_data.get("cloud_api_key", settings.cloud_api_key)
