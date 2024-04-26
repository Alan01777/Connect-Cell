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
    @st.cache_data
    def load_data(_self):
        df = pd.read_excel(_self.url, dtype=_self.types)
        return df