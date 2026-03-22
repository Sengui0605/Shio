# Dockerfile
FROM python:3.12-slim

# Instalar dependencias del sistema y herramientas de compilacion
RUN apt-get update && apt-get install -y \
    build-essential \
    g++ \
    cmake \
    python3-dev \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Actualizar pip para asegurar soporte de wheels modernos
# Crear usuario si no existe (Hugging Face usualmente ya lo tiene con UID 1000)
RUN id -u user >/dev/null 2>&1 || useradd -m -u 1000 user

# Configurar entorno
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    PORT=7860

# Directorio de trabajo estandar de HF
WORKDIR $HOME/app

# Asegurar que el usuario es dueño del directorio antes de empezar
RUN chown -R 1000:1000 $HOME/app

# Cambiar al usuario para instalaciones
USER user

# Instalar dependencias
COPY --chown=user:user requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código
COPY --chown=user:user . .

# Crear carpetas de datos con el usuario correcto
RUN mkdir -p uploads data chroma

EXPOSE 7860

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
