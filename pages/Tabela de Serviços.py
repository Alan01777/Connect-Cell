import streamlit as st
from utils import DataLoader, DateFilter
from settings import page_settings

page_settings("Tabela de Serviços", "📊")

# Load data
df = DataLoader().load_data()

# Page title
st.title("Tabela de Serviços")
col1, col2 = st.columns(2)

# Create an instance of DateFilter with df and the date column name
date_filter = DateFilter(df, "DATA")

# Filter the DataFrame by the selected date range
df = date_filter.filter_by_date()

# Barra de busca
search_term = st.text_input("Buscar por cliente ou técnico")
with col1:
# Filtros
    selected_status = st.selectbox(
        "Filtrar por status", ["All"] + list(df["STATUS"].unique())
    )
with col2:
    selected_technician = st.selectbox(
        "Filtrar por técnico", ["All"] + list(df["TECNICO"].unique())
    )

# Aplicar filtros
if selected_status != "All":
    df = df[df["STATUS"] == selected_status]
if selected_technician != "All":
    df = df[df["TECNICO"] == selected_technician]

# Aplicar busca
if search_term:
    df = df[(df["CLIENTE"].str.contains(search_term)) | (df["TECNICO"].str.contains(search_term))]

monetary_columns = [
    "(R$)PEÇA",
    "VALOR TOTAL DO SERVIÇO",
    "LUCRO",
    "VALOR DO TÉCNICO",
    "LUCRO FINAL",
]

for col in monetary_columns:
    df[col] = df[col].map(lambda x: f"R$ {x: ,.2f}")

df["DATA"] = df["DATA"].dt.strftime("%d/%m/%Y")

# Display the DataFrame
st.data_editor(df, )

st.markdown("## Exportar dados")
# export to excel
if st.button("Exportar dados"):
    st.write("Exportando dados...")
    df.to_excel("servicos_exportados.xlsx", index=False)
    st.write("Dados exportados com sucesso!")