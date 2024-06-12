import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from utils import DataLoader
from utils import DateFilter
from utils import Formatting
from settings import page_settings


class Dashboard:
    def __init__(self):
        page_settings("Dashboard", "📊")
        self.df = DataLoader().load_data()
        self.colors = {
            "blue": "#1f77b4",
            "red": "#d62728",
            "green": "#2ca02c",
            "purple": "#9467bd",
            "orange": "#ff7f0e",
            "yellow": "#ffbb78",
        }

    def display_general_info(self, data):
        with st.container(border=True, height=650):
            df = data

            st.header("Informações Gerais")

            with st.container(border=True):
                st.metric(
                    "Total de serviços",
                    len(df.index),
                )

            with st.container(border=True):
                st.metric("Despesas", Formatting.format_monetary(df["DESPESAS"].sum()))

            with st.container(border=True):
                st.metric(
                    "Faturamento",
                    Formatting.format_monetary(df["FATURAMENTO"].sum()),
                )

            with st.container(border=True):
                st.metric(
                    "Lucro", Formatting.format_monetary(df["LUCRO LIQUIDO"].sum())
                )

            st.caption(
                """
                        As métricas acima mostram dados financeiros gerais, incluindo o número total de serviços, gastos com peças, valor total recebido e LUCRO LIQUIDO.
                    """
            )

    def details_by_category(self, data):
        with st.container(border=True, height=1242):
            st.header("Detalhes por categoria")
            df = data
            category = {
                "Reparos de Hardware": df[df["CATEGORIA"] == "REPAROS HARDWARE"],
                "Reparos de Software": df[df["CATEGORIA"] == "REPAROS SOFTWARE"],
                "Vendas de Dispositivos": df[df["CATEGORIA"] == "VENDAS DISPOSITIVOS"],
                "Vendas de Hardware": df[df["CATEGORIA"] == "VENDAS HARDWARE"],
                "Vendas de Acessórios": df[df["CATEGORIA"] == "VENDAS ACESSÓRIOS"],
                "Outros": df[df["CATEGORIA"] == "OUTROS"],
            }

            for name, data in category.items():
                with st.container(border=True):
                    st.subheader(name)
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric(
                            "Número de serviços",
                            len(data.index),
                        )
                    with col2:
                        st.metric(
                            "Lucro Final",
                            Formatting.format_monetary(data["LUCRO LIQUIDO"].sum()),
                        )
            st.caption(
                """
                Os gráficos acima mostram o número total de serviços e o valor total arrecadado para cada categoria de serviço.
            """
            )

    def details_by_technician(self, data):
        with st.container(border=True, height=600):
            st.subheader("Detalhes por técnico")
            df = data
            technicians = {
                "TIAGO": df[df["TECNICO"] == "TIAGO"],
                "VALDERI": df[df["TECNICO"] == "VALDERI"],
                # Add more technicians here if needed
            }

            for name, data in technicians.items():
                with st.container(border=True):
                    st.write(name)
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric(
                            "Número de Serviços",
                            len(data.index),
                        )
                    with col2:
                        st.metric(
                            "Receita Acumulada",
                            Formatting.format_monetary(data["VALOR DO TÉCNICO"].sum()),
                        )
            st.caption(
                "O Painel acima mostra um resumo do número total de serviços e a receita acumulada por cada técnico."
            )

    def display_profit_trend(self, data):
        col1, col2 = st.columns([4, 2], gap="small")

        with col1:
            with st.container(border=True, height=650):
                df = data
                st.header("Tendência do Faturamento/Despesas")

                df = df.rename(
                    columns={
                        "DESPESAS": "Despesas",
                        "FATURAMENTO": "Faturamento",
                        "LUCRO LIQUIDO": "Lucro",
                    }
                )

                df_melt = df.melt(
                    id_vars=["DATA"],
                    value_vars=["Despesas", "Faturamento", "Lucro"],
                    var_name="Tipo",
                    value_name="Valor",
                )

                df_melt["DATA"] = pd.to_datetime(df_melt["DATA"])
                df_melt.set_index("DATA", inplace=True)
                df_melt = (
                    df_melt.groupby([pd.Grouper(freq="M"), "Tipo"]).sum().reset_index()
                )

                fig = px.line(
                    df_melt,
                    x="DATA",
                    y="Valor",
                    color="Tipo",
                    markers=True,
                    # width=1100,
                    color_discrete_map={
                        "Despesas": self.colors["red"],
                        "Faturamento": self.colors["green"],
                        "Lucro": self.colors["blue"],
                    },
                )
                fig.update_layout(
                    xaxis_title="PERÍODO DE TEMPO", yaxis_title="VALOR (R$)"
                )
                st.plotly_chart(fig)
                st.caption(
                    """
            O gráfico acima mostra a tendência do faturamento, das despesas e do lucro ao longo do tempo.
        """
                )
        with col2:
            self.display_general_info(data)

    def display_category_performance(self, data):
        df = data
        st.header("Faturamento por categoria")
        df_melt = df.melt(id_vars=["DATA", "CATEGORIA"], value_vars=["FATURAMENTO"])
        df_melt["DATA"] = pd.to_datetime(df_melt["DATA"])
        df_melt.set_index("DATA", inplace=True)
        df_melt = (
            df_melt.groupby([pd.Grouper(freq="M"), "CATEGORIA"]).sum().reset_index()
        )

        df_melt.set_index(["DATA", "CATEGORIA"], inplace=True)
        df_melt = df_melt.reindex(
            pd.MultiIndex.from_product(
                [
                    pd.date_range(
                        start=df_melt.index.get_level_values("DATA").min(),
                        end=df_melt.index.get_level_values("DATA").max(),
                        freq="M",
                    ),
                    df_melt.index.get_level_values("CATEGORIA").unique(),
                ],
                names=["DATA", "CATEGORIA"],
            ),
            fill_value=0,
        ).reset_index()

        fig = px.line(
            df_melt,
            x="DATA",
            y="value",
            # text="value",
            color="CATEGORIA",
            markers=True,
            # width=122,
            color_discrete_map={
                "REPAROS HARDWARE": self.colors["blue"],
                "REPAROS SOFTWARE": self.colors["purple"],
                "VENDAS DISPOSITIVOS": self.colors["green"],
                "VENDAS HARDWARE": self.colors["yellow"],
                "VENDAS ACESSÓRIOS": self.colors["orange"],
                "OUTROS": self.colors["red"],
            },
        )
        fig.update_traces(textposition="top right", texttemplate="R$ %{y:.2f}")
        fig.update_layout(xaxis_title="PERÍODO DE TEMPO", yaxis_title="VALOR (R$)")
        st.plotly_chart(fig)
        st.caption(
            """
                    O gráfico acima mostra o desempenho financeiro das categorias de serviço ao longo do tempo. 
                """
        )

    def display_category_expenses(self, data):
        df = data
        st.header("Despesas por categoria")
        df_melt = df.melt(id_vars=["DATA", "CATEGORIA"], value_vars=["DESPESAS"])
        df_melt["DATA"] = pd.to_datetime(df_melt["DATA"])
        df_melt.set_index("DATA", inplace=True)
        df_melt = (
            df_melt.groupby([pd.Grouper(freq="M"), "CATEGORIA"]).sum().reset_index()
        )

        df_melt.set_index(["DATA", "CATEGORIA"], inplace=True)

        df_melt = df_melt.reindex(
            pd.MultiIndex.from_product(
                [
                    pd.date_range(
                        start=df_melt.index.get_level_values("DATA").min(),
                        end=df_melt.index.get_level_values("DATA").max(),
                        freq="M",
                    ),
                    df_melt.index.get_level_values("CATEGORIA").unique(),
                ],
                names=["DATA", "CATEGORIA"],
            ),
            fill_value=0,
        ).reset_index()

        fig = px.line(
            df_melt,
            x="DATA",
            y="value",
            color="CATEGORIA",
            markers=True,
            # width=1100,
            color_discrete_map={
                "REPAROS HARDWARE": self.colors["blue"],
                "REPAROS SOFTWARE": self.colors["purple"],
                "VENDAS DISPOSITIVOS": self.colors["green"],
                "VENDAS HARDWARE": self.colors["yellow"],
                "VENDAS ACESSÓRIOS": self.colors["orange"],
                "OUTROS": self.colors["red"],
            },
        )
        fig.update_layout(xaxis_title="PERÍODO DE TEMPO", yaxis_title="VALOR (R$)")
        st.plotly_chart(fig)
        st.caption(
            """
                    O gráfico acima mostra as despesas por categoria ao longo do tempo.
                """
        )

    def display_technician_performance(self, data):
        col1, col2 = st.columns([4, 2], gap="small")
        df = data
        with col1:
            with st.container(border=True):
                st.header("Receitas Mensais dos Técnicos")
                df_melt = df.melt(
                    id_vars=["DATA", "TECNICO"], value_vars=["VALOR DO TÉCNICO"]
                )
                df_melt["DATA"] = pd.to_datetime(df_melt["DATA"])
                df_melt = df.melt(
                    id_vars=["DATA", "TECNICO"], value_vars=["VALOR DO TÉCNICO"]
                )
                df_melt["DATA"] = pd.to_datetime(df_melt["DATA"])
                df_melt.set_index("DATA", inplace=True)
                df_melt = (
                    df_melt.groupby([pd.Grouper(freq="M"), "TECNICO"])
                    .sum()
                    .reset_index()
                )

                df_melt.set_index(["DATA", "TECNICO"], inplace=True)
                df_melt = df_melt
                df_melt = df_melt.reindex(
                    pd.MultiIndex.from_product(
                        [
                            pd.date_range(
                                start=df_melt.index.get_level_values("DATA").min(),
                                end=df_melt.index.get_level_values("DATA").max(),
                                freq="M",
                            ),
                            df_melt.index.get_level_values("TECNICO").unique(),
                        ],
                        names=["DATA", "TECNICO"],
                    ),
                    fill_value=0,
                ).reset_index()

                fig = px.line(
                    df_melt,
                    x="DATA",
                    y="value",
                    color="TECNICO",
                    markers=True,
                    # width=1100,
                    color_discrete_map={
                        "TIAGO": self.colors["blue"],
                        "VALDERI": self.colors["red"],
                    },
                )
                fig.update_layout(
                    xaxis_title="PERÍODO DE TEMPO", yaxis_title="VALOR (R$)"
                )
                st.plotly_chart(fig)
                st.caption(
                    """
                    Este gráfico mostra a receita mensal de cada técnico ao longo do tempo. As linhas representam a receita mensal de cada técnico.
                    """
                )
        with col2:
            self.details_by_technician(data)

    def display_data_distribution(self, data):
        df = data
        col1, col2 = st.columns(2)

        with col1:
            with st.container(border=True):
                st.header("Formas de pagamento")
                df_filtered = df.dropna(subset=["F/PAGAMENTO"])
                if not df_filtered.empty:
                    fig = px.histogram(
                        df_filtered,
                        x="F/PAGAMENTO",
                        histnorm="percent",
                        text_auto=".1f",
                        # width=400,
                        nbins=len(df_filtered["F/PAGAMENTO"].unique()),
                        color_discrete_sequence=[self.colors["blue"]],
                    )
                    fig.update_layout(
                        xaxis_title="Formas de pagamento",
                        yaxis_title="Porcentagem (%)",
                        font=dict(
                            size=18,  # Set the font size here
                            color="black",
                        ),
                    )
                    st.plotly_chart(fig)
                else:
                    st.write("Nenhum dado disponível.")
                st.caption(
                    "O gráfico acima mostra a distribuição de dados relacionados às formas de pagamento. Dados ausentes foram ignorados."
                )

        with col2:
            with st.container(border=True):
                st.header("Status de serviço")
                df_filtered = df.dropna(subset=["STATUS"])
                if not df_filtered.empty:
                    fig = px.histogram(
                        df_filtered,
                        y="STATUS",
                        # width=400,
                        text_auto=".1f",
                        orientation="h",
                        histnorm="percent",
                        nbins=len(df_filtered["STATUS"].unique()),
                        color_discrete_sequence=[self.colors["blue"]],
                    )
                    fig.update_layout(
                        xaxis_title="Porcentagem (%)",
                        yaxis_title="Status de serviço",
                        font=dict(
                            size=18,  # Set the font size here
                            color="black",
                        ),
                    )
                    st.plotly_chart(fig)
                else:
                    st.write("Nenhum dado disponível.")
                st.caption(
                    "O gráfico acima mostra a distribuição de dados relacionados aos statuss dos serviços. Dados ausentes foram ignorados."
                )

    def display_service_distribution(self, data):
        with st.container(border=True, height=605):
            df = data
            st.header("Distribuição de serviços")
            df_filtered = df.dropna(subset=["PRODUTO/SERVIÇO"])
            df_filtered = df_filtered.groupby("TECNICO").agg(
                {"PRODUTO/SERVIÇO": "count"}
            )

            if not df_filtered.empty:
                fig = px.pie(
                    df_filtered,
                    values="PRODUTO/SERVIÇO",
                    names=df_filtered.index,
                    color_discrete_map={
                        "TIAGO": self.colors["blue"],
                        "VALDERI": self.colors["red"],
                    },
                    hole=0.4,
                )
                fig.update_traces(textposition="inside", textinfo="percent", textfont_size=18)
                st.plotly_chart(fig)
            else:
                st.write("Nenhum dado disponível.")
            st.caption(
                """
                O gráfico acima mostra a distribuição de serviços entre os técnicos. 
            """
            )

    def display_top_clients(self, data):
        with st.container(border=True):
            df = data
            st.header("Top 10 clientes")

            top_clients = df.groupby("CLIENTE").agg(
                {"FATURAMENTO": "sum", "PRODUTO/SERVIÇO": "count"}
            )

            top_clients.columns = ["Valor Total Gasto", "Número de Serviços"]

            top_clients = top_clients.sort_values(
                "Valor Total Gasto", ascending=False
            ).head(10)

            top_clients["Valor Total Gasto"] = top_clients["Valor Total Gasto"].apply(
                lambda x: f"R$ {x:,.2f}",
            )

            top_clients["Número de Serviços"] = top_clients[
                "Número de Serviços"
            ].astype(int)

            st.table(top_clients)
            st.write("")
            st.write("")
            st.write("")
            st.write("")
            st.caption(
                """
                A tabela acima mostra os 10 principais clientes com base no valor total gasto.
            """
            )

    def main(self):
        st.title("Dados financeiros da empresa")
        st.write(
            """
            Os gráficos abaixo são baseados nos dados financeiros e operacionais fornecidos pela empresa.
        """
        )

        df = self.df

        date_filter = DateFilter(df, "DATA")
        df = date_filter.filter_by_date()

        self.display_profit_trend(df)

        st.caption("---")

        col1, col2 = st.columns([4, 2], gap="small")
        with col1:
            with st.container(border=True):
                self.display_category_performance(df)

                st.markdown("---")
                self.display_category_expenses(df)

        with col2:
            self.details_by_category(df)

        st.caption("---")

        self.display_technician_performance(df)

        st.caption("---")

        self.display_data_distribution(df)

        st.caption("---")

        col1, col2 = st.columns(2)
        with col1:
            self.display_service_distribution(df)

        with col2:
            self.display_top_clients(df)


if __name__ == "__main__":
    dashboard = Dashboard()
    dashboard.main()
