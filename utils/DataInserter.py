from streamlit_gsheets import GSheetsConnection
import streamlit as st
import pandas as pd

from utils import DataLoader

class DataInserter:
    def __init__(self):
        self.conn = GSheetsConnection("gsheets", type=GSheetsConnection)
        self.df = DataLoader().load_data()
        
    def insert_data(self, data):
        self.df = self.df.append(data, ignore_index=True)
        self.conn.update(data=self.df)
        
    def update_data(self, data):
        self.conn.update(data=data)
        st.cache_data.clear()
        st.rerun()