import streamlit as st
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

    search_term = st.text_input("Buscar por cliente ou técnico")
    with col1:
        selected_status = st.selectbox(
            "Filtrar por status", ["All"] + list(df["STATUS"].unique())
        )
    with col2:
        selected_technician = st.selectbox(
            "Filtrar por técnico", ["All"] + list(df["TECNICO"].unique())
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
        ]

    if selected_status != "All":
        df = df[df["STATUS"] == selected_status]

    if selected_technician != "All":
        df = df[df["TECNICO"] == selected_technician]

    return df


def main():
    data = load_data()
    data = display_dataframe(data)
    new_data = st.data_editor(data, num_rows="dynamic")

    if st.button("Atualizar"):
        if not new_data.equals(data):
            st.success("Data has been updated!")
            DataInserter().update_data(new_data)


if __name__ == "__main__":
    main()
