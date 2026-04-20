from fastapi import APIRouter
from app.services import cluster_service
import pandas as pd

router = APIRouter()

@router.get("/heatmapregioncluster")
def get_heatmap_region_cluster():
    # Carregamento e Processamento de Clustering
    df = pd.read_csv("ocorrencias_tratadas.csv")
    dataSet = cluster_service.Padornizador(df)
    amostra = cluster_service.ObterAmostra(dataSet)
    pca_data = cluster_service.ObterPcaData(dataSet)
    pca_data_amostra = cluster_service.ObterPcaDataAmostra(amostra)
    modelo = cluster_service.ObterModeloV1(pca_data_amostra)
    df_clusters = cluster_service.ObterDfClusters(df, modelo, pca_data)

    # 1. Mapeamento de UF para Região
    mapeamento_regioes = {
        'AC': 'Norte', 'AM': 'Norte', 'AP': 'Norte', 'PA': 'Norte', 'RO': 'Norte', 'RR': 'Norte', 'TO': 'Norte',
        'AL': 'Nordeste', 'BA': 'Nordeste', 'CE': 'Nordeste', 'MA': 'Nordeste', 'PB': 'Nordeste', 'PE': 'Nordeste', 'PI': 'Nordeste', 'RN': 'Nordeste', 'SE': 'Nordeste',
        'DF': 'Centro-Oeste', 'GO': 'Centro-Oeste', 'MT': 'Centro-Oeste', 'MS': 'Centro-Oeste',
        'ES': 'Sudeste', 'MG': 'Sudeste', 'RJ': 'Sudeste', 'SP': 'Sudeste',
        'PR': 'Sul', 'RS': 'Sul', 'SC': 'Sul'
    }

    # Criar a coluna 'regiao' baseada na coluna 'uf'
    df_clusters['regiao'] = df_clusters['uf'].map(mapeamento_regioes)

    # 2. Criar a tabela de contingência (Crosstab) por Região
    # index (Y) = Região, columns (X) = Cluster
    ct = pd.crosstab(df_clusters['regiao'], df_clusters['cluster'])

    # 3. Preparar os dados para o Plotly
    data = {
        "z": ct.values.tolist(),
        "x": [f"Cluster {c}" for c in ct.columns.tolist()],
        "y": ct.index.tolist() # Agora conterá Norte, Sul, etc.
    }
    
    return data