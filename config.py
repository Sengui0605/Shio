from pydantic import field_validator
from typing import Any
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    pin: str = "1234"
    ollama_model: str = "gpt-oss:120b-cloud"
    embed_model: str = "nomic-embed-text"
    ollama_host: str = "https://ollama.com"
    cors_origins: Any = ["*"]
    host: str = "0.0.0.0"
    port: int = 7860
    upload_max_size: int = 20_000_000
    cloud_api_key: str = ""


    @field_validator("cors_origins", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Any) -> list[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, str):
            import json
            return json.loads(v)
        return v

    class Config:
        env_file = ".env"

settings = Settings()
