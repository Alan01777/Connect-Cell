import streamlit as st
import pandas as pd
import plotly.express as px

from utils import DataLoader
from utils import DateFilter
from utils import Formatting
from settings import page_settings


class Dashboard:
    def __init__(
        self,
    ):
        page_settings("Dashboard", "📊")
        self.df = DataLoader().load_data()

    def display_general_info(self):
        df = self.df
        st.header("Informações Gerais")
        col1, col2, col3, col4 = st.columns(4)
        col5, col6, col7 = st.columns([1, 2, 1])

        profit_employee = df.groupby("TECNICO")["VALOR DO TÉCNICO"].sum()
        category = {
            "REPAROS HARDWARE": df[df["CATEGORIA"] == "REPAROS HARDWARE"],
            "REPAROS SOFTWARE": df[df["CATEGORIA"] == "REPAROS SOFTWARE"],
            "VENDAS DISPOSITIVOS": df[df["CATEGORIA"] == "VENDAS DISPOSITIVOS"],
            "VENDAS HARDWARE": df[df["CATEGORIA"] == "VENDAS HARDWARE"],
            "VENDAS ACESSÓRIOS": df[df["CATEGORIA"] == "VENDAS ACESSÓRIOS"],
            "OUTROS": df[df["CATEGORIA"] == "OUTROS"],
        }

        with col1:
            st.metric("Total de serviços", len(df.index))
        with col2:
            st.metric("Despesas", Formatting.format_monetary(df["(R$)PEÇA"].sum()))
        with col3:
            st.metric(
                "Faturamento",
                Formatting.format_monetary(df["VALOR TOTAL DO SERVIÇO"].sum()),
            )
        with col4:
            st.metric("Lucro", Formatting.format_monetary(df["LUCRO LIQUIDO"].sum()))
        with col5:
            st.metric(
                "Valor Recebido por Tiago",
                Formatting.format_monetary(profit_employee.get("TIAGO", 0)),
            )
        with col6:
            st.write(" ")
        with col7:
            st.metric(
                "Valor Recebido por Valderi",
                Formatting.format_monetary(profit_employee.get("VALDERI", 0)),
            )
        st.markdown(
            """
            As métricas acima mostram dados financeiros gerais, incluindo o número total de serviços, gastos com peças, valor total recebido e LUCRO LIQUIDO.
        """
        )
        with st.expander("Detalhes por categoria"):
            col1, col2, col3, col4, col5, col6 = st.columns(6)
            for col, cat in zip([col1, col2, col3, col4, col5, col6], category.keys()):
                with col:
                    st.metric(
                        cat.title().replace("_", " "),
                        len(category[cat].index),
                    )
                    st.write(
                        Formatting.format_monetary(
                            category[cat]["VALOR TOTAL DO SERVIÇO"].sum()
                        )
                    )
            st.markdown(
                """
                    Os valores acima representam o número total de serviços e o valor total recebido para cada categoria de serviço.
                """
            )

    def display_profit_trend(self):
        df = self.df
        st.header("Tendência do lucro")

        df = df.rename(
            columns={
                "(R$)PEÇA": "Despesas",
                "VALOR TOTAL DO SERVIÇO": "Faturamento",
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
        df_melt = df_melt.groupby([pd.Grouper(freq="M"), "Tipo"]).sum().reset_index()

        fig = px.line(
            df_melt,
            x="DATA",
            y="Valor",
            color="Tipo",
            markers=True,
            width=1100,
            color_discrete_map={
                "Despesas": "#8C1C13",
                "Faturamento": "#CD6A13",
                "Lucro": "#00CD6A",
            },
        )
        fig.update_layout(xaxis_title="PERÍODO DE TEMPO", yaxis_title="VALOR (R$)")
        st.plotly_chart(fig)

    def display_category_performance(self):
        df = self.df
        st.header("Faturamento por categoria")
        df_melt = df.melt(
            id_vars=["DATA", "CATEGORIA"], value_vars=["VALOR TOTAL DO SERVIÇO"]
        )
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
            width=1100,
            color_discrete_map={
                "REPAROS HARDWARE": "#8C1C13",
                "REPAROS SOFTWARE": "#CD6A13",
                "VENDAS DISPOSITIVOS": "#00CD6A",
                "VENDAS HARDWARE": "#4B0282",
                "VENDAS ACESSÓRIOS": "#FFD700",
                "OUTROS": "#8A2BE2",
            },
        )
        fig.update_layout(xaxis_title="PERÍODO DE TEMPO", yaxis_title="VALOR (R$)")
        st.plotly_chart(fig)

    def display_category_expenses(self):
        df = self.df
        st.header("Despesas por categoria")
        df_melt = df.melt(id_vars=["DATA", "CATEGORIA"], value_vars=["(R$)PEÇA"])
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
            width=1100,
            color_discrete_map={
                "REPAROS HARDWARE": "#8C1C13",
                "REPAROS SOFTWARE": "#CD6A13",
                "VENDAS DISPOSITIVOS": "#00CD6A",
                "VENDAS HARDWARE": "#4B0282",
                "VENDAS ACESSÓRIOS": "#FFD700",
                "OUTROS": "#8A2BE2",
            },
        )
        fig.update_layout(xaxis_title="PERÍODO DE TEMPO", yaxis_title="VALOR (R$)")
        st.plotly_chart(fig)

    def display_technician_performance(self):
        df = self.df
        st.header("Desempenho dos técnicos")
        df_melt = df.melt(id_vars=["DATA", "TECNICO"], value_vars=["VALOR DO TÉCNICO"])
        df_melt["DATA"] = pd.to_datetime(df_melt["DATA"])
        df_melt = df.melt(id_vars=["DATA", "TECNICO"], value_vars=["VALOR DO TÉCNICO"])
        df_melt["DATA"] = pd.to_datetime(df_melt["DATA"])
        df_melt.set_index("DATA", inplace=True)
        df_melt = df_melt.groupby([pd.Grouper(freq="M"), "TECNICO"]).sum().reset_index()

        df_melt.set_index(["DATA", "TECNICO"], inplace=True)
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
            width=1100,
            color_discrete_map={"TIAGO": "#CD6A13", "VALDERI": "#8C1C13"},
        )
        fig.update_layout(xaxis_title="PERÍODO DE TEMPO", yaxis_title="VALOR (R$)")
        st.plotly_chart(fig)

    def display_data_distribution(self):
        df = self.df
        st.header("Distribuição de dados")
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Formas de pagamento")
            df_filtered = df.dropna(subset=["F/PAGAMENTO"])
            if not df_filtered.empty:
                fig = px.histogram(
                    df_filtered,
                    x="F/PAGAMENTO",
                    histnorm="percent",
                    width=400,
                    nbins=len(df_filtered["F/PAGAMENTO"].unique()),
                    color_discrete_sequence=["#CD6A13"],
                )
                fig.update_layout(
                    xaxis_title="Formas de pagamento", yaxis_title="Porcentagem (%)"
                )
                st.plotly_chart(fig)
            else:
                st.write("Nenhum dado disponível.")

        with col2:
            st.subheader("Status de serviço")
            df_filtered = df.dropna(subset=["STATUS"])
            if not df_filtered.empty:
                fig = px.histogram(
                    df_filtered,
                    x="STATUS",
                    width=400,
                    histnorm="percent",
                    nbins=len(df_filtered["STATUS"].unique()),
                    color_discrete_sequence=["#8C1C13"],
                )
                fig.update_layout(
                    xaxis_title="Status de serviço", yaxis_title="Porcentagem (%)"
                )
                st.plotly_chart(fig)
            else:
                st.write("Nenhum dado disponível.")

    def display_avarage_service_price(self):
        df = self.df
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
            labels={
                "VALOR TOTAL DO SERVIÇO": "Média Recebida (R$)",
                "TECNICO": "Técnico",
            },
            orientation="h",
            width=400,
            height=380,
        )

        fig.update_traces(
            texttemplate="R$ %{text:.2f}", textposition="inside", width=0.4
        )

        fig.update_layout(
            showlegend=False,
            xaxis=dict(title="Média Recebida (R$)"),
            yaxis=dict(title="Técnico"),
        )

        st.plotly_chart(fig)

    def display_top_clients(self):
        df = self.df
        st.header("Top 10 clientes")

        top_clients = df.groupby("CLIENTE").agg(
            {"VALOR TOTAL DO SERVIÇO": "sum", "PRODUTO/SERVIÇO": "count"}
        )

        top_clients.columns = ["Valor Total Gasto", "Número de Serviços"]

        top_clients = top_clients.sort_values(
            "Valor Total Gasto", ascending=False
        ).head(10)

        top_clients["Valor Total Gasto"] = top_clients["Valor Total Gasto"].apply(
            lambda x: f"R$ {x:,.2f}",
        )

        top_clients["Número de Serviços"] = top_clients["Número de Serviços"].astype(
            int
        )

        st.table(top_clients)

    def main(self):
        st.title("Dados financeiros da empresa")
        st.markdown(
            """
            Os valores abaixo são baseados nos dados financeiros e operacionais fornecidos pela empresa.
        """
        )

        df = self.df

        date_filter = DateFilter(df, "DATA")
        df = date_filter.filter_by_date()

        self.display_general_info()
        self.display_profit_trend()
        st.markdown(
            """
            O gráfico acima mostra a tendência do faturamento, das despesas e do lucro ao longo do tempo.
        """
        )
        self.display_category_performance()
        st.markdown(
            """
            O gráfico acima mostra o desempenho financeiro das categorias de serviço ao longo do tempo.
        """
        )
        self.display_category_expenses()
        st.markdown(
            """
            O gráfico acima mostra as despesas por categoria ao longo do tempo.
        """
        )
        self.display_technician_performance()
        st.markdown(
            """
            O gráfico acima ilustra o desempenho financeiro dos técnicos ao longo do tempo.
        """
        )
        self.display_data_distribution()
        st.markdown(
            """
            Os gráficos acima mostram a distribuição de dados relacionados às formas de pagamento e status do serviço. Dados ausentes foram ignorados.
        """
        )
        col1, col2 = st.columns(2)
        with col1:
            self.display_avarage_service_price()
            st.markdown(
                """
                O gráfico acima representa a média de preço dos serviços realizados por cada técnico.
            """
            )
        with col2:
            self.display_top_clients()
            st.markdown(
                """
                A tabela acima mostra os 10 principais clientes com base no valor total gasto.
            """
            )


if __name__ == "__main__":
    dashboard = Dashboard()
    dashboard.main()
