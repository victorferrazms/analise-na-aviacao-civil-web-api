from sklearn.compose import ColumnTransformer
from sklearn.model_selection import train_test_split
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.preprocessing import MinMaxScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelEncoder
import pandas as pd
import unidecode

#RETORNA O PCA_DATA_AMOSTRA
def ObterPcaDataAmostra(amostra: any):
    pca_model = PCA(n_components = 2)
    pca_data_amostra = pca_model.fit_transform(amostra) 
    return pca_data_amostra

#RETORNA O MODELO_V1
def ObterModeloV1(pcaDataAmostra: any):
    modelo_v1 = KMeans(n_clusters = 4, n_init='auto', random_state=42)
    modelo_v1.fit(pcaDataAmostra)
    return modelo_v1

#RETORNO O PCA_DATA
def ObterPcaData(dataSet: any):
    pca_model = PCA(n_components = 2)
    pca_model.fit(dataSet)
    pca_data = pca_model.transform(dataSet)
    return pca_data

#RETORNAO DF_CLUSTERS
def ObterDfClusters(dataFrame: pd.DataFrame, modelo: KMeans, pcaData: any):
    df_clusters = dataFrame.copy()
    df_clusters['cluster'] = modelo.predict(pcaData)
    return df_clusters

#GERA E RETORNA UMA AMOSTRA
def ObterAmostra(dataSet: any):
    amostra1, amostra2 = train_test_split(dataSet, train_size = .01, random_state=42)
    return amostra1

#RETORNA O DATAFRAME PADRONIZADO
def Padornizador(dataFrame: pd.DataFrame):
    
    NUMERICAL_FEATURES = dataFrame.select_dtypes(include=['number']).columns.tolist()
    CATEGORICAL_FEATURES = dataFrame.select_dtypes(include=['object', 'category']).columns.tolist()

    preprocessor = ColumnTransformer(
        transformers=[
            ('num',
            Pipeline([
                ('imputer', SimpleImputer(strategy='median')),
                ('scaler', MinMaxScaler())
            ]),
            NUMERICAL_FEATURES),
            ('cat', OneHotEncoder(handle_unknown='ignore', sparse_output=False), CATEGORICAL_FEATURES)
        ],
        remainder='drop'
    )

    dataset_padronizado = preprocessor.fit_transform(dataFrame)
    return dataset_padronizado

def processarDadosMapa():
    # 1. Carga dos dados
    df = pd.read_csv("ocorrencias_tratadas.csv")
    
    variaveis = ["classificacao_da_ocorrencia", "uf", "fase_da_operacao", "tipo_de_ocorrencia"]
    df_cat = df[variaveis].copy()

    for col in variaveis:
        print(f"Processando coluna: {col}") # Debug para ver em qual coluna trava
        
        # 1. Limpeza radical: Garante string ANTES de qualquer processamento
        # Usamos string(x) dentro do lambda para garantir que nem o unidecode veja floats
        df_cat[col] = (
            df_cat[col]
            .apply(lambda x: unidecode.unidecode(str(x)).lower().strip() if pd.notnull(x) else "nao informado")
        )
        
        # 2. Segunda barreira: remover possíveis strings "nan" que o pandas gera
        df_cat[col] = df_cat[col].replace(["nan", "none", ""], "nao informado")
        
        # 3. LabelEncoder
        le = LabelEncoder()
        # Forçamos .astype(str) uma última vez por segurança
        df_cat[col] = le.fit_transform(df_cat[col].astype(str))
    
    # 3. Aplicação do K-Means (4 clusters como definido)
    kmeans = KMeans(n_clusters=4, random_state=42)
    df["cluster"] = kmeans.fit_predict(df_cat)

    # 4. Limpeza Geográfica (Seu bloco 6)
    df_geo = df.copy()
    
    # Padronização e limpeza de coordenadas
    for col in ["latitude", "longitude"]:
        df_geo[col] = df_geo[col].astype(str).apply(lambda x: unidecode.unidecode(x).strip().lower())
        df_geo[col] = df_geo[col].str.replace(",", ".", regex=False)
    
    # Remove "nao informado" e converte para float
    df_geo = df_geo[
        (df_geo["latitude"] != "nao informado") & 
        (df_geo["longitude"] != "nao informado")
    ]
    
    df_geo["latitude"] = pd.to_numeric(df_geo["latitude"], errors='coerce')
    df_geo["longitude"] = pd.to_numeric(df_geo["longitude"], errors='coerce')
    
    # Filtro geográfico Brasil
    df_geo = df_geo.dropna(subset=["latitude", "longitude"])
    df_geo = df_geo[
        (df_geo["latitude"] >= -35) & (df_geo["latitude"] <= 6) &
        (df_geo["longitude"] >= -75) & (df_geo["longitude"] <= -30)
    ]
   
    # Seleciona apenas o necessário para o Front-end para economizar banda
    colunas_finais = [
        "latitude", "longitude", "cluster", 
        "classificacao_da_ocorrencia", "municipio", "uf"
    ]
    
    df_final = df_geo[colunas_finais].copy()

    # 2. A SOLUÇÃO: Converter NaN para None
    # O Python converte 'None' para 'null' no JSON, o que é 100% válido.
    df_dict = df_final.replace({pd.NA: None, float('nan'): None}).where(pd.notnull(df_final), None).to_dict(orient='records')
    
    return df_dict