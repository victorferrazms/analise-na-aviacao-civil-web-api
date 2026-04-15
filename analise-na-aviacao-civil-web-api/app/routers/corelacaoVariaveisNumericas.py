from fastapi import APIRouter
from app.services import cluster_service
import pandas as pd

router = APIRouter()

@router.get("/correlacao")
def get_correlation():
    
    df = pd.read_csv("ocorrencias_tratadas.csv")
    
    # 1. Selecionar apenas colunas numéricas (usando sua lógica)
    NUMERICAL_FEATURES = df.select_dtypes(include=['number']).columns.tolist()
    
    if len(NUMERICAL_FEATURES) < 2:
        return {"error": "Dados insuficientes para correlação"}, 400

    # 2. Calcular a matriz de correlação
    correlation_matrix = df[NUMERICAL_FEATURES].corr()

    # 3. Preparar os dados para o Plotly
    # O Plotly espera: z (matriz de valores), x (labels), y (labels)
    data = {
        "z": correlation_matrix.values.tolist(),      # Matriz 2D
        "x": correlation_matrix.columns.tolist(),    # Nomes das colunas
        "y": correlation_matrix.index.tolist()       # Nomes das linhas (iguais às colunas)
    }
    
    return data
