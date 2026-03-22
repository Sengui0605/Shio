from faster_whisper import WhisperModel
import asyncio
import os

stt_model = WhisperModel("tiny", device="cpu", compute_type="int8")

async def transcribe_audio(file_path: str) -> str:
    """Trascribe audio a texto usando Whisper"""
    segments, _ = await asyncio.to_thread(stt_model.transcribe, file_path, "es")
    texto = " ".join(seg.text for seg in segments)
    return texto.strip()
