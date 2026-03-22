from fastapi import HTTPException, Security, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from datetime import datetime, timedelta
from config import settings

security = HTTPBearer(auto_error=False)
SECRET_KEY = settings.pin  # Usamos el PIN como secreto para simpleza en este caso
ALGORITHM = "HS256"

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=24)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def verify_token(auth: HTTPAuthorizationCredentials = Security(security)):
    if not auth:
        raise HTTPException(status_code=401, detail="Token de acceso requerido")
    try:
        payload = jwt.decode(auth.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expirado")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token inválido")

async def verify_pin(auth: HTTPAuthorizationCredentials = Security(security)):
    """Mantenemos esta para compatibilidad inicial si es necesario, pero verify_token es preferible"""
    if auth.credentials != settings.pin:
        raise HTTPException(status_code=401, detail="PIN incorrecto")
    return True
