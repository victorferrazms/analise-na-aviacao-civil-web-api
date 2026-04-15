from fastapi import APIRouter
from app.services import cluster_service
import pandas as pd

router = APIRouter()

@router.get("/heatmapufcluster")
def get_heatmap_uf_cluster():
    
    df = pd.read_csv("ocorrencias_tratadas.csv")
    dataSet = cluster_service.Padornizador(df)
    amostra = cluster_service.ObterAmostra(dataSet)
    pca_data = cluster_service.ObterPcaData(dataSet)
    pca_data_amostra = cluster_service.ObterPcaDataAmostra(amostra)
    modelo = cluster_service.ObterModeloV1(pca_data_amostra)
    df_clusters = cluster_service.ObterDfClusters(df, modelo, pca_data)
    
    # 1. Criar a tabela de contingência (Crosstab)
    # index (Y) = UF, columns (X) = Cluster
    ct = pd.crosstab(df_clusters['uf'], df_clusters['cluster'])
    
    # 2. Preparar os dados para o Plotly
    # Precisamos dos nomes das UFs (Y), dos Clusters (X) e dos valores (Z)
    data = {
        "z": ct.values.tolist(),          # Matriz de contagens
        "x": [f"Cluster {c}" for c in ct.columns.tolist()], # Labels do topo
        "y": ct.index.tolist()            # Labels da lateral (UFs)
    }
    
    return data