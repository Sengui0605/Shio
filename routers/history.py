from fastapi import APIRouter, HTTPException, Request
from database import get_all_history_db, get_messages_db, delete_conversation_db, rename_conversation_db
import uuid

router = APIRouter(tags=["History"])

@router.get("/history")
async def get_history():
    rows = await get_all_history_db()
    return [dict(r) for r in rows]

@router.get("/history/{session_id}")
async def get_history_by_id(session_id: str):
    messages = await get_messages_db(session_id)
    if not messages:
        return {"error": "Conversación no encontrada"}
    return {"id": session_id, "messages": [dict(m) for m in messages]}

@router.delete("/history/{session_id}")
async def delete_history(session_id: str):
    await delete_conversation_db(session_id)
    return {"ok": True}

@router.patch("/history/{session_id}")
async def rename_history(session_id: str, request: Request):
    data = await request.json()
    new_title = data.get("title", "").strip()
    if not new_title:
        return {"error": "Título vacío"}
    await rename_conversation_db(session_id, new_title)
    return {"ok": True}

@router.post("/history/new")
async def new_session():
    return {"session_id": str(uuid.uuid4())}
