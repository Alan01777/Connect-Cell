import streamlit as st

class page_settings:
    def __init__(self, title, icon):
        st.set_page_config(
            page_title=title,
            page_icon=icon,
            layout="wide",
            initial_sidebar_state="collapsed",
        )