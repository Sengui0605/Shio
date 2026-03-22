import chromadb
import os

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

def index_document(text: str, source: str):
    """Indexa un documento dividiéndolo en chunks"""
    chunks = chunk_text(text)
    collection.add(
        documents=chunks,
        ids=[f"{source}_{i}" for i in range(len(chunks))],
        metadatas=[{"source": source}] * len(chunks)
    )

def search(query: str, top_k: int = 3):
    """Busca los fragmentos más similares a la consulta"""
    results = collection.query(
        query_texts=[query],
        n_results=top_k
    )
    if results["documents"]:
        return results["documents"][0]
    return []
