import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from typing import Optional
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataLoader:
    """Carregador de dados otimizado com cache"""

    _instance = None
    _conn = None

    def __new__(cls):
        """Singleton pattern para reutilizar conexão"""
        if cls._instance is None:
            cls._instance = super(DataLoader, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if self._conn is None:
            try:
                self._conn = GSheetsConnection("gsheets", type=GSheetsConnection)
            except Exception as e:
                logger.error(f"Erro ao criar conexão: {e}")
                raise

    @st.cache_data(ttl=3600, show_spinner=False)
    def load_data(_self) -> Optional[pd.DataFrame]:
        """
        Carrega dados do Google Sheets com cache de 1 hora

        Returns:
            DataFrame com os dados ou None em caso de erro
        """
        try:
            logger.info("Carregando dados do Google Sheets...")
            df = _self._conn.read()

            if df is None or df.empty:
                logger.warning("Dados vazios recebidos")
                st.warning("⚠️ Nenhum dado encontrado na planilha")
                return pd.DataFrame()

            # Validar colunas essenciais
            required_columns = [
                "DATA", "CLIENTE", "FATURAMENTO", "DESPESAS",
                "LUCRO LIQUIDO", "CATEGORIA", "TECNICO"
            ]

            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                logger.error(f"Colunas faltando: {missing_columns}")
                st.error(f"❌ Colunas faltando na planilha: {', '.join(missing_columns)}")
                return pd.DataFrame()

            # Limpar e preparar dados
            df = _self._clean_data(df)

            logger.info(f"Dados carregados com sucesso: {len(df)} registros")
            return df

        except Exception as e:
            logger.error(f"Erro ao carregar dados: {e}")
            st.error(f"❌ Erro ao carregar os dados: {e}")
            return pd.DataFrame()

    @staticmethod
    def _clean_data(df: pd.DataFrame) -> pd.DataFrame:
        """
        Limpa e prepara os dados

        Args:
            df: DataFrame bruto

        Returns:
            DataFrame limpo
        """
        # Remover linhas completamente vazias
        df = df.dropna(how='all')

        # Converter tipos de dados
        numeric_columns = ["FATURAMENTO", "DESPESAS", "LUCRO LIQUIDO",
                          "LUCRO BRUTO", "VALOR DO TÉCNICO"]

        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

        # Preencher valores nulos em colunas de texto
        text_columns = ["CLIENTE", "CATEGORIA", "TECNICO", "STATUS"]
        for col in text_columns:
            if col in df.columns:
                df[col] = df[col].fillna("N/A")

        return df

    @staticmethod
    def clear_cache():
        """Limpa o cache de dados"""
        st.cache_data.clear()
        logger.info("Cache limpo")
