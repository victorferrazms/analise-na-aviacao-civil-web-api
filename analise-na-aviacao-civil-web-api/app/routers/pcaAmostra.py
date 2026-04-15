from fastapi import APIRouter
from app.services import cluster_service
import pandas as pd

router = APIRouter()

@router.get("/pcaamostra")
def read_root():
    
    df = pd.read_csv("ocorrencias_tratadas.csv")
    dataSet = cluster_service.Padornizador(df)
    amostra = cluster_service.ObterAmostra(dataSet)
    pca_data_amostra = cluster_service.ObterPcaDataAmostra(amostra)

    modelo_v1 = cluster_service.ObterModeloV1(pca_data_amostra)

    data_to_send = [
        {"pc1": float(row[0]), "pc2": float(row[1]), "cluster": int(label)}
        for row, label in zip(pca_data_amostra, modelo_v1.labels_)
    ]  
    return data_to_send
