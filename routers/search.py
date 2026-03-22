from fastapi import APIRouter
from models.schemas import SearchRequest
from services.web_search import search_web

router = APIRouter(tags=["Search"])

@router.post("/buscar")
async def buscar(data: SearchRequest):
    results = await search_web(data.query)
    return {"results": results}
