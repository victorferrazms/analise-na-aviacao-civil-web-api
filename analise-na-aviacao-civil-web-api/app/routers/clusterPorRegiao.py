from fastapi import APIRouter
from app.services import cluster_service
import pandas as pd

router = APIRouter()

@router.get("/clusterporregiao")
def get_clusters_by_region():
    # 1. Processamento dos Dados
    df = pd.read_csv("ocorrencias_tratadas.csv")
    dataSet = cluster_service.Padornizador(df)
    amostra = cluster_service.ObterAmostra(dataSet)
    pca_data = cluster_service.ObterPcaData(dataSet)
    pca_data_amostra = cluster_service.ObterPcaDataAmostra(amostra)
    modelo = cluster_service.ObterModeloV1(pca_data_amostra)
    df_clusters = cluster_service.ObterDfClusters(df, modelo, pca_data)

    # 2. CARACTERIZAÇÃO DINÂMICA (CORRIGIDA)
    # Criamos um mapeamento onde a chave é o ID (0, 1, 2, 3) 
    # e o valor é o nome técnico + ID para garantir que as colunas não se fundam
    nomes_clusters = {}
    for cluster_id in range(4):
        subset = df_clusters[df_clusters['cluster'] == cluster_id]
        
        if not subset.empty:
            tipo = subset['classificacao_da_ocorrencia'].mode()[0]
            fase = subset['fase_da_operacao'].mode()[0]
            # Adicionamos o ID (ex: C0, C1) para evitar nomes duplicados
            nomes_clusters[cluster_id] = f"C{cluster_id} - {tipo} ({fase})".upper()
        else:
            nomes_clusters[cluster_id] = f"C{cluster_id} - SEM DADOS"

    # 3. Mapeamento de Região
    mapeamento_regioes = {
        'AC': 'Norte', 'AM': 'Norte', 'AP': 'Norte', 'PA': 'Norte', 'RO': 'Norte', 'RR': 'Norte', 'TO': 'Norte',
        'AL': 'Nordeste', 'BA': 'Nordeste', 'CE': 'Nordeste', 'MA': 'Nordeste', 'PB': 'Nordeste', 'PE': 'Nordeste', 'PI': 'Nordeste', 'RN': 'Nordeste', 'SE': 'Nordeste',
        'DF': 'Centro-Oeste', 'GO': 'Centro-Oeste', 'MT': 'Centro-Oeste', 'MS': 'Centro-Oeste',
        'ES': 'Sudeste', 'MG': 'Sudeste', 'RJ': 'Sudeste', 'SP': 'Sudeste',
        'PR': 'Sul', 'RS': 'Sul', 'SC': 'Sul'
    }
    df_clusters['regiao'] = df_clusters['uf'].map(mapeamento_regioes)

    # 4. Agrupamento (Garante que os 4 IDs de cluster sejam processados separadamente)
    df_grouped = df_clusters.groupby(['regiao', 'cluster']).size().unstack(fill_value=0)
    
    # IMPORTANTE: Reindexar para garantir que se um cluster não tiver dados em NENHUMA 
    # região, ele ainda apareça como uma coluna de zeros em vez de sumir.
    for i in range(4):
        if i not in df_grouped.columns:
            df_grouped[i] = 0
            
    # Ordenar colunas para manter a ordem 0, 1, 2, 3
    df_grouped = df_grouped.sort_index(axis=1)
    df_grouped = df_grouped.reset_index()

    # 5. Aplicação dos Nomes na Coluna
    # Agora renomeamos apenas após garantir que temos as 4 colunas numéricas separadas
    df_grouped.columns = [nomes_clusters.get(c, c) if isinstance(c, int) else c for c in df_grouped.columns]

    return df_grouped.to_dict(orient='records')