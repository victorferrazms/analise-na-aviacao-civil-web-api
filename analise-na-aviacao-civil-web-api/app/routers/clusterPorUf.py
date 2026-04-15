from fastapi import APIRouter
from app.services import cluster_service
import pandas as pd

router = APIRouter()

@router.get("/clusterporuf")
def get_clusters_data():
    
    df = pd.read_csv("ocorrencias_tratadas.csv")
    dataSet = cluster_service.Padornizador(df)
    amostra = cluster_service.ObterAmostra(dataSet)
    pca_data = cluster_service.ObterPcaData(dataSet)
    pca_data_amostra = cluster_service.ObterPcaDataAmostra(amostra)
    modelo = cluster_service.ObterModeloV1(pca_data_amostra)
    df_clusters = cluster_service.ObterDfClusters(df, modelo, pca_data)
    
    # Supondo que df_clusters seja seu DataFrame original
    # 1. Agrupar e contar
    df_grouped = df_clusters.groupby(['uf', 'cluster']).size().unstack(fill_value=0)
    
    # 2. Resetar o index para que 'uf' vire uma coluna
    df_grouped = df_grouped.reset_index()
    
    # 3. Renomear as colunas para facilitar o mapeamento no Recharts (ex: cluster0, cluster1...)
    # Transformamos colunas numéricas [0, 1, 2, 3] em strings ['cluster0', 'cluster1'...]
    df_grouped.columns = [f'cluster{c}' if isinstance(c, int) else c for c in df_grouped.columns]
    
    # 4. Converter para lista de dicionários (formato JSON que o React entende)
    chart_data = df_grouped.to_dict(orient='records')
    
    return chart_data
