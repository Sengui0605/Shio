from fastapi import APIRouter, Depends
from models.schemas import SearchRequest
from services.web_search import search_web
from services.auth import verify_token

router = APIRouter(tags=["Search"])

@router.post("/buscar")
async def buscar(data: SearchRequest, _=Depends(verify_token)):
    results = await search_web(data.query)
    return {"results": results}
