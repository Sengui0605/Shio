import os
import fitz  # PyMuPDF
import docx

def safe_path(base_dir: str, user_path: str) -> str:
    """Asegura que la ruta este dentro del directorio permitido"""
    full_path = os.path.realpath(
        os.path.join(base_dir, user_path)
    )
    if not full_path.startswith(os.path.realpath(base_dir)):
        raise ValueError("Acceso denegado: ruta fuera del directorio")
    return full_path

def extract_text_from_pdf(path: str) -> str:
    text = ""
    try:
        doc = fitz.open(path)
        for page in doc:
            text += page.get_text() + "\n"
        doc.close()
    except Exception:
        return ""
    return text.strip()

def extract_text_from_docx(path: str) -> str:
    try:
        doc = docx.Document(path)
        return "\n".join([para.text for para in doc.paragraphs])
    except Exception:
        return ""

def extract_text_from_file(path: str, filename: str) -> str:
    ext = os.path.splitext(filename)[1].lower()
    if ext == ".pdf":
        return extract_text_from_pdf(path)
    if ext == ".docx":
        return extract_text_from_docx(path)
    
    text_exts = [".py", ".js", ".ts", ".html", ".css", ".json", ".md", ".txt", ".csv", ".yaml", ".yml", ".toml", ".ini", ".cfg", ".bat", ".sh", ".sql", ".java", ".c", ".cpp", ".h", ".go", ".rs", ".rb", ".php"]
    if ext in text_exts:
        try:
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                return f.read()
        except:
            return ""
    return ""

def chunk_text(text: str, chunk_size: int = 500) -> list[str]:
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
