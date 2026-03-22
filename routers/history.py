from fastapi import APIRouter, HTTPException, Request, Depends
from database import get_all_history_db, get_messages_db, delete_conversation_db, rename_conversation_db, check_conversation_ownership
from services.auth import verify_token
import uuid

router = APIRouter(tags=["History"])

@router.get("/history")
async def get_history(user_id: str, _=Depends(verify_token)):
    rows = await get_all_history_db(user_id)
    return [dict(r) for r in rows]

@router.get("/history/{session_id}")
async def get_history_by_id(session_id: str, user_id: str, _=Depends(verify_token)):
    if not await check_conversation_ownership(session_id, user_id):
        raise HTTPException(status_code=403, detail="No tienes permiso para ver esta conversación")
    messages = await get_messages_db(session_id)
    if not messages:
        return {"error": "Conversación no encontrada"}
    return {"id": session_id, "messages": [dict(m) for m in messages]}

@router.delete("/history/{session_id}")
async def delete_history(session_id: str, user_id: str, _=Depends(verify_token)):
    if not await check_conversation_ownership(session_id, user_id):
        raise HTTPException(status_code=403, detail="No tienes permiso para eliminar esta conversación")
    await delete_conversation_db(session_id)
    return {"ok": True}

@router.patch("/history/{session_id}")
async def rename_history(session_id: str, user_id: str, request: Request, _=Depends(verify_token)):
    if not await check_conversation_ownership(session_id, user_id):
        raise HTTPException(status_code=403, detail="No tienes permiso para renombrar esta conversación")
    data = await request.json()
    new_title = data.get("title", "").strip()
    if not new_title:
        return {"error": "Título vacío"}
    await rename_conversation_db(session_id, new_title)
    return {"ok": True}

@router.post("/history/new")
async def new_session():
    return {"session_id": str(uuid.uuid4())}
