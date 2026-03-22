import asyncio
import feedparser
import logging

logger = logging.getLogger("shio")

async def get_latest_news():
    """
    Obtiene los 10 titulares globales más recientes en español 
    desde el feed RSS de Google News (No bloqueante).
    """
    rss_url = "https://news.google.com/rss?hl=es-419&gl=US&ceid=US:es-419"
    
    try:
        # feedparser.parse es bloqueante, lo corremos en un hilo
        feed = await asyncio.to_thread(feedparser.parse, rss_url)
        news_list = []
        
        for entry in feed.entries[:10]:
            news_list.append({
                "title": entry.title,
                "link": entry.link,
                "published": entry.published if hasattr(entry, 'published') else "Reciente",
                "source": entry.source.title if hasattr(entry, 'source') else "Fuente desconocida"
            })
            
        return news_list
    except Exception as e:
        logger.error(f"Error obteniendo noticias: {e}")
        return []

if __name__ == "__main__":
    # Prueba rápida
    news = get_latest_news()
    for i, n in enumerate(news, 1):
        print(f"{i}. {n['title']} ({n['source']})")
