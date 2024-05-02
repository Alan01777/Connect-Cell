import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

class DataLoader:
    def __init__(self):
        self.conn = GSheetsConnection("gsheets", type=GSheetsConnection)

    def load_data(self):
        st.cache_data.clear()
        try:
            self.df = self.conn.read()
            return self.df
        except Exception as e:
            return st.error(f"Erro ao carregar os dados: {e}")
