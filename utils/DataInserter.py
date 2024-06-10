from streamlit_gsheets import GSheetsConnection
import streamlit as st
import pandas as pd

from utils import DataLoader

class DataInserter:
    def __init__(self):
        self.conn = GSheetsConnection("gsheets", type=GSheetsConnection)
        self.old_data = DataLoader().load_data()
        self.df = pd.DataFrame()
        
    def insert_data(self, data):
        self.df = self.df.append(data, ignore_index=True)
        self.conn.update(data=self.df)
        
    def update_data(self, new_data, old_data):
        updated = False
        for index, row in new_data.iterrows():
            if index not in old_data.index or not old_data.loc[index].equals(row):
                old_data.loc[index] = row
                updated = True
        if updated:
            self.conn.update(data=old_data)
            st.rerun()