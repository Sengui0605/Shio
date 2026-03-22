from fastapi import Header, HTTPException, Depends
from config import settings

def verify_pin(authorization: str = Header(None)):
    """
    Dependency to verify the PIN sent in the Authorization header.
    Format: Bearer <PIN>
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Se requiere autenticación (Bearer PIN)")
    
    token = authorization.split(" ")[1]
    if token != settings.pin:
        raise HTTPException(status_code=401, detail="PIN incorrecto")
    return token
