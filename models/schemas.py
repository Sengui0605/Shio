from pydantic import BaseModel
from typing import Optional

class ChatRequest(BaseModel):
    msg: str
    session_id: Optional[str] = None
    file_context: Optional[str] = None
    model: Optional[str] = None
    temperature: Optional[float] = 0.2

class AuthRequest(BaseModel):
    pin: str

class SearchRequest(BaseModel):
    query: str

class PromptUpdate(BaseModel):
    prompt: str

class RagIndexRequest(BaseModel):
    folder: str

class RuntimeConfig(BaseModel):
    pin: str
    ollama_model: str
    ollama_host: str
    cloud_api_key: str
