import sys, os
# Resolver ruta base para PyInstaller
if getattr(sys, 'frozen', False):
    BASE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

from fastapi import APIRouter, Depends, HTTPException
import logging
import os
import traceback
import sys
import uuid
from datetime import datetime
from models.schemas import ChatRequest
from services.llm import generate_response
from services.web_search import search_web
from services.news_service import get_latest_news
from services.video_service import search_youtube_videos
from database import save_conversation_db, save_message_db, get_messages_db

logger = logging.getLogger("shio")

router = APIRouter(tags=["Chat"])

with open(os.path.join(BASE_DIR, "prompt.txt"), "r", encoding="utf-8") as f:
    SYSTEM_PROMPT = f.read().strip()

@router.post("/chat")
async def chat_post(data: ChatRequest):
    logger.info(f"[CHAT] Mensaje recibido: '{data.msg}' (Session: {data.session_id})")
    session_id = data.session_id or str(uuid.uuid4())
    
    # Check if first message to create conversation
    messages = await get_messages_db(session_id)
    if not messages:
        await save_conversation_db(session_id, data.msg[:50], datetime.now().isoformat())
    
    # Save user message
    timestamp = datetime.now().isoformat()
    await save_message_db(session_id, "user", data.msg, timestamp)
    
    # Búsqueda Web (si aplica)
    msg_clean = data.msg.strip()
    user_msg_lower = msg_clean.lower()
    trigger_words = ["busca", "buscar", "search", "usca", "quien es", "que es"]
    
    # Buscamos la primera palabra que coincida
    triggered_word = None
    for w in trigger_words:
        if user_msg_lower.startswith(w):
            triggered_word = w
            break
            
    is_search = triggered_word is not None
    is_news = user_msg_lower == "noticias"
    is_yt = user_msg_lower.startswith("yt") and (len(user_msg_lower) == 2 or user_msg_lower[2] in [" ", ":", "-"])
    
    logger.info(f"[CHAT] Flags: is_search={is_search}, is_news={is_news}, is_yt={is_yt}")
    
    context_search = ""
    search_query = ""
    videos_list = []
    
    # Manejo de Noticias
    if is_news:
        logger.info("[CHAT] Gatillo 'noticias' detectado.")
        news = get_latest_news()
        if news:
            context_search = "### NOTICIAS GLOBALES DEL DÍA (Mundo en Español):\n"
            for n in news:
                context_search += f"- {n['title']} (Fuente: {n['source']}, Link: {n['link']})\n"
            context_search += "\nInstrucción: Resume estas 10 noticias de forma muy breve y amena en español.\n"
        else:
            context_search = "⚠️ No se han podido obtener noticias en este momento."

    # Manejo de YouTube
    elif is_yt:
        search_query = msg_clean[2:].strip()
        if not search_query:
            search_query = "videos interesantes" 
        logger.info(f"[CHAT] Gatillo 'YT' detectado para: '{search_query}'")
        videos_list = await search_youtube_videos(search_query)
        logger.info(f"[CHAT] Videos encontrados: {len(videos_list)}")
        
        if videos_list:
            context_search = f"### VIDEOS DE YOUTUBE ENCONTRADOS PARA: '{search_query}':\n"
            for v in videos_list:
                context_search += f"- {v['title']}\n"
            context_search += "\nInstrucción: Dile al usuario que has encontrado estos videos y que puede verlos abajo."
        else:
            context_search = f"⚠️ No he encontrado videos para '{search_query}' en este momento."

    # Manejo de Búsqueda Web (si no es noticia ni YT)
    elif is_search:
        # Extraer el término de búsqueda removiendo la palabra gatillo y posibles espacios/dos puntos
        search_query = msg_clean[len(triggered_word):].strip()
        if search_query.startswith(":") or search_query.startswith("-"):
             search_query = search_query[1:].strip()
             
        if not search_query:
            # Si el mensaje era solo "busca", no buscamos nada
            is_search = False
        else:
            logger.info(f"[CHAT] Gatillo '{triggered_word}' activó búsqueda para: '{search_query}'")
            try:
                results = await search_web(search_query)
                if results:
                    logger.info(f"[CHAT] Búsqueda exitosa: {len(results)} resultados.")
                    context_search = "### CONTEXTO DE BÚSQUEDA WEB ACTUALIZADO (Usa esto prioritariamente para responder):\n"
                    for r in results:
                        context_search += f"- {r['title']}: {r['snippet']} (Fuente: {r['url']})\n"
                    context_search += "\nInstrucción: Usa los datos anteriores para dar una respuesta precisa. Es MUY IMPORTANTE que incluyas los enlaces (URLs) directamente en tu respuesta para que el usuario pueda hacer clic en ellos.\n"
                else:
                    logger.warning(f"[CHAT] Búsqueda vacía para: '{search_query}'")
            except Exception as e:
                logger.error(f"[CHAT] Error en búsqueda: {e}")

    # Build context for LLM
    system_prompt = "Te expresas siempre en español."
    if os.path.exists(os.path.join(BASE_DIR, "prompt.txt")):
        try:
            with open(os.path.join(BASE_DIR, "prompt.txt"), "r", encoding="utf-8") as f:
                system_prompt = f.read().strip()
        except Exception as e:
            logger.error(f"Error leyendo prompt.txt: {e}")
            
    # Refuerzo de idioma
    if "español" not in system_prompt.lower():
        system_prompt = "Responde SIEMPRE en español. " + system_prompt

    all_msgs = [{"role": "system", "content": system_prompt}]
    
    # Add history
    for m in messages:
        all_msgs.append({"role": m["role"], "content": m["content"]})
        
    # Add current message
    if context_search:
        all_msgs.append({"role": "system", "content": context_search})
        
    if data.file_context:
        all_msgs.append({"role": "system", "content": f"### [INICIO DEL ARCHIVO ADJUNTO]\n{data.file_context}\n### [FIN DEL ARCHIVO ADJUNTO]\n\nInstrucción: La información anterior pertenece al archivo que el usuario acaba de subir. Úsala para responder a su pregunta."})

    all_msgs.append({"role": "user", "content": data.msg})
    
    try:
        response = await generate_response(all_msgs, model=data.model, temperature=data.temperature)

        # Informativa VIP sobre búsqueda en la respuesta del bot
        debug_prefix = ""
        if is_search:
            if context_search:
                debug_prefix = f"🔍 _(Búsqueda exitosa para: **{search_query}**)_\n\n"
            else:
                debug_prefix = f"⚠️ _(Búsqueda activada para **{search_query}**, pero no se obtuvieron resultados de la web. Mostrando conocimientos internos.)_\n\n"
        
        response = debug_prefix + response

        # Save assistant message
        await save_message_db(session_id, "assistant", response, datetime.now().isoformat())
        return {
            "text": response, 
            "session_id": session_id,
            "videos": videos_list
        }
    except Exception as e:
        logger.error(f"Fallo en chat: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
