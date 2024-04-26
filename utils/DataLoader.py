import streamlit as st
import pandas as pd

class DataLoader:
    def __init__(self):
        self.url = st.secrets["Database_url"]["url"]
        self.types = {
            "CONTATO": str,
            "(R$)PEÇA": float,
            "VALOR TOTAL DO SERVIÇO": float,
            "LUCRO BRUTO": float,
            "VALOR DO TÉCNICO": float,
            "LUCRO LIQUIDO": float,
        }

    st.cache_data
    def load_data(self):
        return pd.read_excel(self.url, dtype=self.types)