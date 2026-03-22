import httpx
import logging
from config import settings

async def generate_response(messages: list[dict], model: str = None, temperature: float = 0.2) -> str:
    """Envía mensajes a Ollama Cloud usando httpx para mayor estabilidad en auth"""
    host = settings.ollama_host.rstrip('/')
    url = f"{host}/api/chat"
    
    # Limpieza defensiva de la llave
    api_key = (settings.cloud_api_key or "").strip()
    
    headers = {
        "Content-Type": "application/json"
    }
    
    selected_model = model or settings.ollama_model
    
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
        masked_key = f"{api_key[:6]}...{api_key[-6:]}" if len(api_key) > 12 else "****"
        print(f"[DEBUG] Request a {url} | Key: {masked_key} | Model: {selected_model}")
    else:
        print(f"[DEBUG] Request a {url} SIN API KEY")

    payload = {
        "model": selected_model,
        "messages": messages,
        "stream": False,
        "options": {
            "temperature": temperature if temperature is not None else 0.2,
            "num_predict": 1000
        }
    }

    try:
        async with httpx.AsyncClient(timeout=120.0, follow_redirects=True) as client:
            response = await client.post(url, headers=headers, json=payload)
            
            if response.status_code == 401:
                key_info = f"({api_key[:4]}...{api_key[-4:]})" if api_key else "(VACÍA)"
                print(f"[ERROR] 401 Unauthorized | Key local: {key_info} | URL: {url}")
                return f"VERSIÓN DEBUG 2 - Error: No autorizado (401). El servidor rechazó la llave {key_info}. Verifica tu Cloud API Key en Configuración."
            
            if response.status_code != 200:
                print(f"[ERROR] Status {response.status_code} | Body: {response.text}")
                return f"Error del servidor Ollama ({response.status_code}): {response.text}"

            data = response.json()
            message = data.get("message", {})
            content = message.get("content", "").strip()
            thinking = message.get("thinking", "").strip()
            
            final_text = content or thinking
            if not final_text:
                return "No recibí respuesta del modelo. Por favor intenta de nuevo."
            
            return final_text
            
    except Exception as e:
        logging.error(f"Error en generate_response (httpx): {e}")
        return f"Error de conexión: {str(e)}"

async def generate_embeddings(texts: list[str]) -> list:
    """Genera embeddings usando la API de Ollama"""
    url = f"{settings.ollama_host.rstrip('/')}/api/embed"
    api_key = (settings.cloud_api_key or "").strip()
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    try:
        async with httpx.AsyncClient(timeout=60.0, follow_redirects=True) as client:
            response = await client.post(url, headers=headers, json={
                "model": settings.embed_model,
                "input": texts
            })
            response.raise_for_status()
            data = response.json()
            return data.get("embeddings", [])
    except Exception as e:
        logging.error(f"Error en generate_embeddings (httpx): {e}")
        return []
