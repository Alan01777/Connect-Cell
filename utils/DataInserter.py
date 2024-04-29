from streamlit_gsheets import GSheetsConnection
import streamlit as st
import pandas as pd


class DataInserter:
    def __init__(self):
        self.conn = GSheetsConnection("gsheets", type=GSheetsConnection)

    def insert_data(self, data: pd.DataFrame):
        # Check if 'df' is in the session state
        if 'df' not in st.session_state:
            # If not, read the existing data from the Google Sheets document
            st.session_state.df = self.conn.read()

        # Append the new row to the current data
        st.session_state.df = st.session_state.df.append(data, ignore_index=True)

        # Write the updated DataFrame back to the Google Sheets document
        self.conn.update(data=st.session_state.df)