import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

class DataLoader:
    def __init__(self):
        self.conn = st.connection("gsheets", type=GSheetsConnection)
        self.df = self.conn.read()
        
        
    @st.cache_data
    def load_data(_self):
        return _self.df