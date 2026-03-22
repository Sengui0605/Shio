from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
import logging
import os
import json
import uuid
from datetime import datetime
from models.schemas import ChatRequest
from services.llm import generate_response, generate_response_stream
from services.web_search import search_web
from services.news_service import get_latest_news
from services.video_service import search_youtube_videos
from services.rag import search as rag_search, collection as rag_collection
from database import save_conversation_db, save_message_db, get_messages_db

log = logging.getLogger("shio")
router = APIRouter(tags=["Chat"])

def _load_prompt():
    try:
        if os.path.exists("prompt.txt"):
            with open("prompt.txt", "r", encoding="utf-8") as f:
                return f.read().strip()
    except Exception as e:
        log.error(f"Error leyendo prompt.txt: {e}")
    return "Eres Shio, una asistente de IA. Responde siempre en español."

async def _build_context(data):
    msg_clean = data.msg.strip()
    msg_lower = msg_clean.lower()
    trigger_words = ["busca", "buscar", "search", "quien es", "que es"]
    triggered_word = next((w for w in trigger_words if msg_lower.startswith(w)), None)
    is_search = triggered_word is not None
    is_news = msg_lower == "noticias"
    is_yt = msg_lower.startswith("yt") and (len(msg_lower) == 2 or msg_lower[2] in " :-")

    context_search = ""
    search_query = ""
    videos_list = []
    search_prefix = ""

    if is_news:
        news = get_latest_news()
        if news:
            context_search = "### NOTICIAS GLOBALES DEL DÍA:\n"
            for n in news:
                context_search += f"- {n['title']} (Fuente: {n['source']}, Link: {n['link']})\n"
            context_search += "\nResume estas noticias de forma breve y amena en español.\n"
        else:
            context_search = "No se pudieron obtener noticias."
    elif is_yt:
        search_query = msg_clean[2:].strip().lstrip(":-").strip() or "videos interesantes"
        videos_list = await search_youtube_videos(search_query)
        if videos_list:
            context_search = f"### VIDEOS DE YOUTUBE PARA: '{search_query}':\n"
            for v in videos_list:
                context_search += f"- {v['title']}\n"
            context_search += "\nDile al usuario que encontraste estos videos abajo."
        else:
            context_search = f"No encontré videos para '{search_query}'."
    elif is_search:
        search_query = msg_clean[len(triggered_word):].strip().lstrip(":-").strip()
        if search_query:
            try:
                results = await search_web(search_query)
                if results:
                    search_prefix = f"🔍 _(Búsqueda: **{search_query}**)_\n\n"
                    context_search = "### RESULTADOS DE BÚSQUEDA WEB:\n"
                    for r in results:
                        context_search += f"- {r['title']}: {r['snippet']} (URL: {r['url']})\n"
                    context_search += "\nUsa estos datos para responder e incluye los enlaces.\n"
                else:
                    search_prefix = f"⚠️ Sin resultados para **{search_query}**\n\n"
            except Exception as e:
                log.error(f"Error búsqueda: {e}")

    messages = await get_messages_db(data.session_id or "")

    rag_context = ""
    try:
        if rag_collection.count() > 0:
            rag_results = rag_search(data.msg, top_k=3)
            if rag_results:
                rag_context = "### CONTEXTO DE DOCUMENTOS:\n"
                for chunk in rag_results:
                    rag_context += f"- {chunk}\n"
    except Exception as e:
        log.warning(f"RAG error: {e}")

    system_prompt = _load_prompt()
    if "español" not in system_prompt.lower():
        system_prompt = "Responde SIEMPRE en español.\n" + system_prompt

    all_msgs = [{"role": "system", "content": system_prompt}]
    for m in messages:
        all_msgs.append({"role": m["role"], "content": m["content"]})
    if rag_context:
        all_msgs.append({"role": "system", "content": rag_context})
    if context_search:
        all_msgs.append({"role": "system", "content": context_search})
    if data.file_context:
        all_msgs.append({"role": "system", "content": f"### [ARCHIVO ADJUNTO]\n{data.file_context}\n### [FIN ARCHIVO]"})
    all_msgs.append({"role": "user", "content": data.msg})

    return all_msgs, videos_list, search_prefix, messages

@router.post("/chat/stream")
async def chat_stream(data: ChatRequest):
    session_id = data.session_id or str(uuid.uuid4())
    data.session_id = session_id
    messages = await get_messages_db(session_id)
    if not messages:
        await save_conversation_db(session_id, data.msg[:50], datetime.now().isoformat())
    await save_message_db(session_id, "user", data.msg, datetime.now().isoformat())
    all_msgs, videos_list, search_prefix, _ = await _build_context(data)

    async def event_generator():
        meta = {"type": "meta", "session_id": session_id, "videos": videos_list}
        yield f"data: {json.dumps(meta, ensure_ascii=False)}\n\n"
        if search_prefix:
            yield f"data: {json.dumps({'type': 'text', 'text': search_prefix}, ensure_ascii=False)}\n\n"
        full_response = ""
        async for chunk in generate_response_stream(all_msgs, model=data.model, temperature=data.temperature):
            yield chunk
            try:
                parsed = json.loads(chunk.removeprefix("data: ").strip())
                if parsed.get("type") == "text":
                    full_response += parsed.get("text", "")
            except Exception:
                pass
        if full_response:
            await save_message_db(session_id, "assistant", search_prefix + full_response, datetime.now().isoformat())

    return StreamingResponse(event_generator(), media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})

@router.post("/chat")
async def chat_post(data: ChatRequest):
    session_id = data.session_id or str(uuid.uuid4())
    data.session_id = session_id
    messages = await get_messages_db(session_id)
    if not messages:
        await save_conversation_db(session_id, data.msg[:50], datetime.now().isoformat())
    await save_message_db(session_id, "user", data.msg, datetime.now().isoformat())
    all_msgs, videos_list, search_prefix, _ = await _build_context(data)
    try:
        response = await generate_response(all_msgs, model=data.model, temperature=data.temperature)
        full = search_prefix + response
        await save_message_db(session_id, "assistant", full, datetime.now().isoformat())
        return {"text": full, "session_id": session_id, "videos": videos_list}
    except Exception as e:
        log.error(f"chat error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
