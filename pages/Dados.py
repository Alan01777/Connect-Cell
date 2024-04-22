import streamlit as st
import pandas as pd
import plotly.express as px

from utils import DataLoader
from settings import page_settings
from utils import DateFilter

page_settings("Dashboard", "📊")

st.title("Dados financeiros da empresa")

df = DataLoader().load_data()

# Create an instance of DateFilter with df and the date column name
date_filter = DateFilter(df, "DATA")

# Filter the DataFrame by the selected date range
df = date_filter.filter_by_date()

# DADOS GERAIS

st.header("Informações Gerais")
col1, col2, col3, col4 = st.columns(4)
col5, col6, col7 = st.columns(3)

total_requests = len(df.index)
total_spent = df["(R$)PEÇA"].sum()
service_prices = df["VALOR TOTAL DO SERVIÇO"].sum()

profit_emploee = df.groupby("TECNICO")["VALOR DO TÉCNICO"].sum()
liquid_profit = df["LUCRO FINAL"].sum()

with col1:
    st.metric("Total de pedidos", total_requests)
with col2:
    st.metric("Total gasto com peças", f"R$ {total_spent: .2f}")
with col3:
    st.metric("Total recebido", f"R$ {service_prices: .2f}")
with col4:
    st.metric("Lucro final", f"R$ {liquid_profit: .2f}")
with col5:
    st.metric("Valor Recebido por Tiago", f"R$ {profit_emploee['TIAGO']: .2f}")
with col6:
    st.write("")
with col7:
    st.metric("Valor Recebido por Valderi", f"R$ {profit_emploee['VALDERI']: .2f}")
    
st.markdown(
    """
    **OBS:** Os valores acima representam informações gerais sobre os dados financeiros da empresa.
    """
)


# TENDÊNCIA DO LUCRO AO LONGO DO TEMPO
st.header("Tendência do lucro ao longo do tempo")
fig = px.line(
    df.set_index("DATA")["LUCRO FINAL"].groupby(pd.Grouper(freq="ME")).sum(),
    markers=True,
    width=1100,
    color_discrete_map={"LUCRO FINAL": "#CD6A13"},
)
fig.update_layout(xaxis_title="PERÍODO DE TEMPO", yaxis_title="LUCRO (R$)")
st.plotly_chart(fig)

st.markdown(
    """
    **OBS:** O gráfico acima representa a tendência do lucro final obtido pela empresa ao longo do tempo.
    """
)

# DESEMPENHO FINANCEIRO POR TÉCNICO
st.header("Desempenho financeiro por técnico")
fig = px.histogram(
    df.groupby([pd.Grouper(key="DATA", freq="ME"), "TECNICO"])["VALOR DO TÉCNICO"]
    .sum()
    .reset_index(),
    y="VALOR DO TÉCNICO",
    x="DATA",
    color="TECNICO",
    barmode="group",
    text_auto=True,
    width=1100,
    color_discrete_map={"TIAGO": "#CD6A13", "VALDERI": "#8C1C13"},
)
fig.update_layout(xaxis_title="PERIODO DE TEMPO", yaxis_title="VALOR RECEBIDO (R$)")
fig.update_traces(
    textfont_size=14,
    textangle=0,
    textposition="outside",
    cliponaxis=False,
)
fig.update_yaxes(tickformat=",.2f")
st.plotly_chart(fig)

st.markdown(
    """
    **OBS:** Os gráficos acima representam o lucro final obtido pela empresa e o desempenho financeiro dos técnicos Tiago e Valderi ao longo do tempo.
    """
)


st.header("Distribuição de dados")
col1, col2 = st.columns(2)
# METODOS DE PAGAMENTO
with col1:
    st.subheader("Formas de pagamento")
    df_filtered = df.dropna(subset=["F/PAGAMENTO"])
    if not df_filtered.empty:
        fig = px.pie(
            df_filtered,
            names="F/PAGAMENTO",
            width=400,
            color_discrete_sequence=["#10D2F9", "#152566", "#CD6A13", "#8C1C13"],
            hole=0.4,
        )
        fig.update_traces(
            textinfo="percent",
            hoverinfo="percent",
            text=df_filtered["F/PAGAMENTO"].unique(),
        )
        st.plotly_chart(fig)
    else:
        st.write("Nenhum dado disponível para a distribuição das formas de pagamento.")

with col2:
    # STATUS DOS PEDIDOS
    st.subheader("Status de serviço")
    df_filtered = df.dropna(subset=["STATUS"])
    if not df_filtered.empty:
        fig = px.pie(
            df_filtered,
            names="STATUS",
            width=400,
            color_discrete_sequence=["#10D2F9", "#152566", "#CD6A13", "#8C1C13"],
            hole=0.4,
        )
        fig.update_traces(
            textinfo="percent",
            hoverinfo="percent",
            text=df_filtered["F/PAGAMENTO"].unique(),
        )
        st.plotly_chart(fig)
    else:
        st.write("Nenhum dado disponível para a distribuição dos status de serviço.")
        
st.markdown(
    """
    **OBS:** Dados em estado como N/A ou null não foram levados em consideração para os gráficos de distribuição de dados.
    """
)