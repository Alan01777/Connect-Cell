from asyncio import sleep
import streamlit as st
import pandas as pd
from utils import DataLoader, DataInserter


def main():

    st.title("Registro de Serviços")

    # Data e Informações do Cliente
    st.header("Detalhes do Serviço")
    client = st.text_input("Cliente")
    col1, col2 = st.columns(2)
    with col1:
        contact = st.text_input("Contato")
    with col2:
        date = st.date_input("Data")
        date_str = date.strftime("%d/%m/%Y")

    # Status e Descrição do Serviço
    status_options = ["EM ANDAMENTO", "ENTREGUE", "DEVOLUÇÃO", "FINALIZADO", "ORÇAMENTO"]
    status = st.selectbox("Status", status_options)
    technician = st.selectbox("Técnico", ["TIAGO", "VALDERI"])
    product = st.text_area("Descrição do Produto/Serviço")

    st.header("Detalhes Financeiros")

    # Valores e Pagamento
    col1, col2 = st.columns(2)
    with col1:
        part_value = st.number_input("Total gasto com peças")
        service_value = st.number_input("Valor do Serviço")
    with col2:
        technician_percentage = st.number_input("% do técnico (0.3, 0.8, etc.)")
        payment_method = st.selectbox(
            "Método de pagamento",
            ["Dinheiro", "Cartão de crédito", "Cartão de débito", "Pix"],
        )

    # Cálculos de Lucro
    brute_profit = service_value - part_value
    technician_value = technician_percentage * brute_profit
    liquid_profit = brute_profit if technician_percentage == 1 else brute_profit - (brute_profit * technician_percentage)

    data = {
        "DATA": [date_str],
        "CLIENTE": [client],
        "CONTATO": [contact],
        "STATUS": [status],
        "PRODUTO/SERVIÇO": [product],
        "(R$)PEÇA": [part_value],
        "VALOR TOTAL DO SERVIÇO": [service_value],
        "TECNICO": [technician],
        "% DO TÉCNICO": [technician_percentage],
        "LUCRO BRUTO": [brute_profit],
        "VALOR DO TÉCNICO": [technician_value],
        "LUCRO LIQUIDO": [liquid_profit],
        "F/PAGAMENTO": [payment_method],
    }

    if st.button("Inserir"):
        try:    
            DataInserter().insert_data(pd.DataFrame.from_dict(data))
            with st.expander("Dados inseridos:", expanded=True):
                st.dataframe(pd.DataFrame.from_dict(data))
            #show the inserted data as a popup
            st.success("Dados inseridos com sucesso!")
        except Exception as e:
            st.error(f"Erro ao inserir dados: {e}")

if __name__ == "__main__":
    main()