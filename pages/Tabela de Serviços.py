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
            selected_category = st.selectbox(
                "Filtrar por categoria", ["TODOS"] + list(df["CATEGORIA"].unique())
            )

        with col1:
            selected_status = st.selectbox(
                "Filtrar por status", ["TODOS"] + list(df["STATUS"].unique())
            )
        with col2:
            selected_technician = st.selectbox(
                "Filtrar por técnico", ["TODOS"] + list(df["TECNICO"].unique())
            )

        return search_term, selected_status, selected_technician, selected_category

    def apply_filters(self, df, search_term, selected_status, selected_technician, selected_category):
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
            
        if selected_category != "TODOS":
            df = df[df["CATEGORIA"] == selected_category]

        return df

    @staticmethod
    def format_dataframe(df):
        df["DATA"] = df["DATA"].dt.strftime("%d/%m/%Y")
        return df

    def display_dataframe(self):
        st.title("Tabela de Serviços")

        date_filter = DateFilter(self.data, "DATA")
        filtered_data = (
            date_filter.filter_by_date().copy()
        )

        search_term, selected_status, selected_technician, selected_category = self.display_filters(
            filtered_data
        )

        filtered_data = self.apply_filters(
            filtered_data, search_term, selected_status, selected_technician, selected_category
        )

        filtered_data = self.format_dataframe(filtered_data)

        new_data = st.data_editor(
            filtered_data,
            num_rows="fixed",
            column_config={
                "STATUS": st.column_config.SelectboxColumn(
                    "STATUS",
                    help="Selecione o status do serviço",
                    width="small",
                    options=[
                        "EM ANDAMENTO",
                        "ENTREGUE",
                        "DEVOLUÇÃO",
                        "FINALIZADO",
                        "ORÇAMENTO",
                        "OUTROS",
                    ],
                    required=True,
                ),
                "CATEGORIA": st.column_config.SelectboxColumn(
                    "CATEGORIA",
                    help="Selecione a categoria do serviço",
                    width="medium",
                    options=[
                        "REPAROS HARDWARE",
                        "REPAROS SOFTWARE",
                        "VENDAS DISPOSITIVOS",
                        "VENDAS HARDWARE",
                        "VENDAS ACESSÓRIOS",
                        "OUTROS",
                    ],
                    required=True,
                ),
                "TECNICO": st.column_config.SelectboxColumn(
                    "TECNICO",
                    help="Selecione o técnico responsável pelo serviço",
                    width="medium",
                    options=["TIAGO", "VALDERI"],
                    required=True,
                ),
                "% DO TÉCNICO": st.column_config.SelectboxColumn(
                    "% DO TÉCNICO",
                    help="Porcentagem do valor do serviço que será destinado ao técnico",
                    width="small",
                    options=[0.3, 0.5, 0.8, 1],
                    required=True,
                ),
                "F/PAGAMENTO": st.column_config.SelectboxColumn(
                    "F/PAGAMENTO",
                    help="Selecione o método de pagamento",
                    width="medium",
                    options=["DINHEIRO", "CREDITO", "DEBITO", "PIX", "OUTROS"],
                    required=True,
                ),
            },
        )
        old_data = self.load_data()
        if st.button("Salvar"):
            try:
                DataInserter().update_data(new_data, old_data)
                st.success("Dados salvos com sucesso!")
            except Exception as e:
                st.error(f"Erro ao salvar dados: {e}")

    def run(self):
        page_settings("Tabela de Serviços", "📊")
        self.data = self.load_data()
        self.display_dataframe()


if __name__ == "__main__":
    app = ServiceTableApp()
    app.run()
