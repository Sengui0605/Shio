import httpx
import logging
import json
import asyncio
from config import settings

async def generate_response(messages: list[dict], model: str | None = None, temperature: float = 0.2) -> str:
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
        key_str = str(api_key)
        masked_key = f"{key_str[:6]}...{key_str[-6:]}" if len(key_str) > 12 else "****"
        logging.debug(f"Request a {url} | Key: {masked_key} | Model: {selected_model}")
    else:
        logging.debug(f"Request a {url} SIN API KEY")

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
        transport = httpx.AsyncHTTPTransport(retries=2)
        async with httpx.AsyncClient(timeout=120.0, follow_redirects=True, transport=transport) as client:
            response = await client.post(url, headers=headers, json=payload)
            
            if response.status_code == 401:
                key_str = str(api_key)
                key_info = f"({key_str[:4]}...{key_str[-4:]})" if key_str else "(VACÍA)"
                logging.error(f"401 Unauthorized | Key local: {key_info} | URL: {url}")
                return f"Error: No autorizado (401). Verifica tu Cloud API Key."
            
            if response.status_code != 200:
                logging.error(f"Status {response.status_code} | Body: {response.text}")
                return f"Error del servidor Ollama ({response.status_code})"

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

async def generate_response_stream(messages: list[dict], model: str = None, temperature: float = 0.2):
    """Envía mensajes a Ollama Cloud con streaming usando httpx"""
    host = settings.ollama_host.rstrip('/')
    url = f"{host}/api/chat"
    api_key = (settings.cloud_api_key or "").strip()
    
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    payload = {
        "model": model or settings.ollama_model,
        "messages": messages,
        "stream": True,
        "options": {
            "temperature": temperature if temperature is not None else 0.2
        }
    }

    try:
        async with httpx.AsyncClient(timeout=120.0, follow_redirects=True) as client:
            async with client.stream("POST", url, headers=headers, json=payload) as response:
                if response.status_code != 200:
                    err_body = await response.aread()
                    yield f"data: {json.dumps({'type': 'error', 'text': f'Error {response.status_code}: {err_body.decode()}'})}\n\n"
                    return

                async for line in response.aiter_lines():
                    if not line:
                        continue
                    try:
                        data = json.loads(line)
                        if data.get("done"):
                            break
                        
                        message = data.get("message", {})
                        content = message.get("content", "")
                        thinking = message.get("thinking", "")
                        
                        chunk_text = content or thinking
                        if chunk_text:
                            yield f"data: {json.dumps({'type': 'text', 'text': chunk_text}, ensure_ascii=False)}\n\n"
                    except Exception as e:
                        logging.error(f"Error parseando streaming chunk: {e}")
                        continue
    except Exception as e:
        logging.error(f"Error en generate_response_stream: {e}")
        yield f"data: {json.dumps({'type': 'error', 'text': f'Error de conexión: {str(e)}'})}\n\n"

async def generate_embeddings(texts: list[str]) -> list:
    """Genera embeddings usando la API de Ollama"""
    url = f"{settings.ollama_host.rstrip('/')}/api/embed"
    api_key_raw = settings.cloud_api_key or ""
    api_key: str = str(api_key_raw).strip()
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
