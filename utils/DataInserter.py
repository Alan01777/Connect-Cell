from streamlit_gsheets import GSheetsConnection
import streamlit as st
import pandas as pd

from utils import DataLoader

class DataInserter:
    def __init__(self):
        self.conn = GSheetsConnection("gsheets", type=GSheetsConnection)
        self.old_data = DataLoader().load_data()
        
    def insert_data(self, data):
        self.df = self.df.append(data, ignore_index=True)
        self.conn.update(data=self.df)
        
    def update_data(self, new_data, old_data):
        # compare all the rows in the new data with the old data
        # if the row is not in the old data or if the row is in the old data but has different values, update the row
        for index, row in new_data.iterrows():
            if index not in old_data.index or not old_data.loc[index].equals(row):
                old_data.loc[index] = row
        self.conn.update(data=old_data)
        st.rerun() 