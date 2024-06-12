from asyncio import sleep
import streamlit as st
import pandas as pd
from utils import DataLoader, DataInserter
from settings import page_settings


class ServiceRegistry:
    def __init__(self):
        st.set_page_config(
            page_title="Registro de Serviços",
            layout="wide",
            
        )

    def insert(self):

        st.title("Registro de Serviços")
        
        st.header("Detalhes do Serviço")
        col1, col2 = st.columns(2)

        with col1:
            client = st.text_input("Cliente")
        with col2:
            contact = st.text_input("Contato")
        with col2:
            date = st.date_input("Data")
            date_str = date.strftime("%d/%m/%Y")

        with col1:
            category = st.selectbox(
                "Categoria",
                [
                    "REPAROS HARDWARE",
                    "REPAROS SOFTWARE",
                    "VENDAS DISPOSITIVOS",
                    "VENDAS HARDWARE",
                    "VENDAS ACESSÓRIOS",
                    "OUTROS",
                ],
            )
        with col2:
            status_options = [
                "EM ANDAMENTO",
                "ENTREGUE",
                "DEVOLUÇÃO",
                "FINALIZADO",
                "ORÇAMENTO",
                "OUTROS"
            ]
            status = st.selectbox("Status", status_options)
        with col1:
            technician = st.selectbox("Técnico", ["TIAGO", "VALDERI"])
        product = st.text_area("Descrição do Produto/Serviço")

        st.header("Detalhes Financeiros")

        col1, col2 = st.columns(2)
        with col1:
            part_value = st.number_input("Total gasto com peças")
            service_value = st.number_input("Valor do Serviço")
        with col2:
            technician_percentage = st.selectbox("Porcentagem do técnico (%)", [30, 50, 80, 100])
            payment_method = st.selectbox(
                "Método de pagamento",
                ["DINHEIRO", "CREDITO", "DEBITO", "PIX", "OUTROS"],
            )

        brute_profit = service_value - part_value
        if technician_percentage == 100 or technician == "TIAGO":
            technician_value = brute_profit
            technician_percentage = 100
        else:
            technician_value = brute_profit * technician_percentage / 100

        if technician == "TIAGO":
            liquid_profit = brute_profit
        else:
            liquid_profit = brute_profit - technician_value

        data = {
            "DATA": [date_str],
            "CLIENTE": [client],
            "CONTATO": [contact],
            "STATUS": [status],
            "PRODUTO/SERVIÇO": [product],
            "CATEGORIA": [category],
            "DESPESAS": [part_value],
            "FATURAMENTO": [service_value],
            "TECNICO": [technician],
            "% DO TÉCNICO": [technician_percentage / 100],
            "LUCRO BRUTO": [brute_profit],
            "VALOR DO TÉCNICO": [technician_value],
            "LUCRO LIQUIDO": [liquid_profit],
            "F/PAGAMENTO": [payment_method],
        }

        if st.button("Inserir"):
            try:
                DataInserter().insert_data(pd.DataFrame.from_dict(data))
                st.success("Dados inseridos com sucesso!")
            except Exception as e:
                st.error(f"Erro ao inserir dados: {e}")


if __name__ == "__main__":
    registry = ServiceRegistry()
    registry.insert()
