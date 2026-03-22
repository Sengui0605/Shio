import sys, os
if getattr(sys, 'frozen', False):
    BASE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PROMPT_FILE = os.path.join(BASE_DIR, "prompt.txt")
from fastapi import APIRouter, HTTPException, Body, WebSocket, WebSocketDisconnect
from models.schemas import AuthRequest, PromptUpdate, RuntimeConfig
from config import settings
from services.config_manager import get_runtime_config, save_runtime_config
from services.logger import log_buffer
import os
import json
import requests
from bs4 import BeautifulSoup
import random

router = APIRouter(tags=["Admin"])



@router.post("/auth")
async def auth(data: AuthRequest):
    if data.pin == settings.pin:
        return {"ok": True, "pin": data.pin}
    raise HTTPException(status_code=401, detail="PIN incorrecto")

@router.get("/prompt")
async def get_prompt():
    prompt = ""
    if os.path.exists(PROMPT_FILE):
        with open(PROMPT_FILE, "r", encoding="utf-8") as f:
            prompt = f.read()
    return {"prompt": prompt}

@router.post("/prompt")
async def save_prompt(data: PromptUpdate):
    with open(PROMPT_FILE, "w", encoding="utf-8") as f:
        f.write(data.prompt)
    return {"ok": True}

@router.post("/imagenes")
async def imagenes(data: dict = Body(...), cantidad: int = 18):
    tema = data.get("tema", "")
    if not tema:
        return {"error": "Debes indicar un tema"}
    
    offset = random.randint(0, 50)
    url = f"https://www.bing.com/images/search?q={tema}&first={offset}&FORM=HDRSC2"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    try:
        resp = requests.get(url, headers=headers)
        soup = BeautifulSoup(resp.text, "html.parser")
        imgs = []
        for a in soup.find_all("a", {"class": "iusc"}):
            m_json = a.get("m")
            if m_json:
                try:
                    m_data = json.loads(m_json)
                    img_url = m_data.get("murl")
                    if img_url:
                        imgs.append(img_url)
                except:
                    continue
        random.shuffle(imgs)
        return {"imagenes": imgs[:cantidad]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/config")
async def get_config():
    return get_runtime_config()

@router.post("/config")
async def save_config(data: RuntimeConfig):
    save_runtime_config(data.model_dump())
    return {"ok": True}

@router.websocket("/ws/logs")
async def websocket_logs(websocket: WebSocket):
    await websocket.accept()
    log_buffer.clients.append(websocket)
    # Send existing logs
    for log in log_buffer.logs:
        await websocket.send_json(log)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        if websocket in log_buffer.clients:
            log_buffer.clients.remove(websocket)
