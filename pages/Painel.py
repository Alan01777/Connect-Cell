import streamlit as st
import pandas as pd
import plotly.express as px

from utils import DataLoader
from utils import DateFilter
from utils import Formatting
from settings import page_settings

def load_data():
    return DataLoader().load_data()


def display_general_info(df):
    st.header("Informações Gerais")
    col1, col2, col3, col4 = st.columns(4)
    col5, col6, col7 = st.columns(3)

    total_requests = len(df.index)
    total_spent = Formatting.format_monetary(df["(R$)PEÇA"].sum())
    service_prices = Formatting.format_monetary(df["VALOR TOTAL DO SERVIÇO"].sum())

    profit_employee = df.groupby("TECNICO")["VALOR DO TÉCNICO"].sum()
    liquid_profit = Formatting.format_monetary(df["LUCRO FINAL"].sum())

    with col1:
        st.metric("Total de serviços", total_requests)
    with col2:
        st.metric("Total gasto com peças", total_spent)
    with col3:
        st.metric("Total recebido", service_prices)
    with col4:
        st.metric("Lucro final", liquid_profit)
    with col5:
        st.metric(
            "Valor Recebido por Tiago",
            Formatting.format_monetary(profit_employee["TIAGO"]),
        )
    with col7:
        if "VALDERI" in profit_employee.index:
            st.metric(
                "Valor Recebido por Valderi",
                Formatting.format_monetary(profit_employee["VALDERI"]),
            )
        else:
            st.write("Nenhum dado disponível para o valor recebido por Valderi.")


def display_profit_trend(df):
    st.header("Tendência do lucro")
    fig = px.line(
        df.set_index("DATA")["LUCRO FINAL"].groupby(pd.Grouper(freq="ME")).sum(),
        markers=True,
        width=1100,
        color_discrete_map={"LUCRO FINAL": "#CD6A13"},
    )
    fig.update_layout(xaxis_title="PERÍODO", yaxis_title="LUCRO (R$)")
    st.plotly_chart(fig)


def display_technician_performance(df):
    st.header("Desempenho dos técnicos")
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
    fig.update_layout(xaxis_title="PERIODO", yaxis_title="VALOR RECEBIDO (R$)")
    fig.update_traces(
        textfont_size=14, textangle=0, textposition="outside", cliponaxis=False
    )
    fig.update_yaxes(tickformat=",.2f")
    st.plotly_chart(fig)


def display_data_distribution(df):
    st.header("Distribuição de dados")
    col1, col2 = st.columns(2)

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
            st.write("Nenhum dado disponível.")

    with col2:
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
            st.write("Nenhum dado disponível.")


def display_avarage_service_price(df):
    st.header("Preço médio dos serviços")
    avg_service_price = (
        df.groupby("TECNICO")["VALOR TOTAL DO SERVIÇO"].mean().reset_index()
    )

    fig = px.bar(
        avg_service_price,
        x="VALOR TOTAL DO SERVIÇO",
        y="TECNICO",
        color="TECNICO",
        color_discrete_map={"TIAGO": "#CD6A13", "VALDERI": "#8C1C13"},
        text="VALOR TOTAL DO SERVIÇO",
        labels={"VALOR TOTAL DO SERVIÇO": "Média Recebida (R$)", "TECNICO": "Técnico"},
        orientation="h",
        width=400,
        height=380,
    )

    fig.update_traces(texttemplate="R$ %{text:.2f}", textposition="inside", width=0.4)

    fig.update_layout(
        showlegend=False,
        xaxis=dict(title="Média Recebida (R$)"),
        yaxis=dict(title="Técnico"),
    )

    st.plotly_chart(fig)


def display_top_clients(df):
    st.header("Top 10 clientes")

    top_clients = df.groupby("CLIENTE").agg(
        {"VALOR TOTAL DO SERVIÇO": "sum", "PRODUTO/SERVIÇO": "count"}
    )

    top_clients.columns = ["Valor Total Gasto", "Número de Serviços"]

    top_clients = top_clients.sort_values("Valor Total Gasto", ascending=False).head(10)

    top_clients["Valor Total Gasto"] = top_clients["Valor Total Gasto"].apply(
        lambda x: f"R$ {x:,.2f}",
    )

    top_clients["Número de Serviços"] = top_clients["Número de Serviços"].astype(int)

    st.table(top_clients)


def main():
    page_settings("Dashboard", "📊")
    st.title("Dados financeiros da empresa")
    st.markdown(
        """
        Os valores abaixo são baseados nos dados financeiros e operacionais fornecidos pela empresa.
    """
    )

    df = load_data()

    date_filter = DateFilter(df, "DATA")
    df = date_filter.filter_by_date()

    display_general_info(df)
    st.markdown(
        """
        As métricas acima mostram dados financeiros gerais, incluindo o número total de serviços, gastos com peças, valor total recebido e lucro final.
    """
    )
    display_profit_trend(df)
    st.markdown(
        """
        O gráfico acima mostra a tendência do lucro ao longo do tempo.
    """
    )
    display_technician_performance(df)
    st.markdown(
        """
        O gráfico acima ilustra o desempenho financeiro dos técnicos ao longo do tempo.
    """
    )
    display_data_distribution(df)
    st.markdown(
        """
        Os gráficos acima mostram a distribuição de dados relacionados às formas de pagamento e status do serviço. Dados ausentes foram ignorados.
    """
    )
    col1, col2 = st.columns(2)
    with col1:
        display_avarage_service_price(df)
        st.markdown(
            """
            O gráfico acima representa a média de preço dos serviços realizados por cada técnico.
        """
        )
    with col2:
        display_top_clients(df)
        st.markdown(
            """
            A tabela acima mostra os 10 principais clientes com base no valor total gasto.
        """
        )


if __name__ == "__main__":
    main()
