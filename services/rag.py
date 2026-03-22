import chromadb
import os
import asyncio

# Directorio para persistencia de ChromaDB
CHROMA_PATH = "data/chroma"
os.makedirs(CHROMA_PATH, exist_ok=True)

client = chromadb.PersistentClient(path=CHROMA_PATH)
collection = client.get_or_create_collection("shio_docs")

def chunk_text(text: str, chunk_size: int = 500) -> list[str]:
    # Función auxiliar para dividir texto (simplificada)
    words = text.split()
    chunks = []
    current = []
    current_len = 0
    for word in words:
        current.append(word)
        current_len += len(word) + 1
        if current_len >= chunk_size:
            chunks.append(" ".join(current))
            current = []
            current_len = 0
    if current:
        chunks.append(" ".join(current))
    return chunks

import httpx
from config import settings

async def generate_embeddings(texts: list[str]) -> list[list[float]]:
    """Genera embeddings usando Ollama Cloud"""
    host = settings.ollama_host.rstrip('/')
    url = f"{host}/api/embed"
    api_key = (settings.cloud_api_key or "").strip()
    
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    payload = {
        "model": settings.embed_model,
        "input": texts
    }

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(url, headers=headers, json=payload)
            if response.status_code != 200:
                return []
            return response.json().get("embeddings", [])
    except Exception:
        return []

async def index_document_async(text: str, source: str):
    """Indexa un documento de forma asíncrona usando embeddings de Ollama"""
    chunks = chunk_text(text)
    embeddings = await generate_embeddings(chunks)
    
    if embeddings:
        await asyncio.to_thread(
            collection.add,
            documents=chunks,
            embeddings=embeddings,
            ids=[f"{source}_{i}" for i in range(len(chunks))],
            metadatas=[{"source": source}] * len(chunks)
        )

async def search(query: str, top_k: int = 3):
    """Busca los fragmentos más similares usando embeddings de Ollama"""
    query_vecs = await generate_embeddings([query])
    if not query_vecs:
        return []
        
    results = await asyncio.to_thread(
        collection.query,
        query_embeddings=query_vecs,
        n_results=top_k
    )
    if results["documents"]:
        return results["documents"][0]
    return []
