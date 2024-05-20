from streamlit_gsheets import GSheetsConnection
import streamlit as st
import pandas as pd

class DataInserter:
    def __init__(self):
        self.conn = GSheetsConnection("gsheets", type=GSheetsConnection)

    def insert_data(self, data: pd.DataFrame):
        if 'df' not in st.session_state:
            st.session_state.df = self.conn.read()
        st.session_state.df = st.session_state.df.append(data, ignore_index=True)
        self.conn.update(data=st.session_state.df)
        
    def update_data(self, data: pd.DataFrame):
        if 'df' not in st.session_state:
            st.session_state.df = self.conn.read()
            st.session_state.df = st.session_state.df.append(data, ignore_index=True)
            self.conn.update(data=st.session_state.df)