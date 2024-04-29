import streamlit as st
from streamlit_gsheets import GSheetsConnection

class DataLoader:
    def __init__(self):
        self.conn = None

    def load_data(self):
        # Disconnect from Google Sheets
        self.conn = None
        self.df = None

        # Reestablish the connection with Google Sheets
        self.conn = GSheetsConnection("gsheets", type=GSheetsConnection)
        self.df = self.conn.read()

        return self.df

