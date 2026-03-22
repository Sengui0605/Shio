from fastapi import APIRouter, UploadFile, File, HTTPException
import os
import uuid
from services.stt import transcribe_audio
from services.file_parser import extract_text_from_file
from services.rag import index_document_async, collection
from models.schemas import RagIndexRequest

router = APIRouter(tags=["Files & RAG"])

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/stt")
async def stt(file: UploadFile = File(...)):
    audio = await file.read()
    if len(audio) > 10_000_000:
        return {"error": "Archivo demasiado grande"}
    
    tmp_file = f"voz_{uuid.uuid4().hex}.wav"
    with open(tmp_file, "wb") as f:
        f.write(audio)
    
    try:
        texto = await transcribe_audio(tmp_file)
        return {"text": texto}
    finally:
        if os.path.exists(tmp_file):
            os.remove(tmp_file)

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    content = await file.read()
    if len(content) > 20_000_000:
        return {"error": "Archivo demasiado grande (max 20MB)"}
    
    filename = f"{uuid.uuid4().hex}_{file.filename}"
    filepath = os.path.join(UPLOAD_DIR, filename)
    
    with open(filepath, "wb") as f:
        f.write(content)
    
    text = extract_text_from_file(filepath, file.filename)
    return {"filename": file.filename, "text": text[:8000], "path": filepath}

@router.post("/rag/index")
async def rag_index(data: RagIndexRequest):
    if not os.path.isdir(data.folder):
        raise HTTPException(status_code=404, detail="Carpeta no encontrada")

    file_count = 0
    for root, dirs, files in os.walk(data.folder):
        for fname in files:
            fpath = os.path.join(root, fname)
            text = extract_text_from_file(fpath, fname)
            if text:
                await index_document_async(text, fpath)
                file_count += 1

    return {"ok": True, "files": file_count}

@router.get("/rag/status")
async def rag_status():
    count = collection.count()
    return {"chunks": count, "has_index": count > 0}
