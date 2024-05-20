import streamlit as st
import pandas as pd
from utils import DataLoader, DateFilter, DataInserter
from settings import page_settings

page_settings("Tabela de Serviços", "📊")


@st.cache_data
def load_data():
    return DataLoader().load_data()


def display_dataframe(df):
    st.title("Tabela de Serviços")
    col1, col2 = st.columns(2)

    date_filter = DateFilter(df, "DATA")

    df = date_filter.filter_by_date()
    colI, colII = st.columns(2)
    with colI:
        search_term = st.text_input("Buscar por termo")
    with colII:
        st.selectbox("Filtrar por categoria", ["TODOS"] + list(df["CATEGORIA"].unique()))
    with col1:
        selected_status = st.selectbox(
            "Filtrar por status", ["TODOS"] + list(df["STATUS"].unique())
        )
    with col2:
        selected_technician = st.selectbox(
            "Filtrar por técnico", ["TODOS"] + list(df["TECNICO"].unique())
        )

    df = apply_filters(df, search_term, selected_status, selected_technician)
    df["DATA"] = df["DATA"].dt.strftime("%d/%m/%Y")
    monetary_columns = [
        "(R$)PEÇA",
        "LUCRO BRUTO",
        "VALOR TOTAL DO SERVIÇO",
        "LUCRO LIQUIDO",
        "VALOR DO TÉCNICO",
    ]
    df["% DO TÉCNICO"] = (df["% DO TÉCNICO"] * 100).map("{:.0f}%".format)
    return df


def apply_filters(df, search_term, selected_status, selected_technician):
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


def main():
    data = load_data()
    data = display_dataframe(data)
    st.dataframe(data)
    # data_dict = new_data.to_dict(orient="records")
    
    # if st.button("Salvar"):
    #     DataInserter().update_data(pd.DataFrame.from_dict(data_dict))
    #     st.success("Dados salvos com sucesso!")
        
if __name__ == "__main__":
    main()
