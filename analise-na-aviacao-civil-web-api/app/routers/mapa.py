from fastapi import APIRouter
from app.services import cluster_service

router = APIRouter()

@router.get("/mapa")
def get_map():
    try:
        dados = cluster_service.processarDadosMapa()
        return dados
    except Exception as e:
        return {"error": str(e)}, 500
    