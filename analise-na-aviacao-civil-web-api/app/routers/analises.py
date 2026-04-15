from fastapi import APIRouter
from app.services import data_service

router = APIRouter()

@router.get("/")
def read_root():
    return {"mensagem": "Minha API está funcionando!"}

@router.get("/analises")
def get_analises():
    # Chama a função que processa os dados
    return data_service.processar_dados_aviacao()