import streamlit as st
from streamlit_gsheets import GSheetsConnection


class DataLoader:
    def __init__(self):
        self.conn = GSheetsConnection("gsheets", type=GSheetsConnection)

    def load_data(self):
        st.cache_data.clear()
        self.df = self.conn.read()

        return self.df
