import httpx
import logging
import asyncio
from bs4 import BeautifulSoup

logger = logging.getLogger("shio")

async def search_web(query: str, max_results: int = 5):
    """
    Busca en DuckDuckGo Lite usando un scraper personalizado con httpx y bs4.
    Este método es mucho más robusto para entornos de servidor (Hugging Face)
    que las librerías estándar que suelen ser bloqueadas.
    """
    url = "https://lite.duckduckgo.com/lite/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "es-ES,es;q=0.9",
        "Referer": "https://lite.duckduckgo.com/"
    }
    # Parámetros para la búsqueda en el formulario de DDG Lite
    data = {"q": query}
    
    def _parse_html(html_text):
        results = []
        try:
            soup = BeautifulSoup(html_text, "html.parser")
            # En DDG Lite, los links de resultados son <a> con class='result-link'
            links = soup.find_all("a", class_="result-link")
            # Los snippets son <td> con class='result-snippet'
            snippets = soup.find_all("td", class_="result-snippet")
            
            for i in range(min(len(links), max_results)):
                results.append({
                    "title": links[i].get_text().strip(),
                    "url": links[i]["href"],
                    "snippet": snippets[i].get_text().strip() if i < len(snippets) else ""
                })
            return results
        except Exception as e:
            logger.error(f"[SEARCH] Error parseando HTML: {e}")
            return []

    try:
        logger.info(f"[SEARCH] Iniciando búsqueda custom para: '{query}'")
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
            response = await client.post(url, data=data, headers=headers)
            
            if response.status_code != 200:
                logger.error(f"[SEARCH] Diferente a 200. Status: {response.status_code}")
                return []
            
            # Procesamos el HTML en un hilo separado para no bloquear el loop
            results = await asyncio.to_thread(_parse_html, response.text)
            
            if results:
                logger.info(f"[SEARCH] Éxito. Encontrados {len(results)} resultados.")
            else:
                logger.warning(f"[SEARCH] La búsqueda no devolvió resultados parseables.")
                
            return results
            
    except Exception as e:
        logger.error(f"[SEARCH] Fallo crítico en búsqueda custom: {e}")
        return []
