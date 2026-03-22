import logging
from duckduckgo_search import DDGS

logger = logging.getLogger("shio")

async def search_youtube_videos(query: str):
    """
    Busca videos usando la librería duckduckgo-search, 
    que es más robusta en entornos cloud como Hugging Face.
    """
    try:
        videos = []
        # Usamos DDGS para buscar videos filtrando por YouTube si es posible
        with DDGS() as ddgs:
            # Añadimos "site:youtube.com" para asegurar resultados de YT
            full_query = f"{query} site:youtube.com"
            results = ddgs.videos(full_query, max_results=5)
            
            for r in results:
                # DDGS devuelve: title, embed_url, video, image, duration, publisher, etc.
                vid_url = r.get('content') or r.get('video') or r.get('url')
                # Intentar extraer ID para la miniatura si no viene
                video_id = ""
                if "v=" in vid_url:
                    video_id = vid_url.split("v=")[1].split("&")[0]
                elif "embed/" in vid_url:
                    video_id = vid_url.split("embed/")[1].split("?")[0]
                
                videos.append({
                    "id": video_id,
                    "url": vid_url,
                    "embed_url": r.get('embed_url') or f"https://www.youtube.com/embed/{video_id}" if video_id else vid_url,
                    "thumbnail": r.get('images', {}).get('medium') or r.get('image') or (f"https://img.youtube.com/vi/{video_id}/mqdefault.jpg" if video_id else ""),
                    "title": r.get('title', 'Video sin título')
                })
        
        return videos
            
    except Exception as e:
        logger.error(f"Error buscando videos con DDGS: {e}")
        # Fallback al scraping original si DDGS falla por alguna razón
        return await _fallback_youtube_scrape(query)

async def _fallback_youtube_scrape(query: str):
    import httpx
    import re
    import urllib.parse
    
    search_url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(query)}"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.get(search_url, headers=headers)
            html = r.text
            video_ids = re.findall(r'"videoId":"([^"]+)"', html)
            videos = []
            seen = set()
            for vid in video_ids:
                if vid not in seen:
                    videos.append({
                        "id": vid,
                        "url": f"https://www.youtube.com/watch?v={vid}",
                        "embed_url": f"https://www.youtube.com/embed/{vid}",
                        "thumbnail": f"https://img.youtube.com/vi/{vid}/mqdefault.jpg",
                        "title": f"Video de YouTube ({vid})"
                    })
                    seen.add(vid)
                    if len(videos) >= 5: break
            return videos
    except:
        return []

if __name__ == "__main__":
    # Prueba rápida
    import asyncio
    async def test():
        vids = await search_youtube_videos("musica para estudiar")
        for v in vids:
            print(f"- {v['title']} -> {v['url']}")
    asyncio.run(test())
