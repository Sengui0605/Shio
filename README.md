<div align="center">

<!-- Logo -->
<img src="static/shio_icon_512.png" width="100" alt="Shio Logo"/>

# ✦ Shio AI

**Asistente de IA modular y robusto construido con FastAPI + Ollama**

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![License: Proprietary](https://img.shields.io/badge/License-Proprietary-red?style=flat-square)](LICENSE)
[![Docker](https://img.shields.io/badge/Docker-ready-2496ED?style=flat-square&logo=docker&logoColor=white)](Dockerfile)
[![Render](https://img.shields.io/badge/Deploy-Render-46E3B7?style=flat-square&logo=render&logoColor=white)](https://render.com)

[🚀 Demo en vivo](https://shio-o7pu.onrender.com/) · [📖 Documentación](#cómo-funciona) · [☕ Apoya el proyecto](#apoya-el-proyecto)

</div>

---

## ¿Qué es Shio?

Shio es un asistente de IA **completo y funcional** que puedes desplegar en minutos. Está pensado para ofrecer una solución robusta que integra los sistemas de IA modernos — desde el streaming de texto hasta la búsqueda semántica con RAG.

No es un wrapper simple de ChatGPT. Es un sistema completo con su propia capa de autenticación, base de datos, búsqueda web, análisis de documentos y frontend.

```
Usuario → Frontend (HTML/JS)
              ↓
         FastAPI (Python)
         ├── JWT Auth
         ├── Rate Limiting
         ├── Web Search (DuckDuckGo)
         ├── RAG (ChromaDB + Ollama Embeddings)
         ├── YouTube Search
         ├── News Feed (RSS)
         └── LLM Stream (Ollama Cloud)
              ↓
         SQLite (historial)
```

---

## ✨ Funcionalidades

| Función | Descripción | Cómo usarla |
|---|---|---|
| 💬 Chat con streaming | Respuestas en tiempo real token a token | Escribe cualquier mensaje |
| 🔍 Búsqueda web | DuckDuckGo Lite, sin API key | `busca [tema]` · `quien es [nombre]` |
| 📰 Noticias | Titulares globales vía RSS | `noticias` |
| 📺 YouTube | Busca y muestra videos embebidos | `yt [búsqueda]` |
| 🖼️ Imágenes | Galería desde Bing Images | `imagenes de [tema]` |
| 📄 Documentos (RAG) | Analiza PDFs, DOCX, TXT con memoria semántica | Arrastra un archivo al chat |
| 🎙️ Voz | Transcripción con Faster-Whisper (STT) | Botón 🎙️ |
| 🧠 Multi-modelo | Cambia de modelo en tiempo real | Panel de configuración |
| 🎨 Temas | 10 temas visuales incluidos | Menú → Temas |

---

## 🏗️ Arquitectura — cómo funciona

> Esta sección es el corazón del proyecto: aprende cómo está construido cada módulo.

### 1. Autenticación con JWT
```
POST /auth { pin } → JWT Token (24h)
Todos los endpoints → Authorization: Bearer <token>
```
El PIN se guarda en `.env`. Al hacer login, el servidor firma un JWT con PyJWT. Los tokens expiran automáticamente y no viajan en cada request como texto plano.

### 2. Streaming con Server-Sent Events (SSE)
```
POST /chat/stream → text/event-stream
data: {"type": "meta", "session_id": "..."}
data: {"type": "text", "text": "Hola"}
data: {"type": "text", "text": ", ¿cómo"}
...
```
El frontend recibe chunks de texto en tiempo real usando `fetch()` con `ReadableStream`. Esto es lo que produce el efecto de escritura progresiva.

### 3. RAG — Retrieval-Augmented Generation
```
Documento PDF
     ↓
Dividir en chunks de ~500 palabras
     ↓
Ollama /api/embed → vectores float[]
     ↓
ChromaDB (base de datos vectorial local)

Al hacer una pregunta:
Pregunta → vector → búsqueda por similitud coseno → top 3 chunks
     ↓
Se inyectan como contexto en el prompt del LLM
```
Esto permite que Shio "recuerde" documentos que nunca fueron parte de su entrenamiento.

### 4. Rate Limiting
```python
@limiter.limit("20/minute")
async def chat_stream(request: Request, ...):
```
`slowapi` limita las peticiones por IP usando un contador en memoria. Evita que un usuario abuse del API sin necesidad de Redis.

### 5. Base de datos
SQLite con `aiosqlite` — async, sin servidor, archivo único en `data/shio.db`.
```sql
conversations (id, user_id, title, created)
messages      (id, conversation_id, role, content, timestamp)
```

---

## 🚀 Instalación local

### Requisitos
- Python 3.10+
- Una cuenta en [Ollama Cloud](https://ollama.com) (gratis para empezar)

### Pasos

```bash
# 1. Clonar el repositorio
git clone https://github.com/Sengui0605/Shio.git
cd shio-ai

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Configurar variables de entorno
cp .env.example .env
# Edita .env con tu API key de Ollama Cloud

# 4. Iniciar el servidor
python main.py
```

Abre `http://localhost:7860` en tu navegador.

### Variables de entorno

```bash
# .env.example
PIN=tu-pin-de-acceso          # PIN para entrar a la interfaz
CLOUD_API_KEY=               # API key de Ollama Cloud
OLLAMA_HOST=https://ollama.com
OLLAMA_MODEL=gpt-oss:120b-cloud
EMBED_MODEL=nomic-embed-text
PORT=7860
```

---

## 🐳 Deploy con Docker

```bash
docker-compose up --build
```

O directamente en Render, Railway, o Hugging Face Spaces con el `Dockerfile` incluido.

---

## 📁 Estructura del proyecto

```
shio-ai/
├── main.py                 # Entry point FastAPI
├── config.py               # Variables de entorno con Pydantic
├── database.py             # SQLite async (conversaciones y mensajes)
├── routers/
│   ├── chat.py             # /chat y /chat/stream (SSE)
│   ├── history.py          # CRUD del historial
│   ├── files.py            # Upload, STT, RAG index
│   ├── search.py           # Búsqueda web
│   └── admin.py            # Config, prompt, imágenes, WebSocket logs
├── services/
│   ├── llm.py              # Llamadas a Ollama (stream + sync + embeddings)
│   ├── rag.py              # ChromaDB: indexar y buscar documentos
│   ├── web_search.py       # Scraper de DuckDuckGo Lite
│   ├── news_service.py     # Feed RSS de Google News
│   ├── video_service.py    # Búsqueda de YouTube con DDGS
│   ├── file_parser.py      # Extrae texto de PDF, DOCX, TXT
│   ├── stt.py              # Transcripción con Faster-Whisper
│   ├── auth.py             # JWT: crear y verificar tokens
│   └── rate_limiter.py     # slowapi limiter
├── models/
│   └── schemas.py          # Modelos Pydantic (ChatRequest, etc.)
├── static/
│   ├── index.html          # Frontend completo (HTML + CSS)
│   └── app.js              # Lógica del cliente (vanilla JS)
├── Index/                  # Recursos UI adicionales
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

---

## 🧩 Conceptos que puedes aprender con este proyecto

- ✅ Cómo funciona un **LLM con streaming** (SSE / token por token)
- ✅ Qué es **RAG** y cómo implementarlo desde cero
- ✅ Cómo funcionan los **embeddings** y la similitud vectorial
- ✅ **JWT authentication** en una API REST
- ✅ **Rate limiting** sin Redis
- ✅ Async Python con **FastAPI + aiosqlite**
- ✅ Un frontend moderno con **vanilla JS** (sin React ni frameworks)
- ✅ Deploy con **Docker + Render**

---

## ☕ Apoya el proyecto

Shio es una herramienta profesional de pago diseñada para ofrecer máxima eficiencia.

Si te ayudó a aprender, si lo usas en algún proyecto, o simplemente quieres que siga creciendo con nuevas funcionalidades y tutoriales:

<div align="center">

[![Ko-fi](https://img.shields.io/badge/Ko--fi-Invítame%20un%20café-FF5E5B?style=for-the-badge&logo=ko-fi&logoColor=white)](https://ko-fi.com/sengui0605)

</div>

Cada aporte, por pequeño que sea, ayuda a mantener el servidor, dedicar tiempo al proyecto y crear más contenido educativo.

---

## 🤝 Contribuir

¡Las contribuciones son bienvenidas! Si encontraste un bug, tienes una idea o quieres añadir una funcionalidad:

1. Haz fork del repositorio
2. Crea una rama: `git checkout -b feature/mi-mejora`
3. Haz commit: `git commit -m 'Añade mi mejora'`
4. Push: `git push origin feature/mi-mejora`
5. Abre un Pull Request

---

## 📄 Licencia

Proprietaria — Queda prohibida la reproducción, distribución o transmisión de este software sin autorización previa. Consulte el archivo [LICENSE](LICENSE) para más detalles.

---

<div align="center">

Hecho con ☕ por **Senjiro** · Si te sirvió, dale ⭐ al repo

</div>
