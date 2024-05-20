import streamlit as st
import pandas as pd
from utils import DataLoader, DateFilter, DataInserter
from settings import page_settings

class ServiceTableApp:
    def __init__(self):
        self.data = None

    @staticmethod
    @st.cache_data
    def load_data():
        return DataLoader().load_data()

    def display_filters(self, df):
        col1, col2 = st.columns(2)
        
        with col1:
            search_term = st.text_input("Buscar por termo")
        with col2:
            st.selectbox("Filtrar por categoria", ["TODOS"] + list(df["CATEGORIA"].unique()))
        
        with col1:
            selected_status = st.selectbox("Filtrar por status", ["TODOS"] + list(df["STATUS"].unique()))
        with col2:
            selected_technician = st.selectbox("Filtrar por técnico", ["TODOS"] + list(df["TECNICO"].unique()))
        
        return search_term, selected_status, selected_technician

    def apply_filters(self, df, search_term, selected_status, selected_technician):
        if search_term:
            df = df[
                df["CLIENTE"].str.contains(search_term, case=False)
                | df["TECNICO"].str.contains(search_term, case=False)
                | df["CATEGORIA"].str.contains(search_term, case=False)
                | df["PRODUTO/SERVIÇO"].str.contains(search_term, case=False)
                | df["CONTATO"].str.contains(search_term, case=False)
            ]

        if selected_status != "TODOS":
            df = df[df["STATUS"] == selected_status]

        if selected_technician != "TODOS":
            df = df[df["TECNICO"] == selected_technician]

        return df

    @staticmethod
    def format_dataframe(df):
        df["DATA"] = df["DATA"].dt.strftime("%d/%m/%Y")
        df["% DO TÉCNICO"] = (df["% DO TÉCNICO"] * 100).map("{:.0f}%".format)
        
        monetary_columns = [
            "DESPESAS",
            "LUCRO BRUTO",
            "FATURAMENTO",
            "LUCRO LIQUIDO",
            "VALOR DO TÉCNICO",
        ]
        for col in monetary_columns:
            df[col] = df[col].map("R${:,.2f}".format)

        return df

    def display_dataframe(self):
        st.title("Tabela de Serviços")

        date_filter = DateFilter(self.data, "DATA")
        self.data = date_filter.filter_by_date()
        
        search_term, selected_status, selected_technician = self.display_filters(self.data)
        
        self.data = self.apply_filters(self.data, search_term, selected_status, selected_technician)
        self.data = self.format_dataframe(self.data)
        
        st.dataframe(self.data)

    def run(self):
        page_settings("Tabela de Serviços", "📊")
        self.data = self.load_data()
        self.display_dataframe()
        # Uncomment the lines below if you want to enable data saving functionality
        # if st.button("Salvar"):
        #     DataInserter().update_data(self.data)
        #     st.success("Dados salvos com sucesso!")

if __name__ == "__main__":
    app = ServiceTableApp()
    app.run()