"""
Pipeline ETL Automatizado – ANAC (TCC)
--------------------------------------
Este script implementa um sistema automatizado para:
Etapas:
1️⃣ Extração (E): obtém os dados em formato CSV diretamente do portal de Dados Abertos da ANAC.
2️⃣ Transformação (T): padroniza os nomes das colunas, trata valores nulos e remove duplicatas.
3️⃣ Carga (L): exporta os dados tratados para um arquivo CSV local.
"""

import pandas as pd
import schedule
import time
import logging
import requests
from io import StringIO
from datetime import datetime

# ======================
# CONFIGURAÇÕES
# ======================
URL_CSV = "https://sistemas.anac.gov.br/dadosabertos/Seguranca%20Operacional/Ocorrencia/V_OCORRENCIA_AMPLA.csv"
ARQUIVO_LOCAL = "ocorrencias_tratadas.csv"

# Configuração de LOG
logging.basicConfig(
    filename="pipeline.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# ======================
# ETL FUNCTIONS
# ======================

def extrair_dados():
    """
    Etapa 1 - Extração
    Baixa o CSV diretamente do portal de Dados Abertos da ANAC.
    """
    try:
        response = requests.get(URL_CSV)
        response.raise_for_status()
        logging.info("Extração concluída com sucesso.")

        # Remove a primeira linha ("Atualizado em: ...")
        linhas = response.text.splitlines()
        linhas_sem_cabecalho_extra = "\n".join(linhas[1:])

        dados_csv = StringIO(linhas_sem_cabecalho_extra)
        df = pd.read_csv(dados_csv, sep=';', low_memory=False)
        return df
    except Exception as e:
        logging.error(f"Erro na extração: {e}")
        return None


def transformar_dados(df):
    """
    Etapa 2 - Transformação
    Padroniza nomes e trata valores nulos.
    """
    if df is None or df.empty:
        logging.warning("Nenhum dado disponível para transformar.")
        return None

     # -------------------------------
    # 1) Padroniza nomes das colunas
    # -------------------------------
    df.columns = (
        df.columns.str.strip()
        .str.replace(" ", "_")
        .str.replace("ã", "a")
        .str.replace("é", "e")
        .str.lower()
    )

    # -----------------------------------
    # 2) Padroniza textos para evitar erros
    # -----------------------------------
    df = df.map(
        lambda x: str(x).strip().upper() if isinstance(x, str) else x
    )

    # ---------------------------------------------------------
    # 3) Padroniza valores inconsistentes ("NAO INFORMADO", etc)
    # ---------------------------------------------------------
    padroes_ruins = ["NAO INFORMADO", "NÃO INFORMADO", "INDETERMINADO",
                     "IGNORADO", "N/I", "NONE", "NULL", ""]
    for col in df.columns:
        df[col] = df[col].replace(padroes_ruins, "NAO INFORMADO")

    # -------------------------------
    # 4) Converte datas
    # -------------------------------
    if "data_da_ocorrencia" in df.columns:
        df["data_da_ocorrencia"] = pd.to_datetime(
            df["data_da_ocorrencia"],
            errors="coerce"
        )

    # -------------------------------
    # 5) Converte números
    # -------------------------------
    num_cols = [
        col for col in df.columns
        if "lesoes" in col or "ilesos" in col or col in ["pmd", "numero_de_assentos"]
    ]

    for col in num_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    # -------------------------------
    # 6) Tratar latitude e longitude
    # -------------------------------
    if "latitude" in df.columns and "longitude" in df.columns:
        df["latitude"] = df["latitude"].astype(str).str.replace(",", ".", regex=False)
        df["longitude"] = df["longitude"].astype(str).str.replace(",", ".", regex=False)

        def to_float_safe(value):
            try:
                return float(value)
            except:
                return None

        df["latitude"] = df["latitude"].apply(to_float_safe)
        df["longitude"] = df["longitude"].apply(to_float_safe)

        # Remove coordenadas fora do Brasil
        df = df[
            (df["latitude"].between(-60, 15)) &
            (df["longitude"].between(-85, -30))
        ]

    # -------------------------------
    # 7) Remove duplicatas
    # -------------------------------
    if "numero_da_ocorrencia" in df.columns:
        df = df.drop_duplicates(subset=["numero_da_ocorrencia"], keep="first")

    logging.info("Transformação concluída: dados totalmente tratados.")
    return df

def carregar_dados(df):
    """
    Etapa 3 - Carga
    Salva os dados tratados em um arquivo CSV local.
    """
    if df is None or df.empty:
        logging.warning("Nenhum dado disponível para carregar.")
        return

    df.to_csv(ARQUIVO_LOCAL, index=False, encoding='utf-8-sig')
    logging.info(f"Arquivo salvo com sucesso em: {ARQUIVO_LOCAL}")


def executar_pipeline():
    """
    Função principal do pipeline.
    """
    logging.info("Iniciando pipeline ETL...")
    df = extrair_dados()
    df_tratado = transformar_dados(df)
    carregar_dados(df_tratado)
    logging.info("Pipeline concluído com sucesso.")
    
