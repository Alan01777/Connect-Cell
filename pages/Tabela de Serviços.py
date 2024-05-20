import streamlit as st
import pandas as pd
from utils import DataLoader, DataInserter

class ServiceRegistry:
    def __init__(self):
        self.data = {}
    
    def input_client_info(self):
        st.header("Detalhes do Serviço")
        col1, col2, col3 = st.columns(3)
        with col1:
            self.data["CLIENTE"] = st.text_input("Cliente")
        with col2:
            self.data["CONTATO"] = st.text_input("Contato")
        with col3:
            date = st.date_input("Data")
            self.data["DATA"] = date.strftime("%d/%m/%Y")
    
    def input_service_details(self):
        col1, col2, col3 = st.columns(3)
        with col1:
            self.data["CATEGORIA"] = st.selectbox(
                "Categoria",
                [
                    "REPAROS HARDWARE",
                    "REPAROS SOFTWARE",
                    "VENDAS DISPOSITIVOS",
                    "VENDAS HARDWARE",
                    "VENDAS ACESSÓRIOS",
                    "OUTROS",
                ]
            )
        with col2:
            status_options = [
                "EM ANDAMENTO",
                "ENTREGUE",
                "DEVOLUÇÃO",
                "FINALIZADO",
                "ORÇAMENTO",
            ]
            self.data["STATUS"] = st.selectbox("Status", status_options)
        with col3:
            self.data["TECNICO"] = st.selectbox("Técnico", ["TIAGO", "VALDERI"])
        self.data["PRODUTO/SERVIÇO"] = st.text_area("Descrição do Produto/Serviço")
    
    def input_financial_details(self):
        st.header("Detalhes Financeiros")
        col1, col2 = st.columns(2)
        with col1:
            self.data["(R$)PEÇA"] = st.number_input("Total gasto com peças")
            self.data["VALOR TOTAL DO SERVIÇO"] = st.number_input("Valor do Serviço")
        with col2:
            self.data["% DO TÉCNICO"] = st.selectbox("% do técnico", [30, 50, 80, 100]) / 100
            self.data["F/PAGAMENTO"] = st.selectbox(
                "Método de pagamento",
                ["Dinheiro", "Cartão de crédito", "Cartão de débito", "Pix"]
            )
        
        self.calculate_profits()
    
    def calculate_profits(self):
        part_value = self.data["(R$)PEÇA"]
        service_value = self.data["VALOR TOTAL DO SERVIÇO"]
        technician_percentage = self.data["% DO TÉCNICO"]
        
        self.data["LUCRO BRUTO"] = service_value - part_value
        self.data["VALOR DO TÉCNICO"] = technician_percentage * self.data["LUCRO BRUTO"]
        self.data["LUCRO LIQUIDO"] = self.data["LUCRO BRUTO"] - self.data["VALOR DO TÉCNICO"]
    
    def insert_data(self):
        if st.button("Inserir"):
            try:
                DataInserter().insert_data(pd.DataFrame([self.data]))
                with st.expander("Dados inseridos:", expanded=True):
                    st.dataframe(pd.DataFrame([self.data]))
                st.success("Dados inseridos com sucesso!")
            except Exception as e:
                st.error(f"Erro ao inserir dados: {e}")
    
    def display_page(self):
        self.input_client_info()
        self.input_service_details()
        self.input_financial_details()
        self.insert_data()

def main():
    st.title("Registro de Serviços (Não Funcional!)")
    service_registry = ServiceRegistry()
    service_registry.display_page()

if __name__ == "__main__":
    main()