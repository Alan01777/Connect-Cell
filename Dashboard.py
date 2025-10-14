"""
Dashboard Financeiro e Operacional - Connect-Cell
Versão Refatorada e Otimizada
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Imports locais
from utils import (
    DataLoader, DateFilter, Formatting,
    ThemeManager, MetricCard, ChartContainer, InsightBox,
    KPIRow, ExportButton, DataAnalyzer, InsightGenerator, MetricsCalculator
)
from settings import page_settings
from config import COLORS, CHART_CONFIG, CATEGORY_DISPLAY_NAMES


class DashboardV2:
    """Dashboard refatorado com melhorias de performance e UX"""

    def __init__(self):
        """Inicializa o dashboard"""
        page_settings("Dashboard", "📊")
        ThemeManager.inject_custom_css()

        # Carregar dados com loading state
        with st.spinner("📊 Carregando dados..."):
            self.df = DataLoader().load_data()

        if self.df.empty:
            st.error("❌ Não foi possível carregar os dados. Verifique a conexão com o Google Sheets.")
            st.stop()

    def render_header(self):
        """Renderiza cabeçalho do dashboard"""
        st.markdown("\n")
        col1, col2, col3 = st.columns([3, 1, 1])

        with col1:
            st.title("📊 Dashboard Financeiro e Operacional")
            st.markdown("*Análise em tempo real dos dados da Connect-Cell*")

        with col2:
            if st.button("🔄 Atualizar Dados", use_container_width=True):
                DataLoader.clear_cache()
                st.rerun()

        with col3:
            ExportButton.render_csv_download(
                self.df,
                f"connect_cell_data_{datetime.now().strftime('%Y%m%d')}.csv"
            )

    def render_insights_panel(self, filtered_df: pd.DataFrame):
        """Renderiza painel de insights automáticos"""
        st.subheader("💡 Insights Automáticos")

        financial_insights = InsightGenerator.generate_financial_insights(filtered_df)
        operational_insights = InsightGenerator.generate_operational_insights(filtered_df)

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**📈 Insights Financeiros**")
            for insight in financial_insights:
                InsightBox.render_info(insight)

        with col2:
            st.markdown("**⚙️ Insights Operacionais**")
            for insight in operational_insights:
                InsightBox.render_info(insight)

    def render_kpi_row(self, df: pd.DataFrame):
        """Renderiza linha de KPIs principais"""
        kpis = MetricsCalculator.calculate_kpis(df)
        comparison = DataAnalyzer.calculate_period_comparison(df, value_column="FATURAMENTO")

        # Formatar delta
        delta_revenue = f"{comparison['variation']:+.1f}% vs mês anterior"

        kpi_data = [
            {
                "label": "Faturamento Total",
                "value": Formatting.format_monetary(kpis['total_revenue']),
                "delta": delta_revenue,
                "icon": "💰"
            },
            {
                "label": "Lucro Líquido",
                "value": Formatting.format_monetary(kpis['total_profit']),
                "delta": f"{kpis['profit_margin']:.1f}% margem",
                "icon": "📊"
            },
            {
                "label": "Total de Serviços",
                "value": f"{kpis['total_services']:,}",
                "delta": f"Ticket médio: {Formatting.format_monetary(kpis['avg_ticket'])}",
                "icon": "🔧"
            },
            {
                "label": "Despesas",
                "value": Formatting.format_monetary(kpis['total_expenses']),
                "delta": None,
                "icon": "💸"
            },
        ]

        KPIRow.render(kpi_data)

    def render_financial_trend_chart(self, df: pd.DataFrame):
        """Renderiza gráfico de tendência financeira"""
        df_copy = df.copy()
        df_copy["DATA"] = pd.to_datetime(df_copy["DATA"], format="%d/%m/%Y", errors='coerce')

        df_renamed = df_copy.rename(columns={
            "DESPESAS": "Despesas",
            "FATURAMENTO": "Faturamento",
            "LUCRO LIQUIDO": "Lucro"
        })

        df_melt = df_renamed.melt(
            id_vars=["DATA"],
            value_vars=["Despesas", "Faturamento", "Lucro"],
            var_name="Tipo",
            value_name="Valor"
        )

        df_melt.set_index("DATA", inplace=True)
        df_monthly = df_melt.groupby([pd.Grouper(freq="M"), "Tipo"]).sum().reset_index()

        fig = px.line(
            df_monthly,
            x="DATA",
            y="Valor",
            color="Tipo",
            markers=True,
            color_discrete_map={
                "Despesas": COLORS.red,
                "Faturamento": COLORS.green,
                "Lucro": COLORS.blue,
            },
        )

        fig.update_layout(
            xaxis_title="Período",
            yaxis_title="Valor (R$)",
            hovermode="x unified",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            autosize=True,
            height=CHART_CONFIG.default_height,
            margin=dict(l=0, r=0, t=30, b=0)
        )

        fig.update_traces(
            hovertemplate="<b>%{fullData.name}</b><br>R$ %{y:,.2f}<extra></extra>"
        )

        st.plotly_chart(fig, use_container_width=True)

    def render_category_performance(self, df: pd.DataFrame):
        """Renderiza análise de performance por categoria"""
        df_copy = df.copy()
        df_copy["DATA"] = pd.to_datetime(df_copy["DATA"], format="%d/%m/%Y", errors='coerce')

        df_melt = df_copy.melt(
            id_vars=["DATA", "CATEGORIA"],
            value_vars=["FATURAMENTO"]
        )

        df_melt.set_index("DATA", inplace=True)
        df_monthly = df_melt.groupby([pd.Grouper(freq="M"), "CATEGORIA"]).sum().reset_index()

        # Preencher valores ausentes
        df_monthly.set_index(["DATA", "CATEGORIA"], inplace=True)
        df_monthly = df_monthly.reindex(
            pd.MultiIndex.from_product(
                [
                    pd.date_range(
                        start=df_monthly.index.get_level_values("DATA").min(),
                        end=df_monthly.index.get_level_values("DATA").max(),
                        freq="M"
                    ),
                    df_monthly.index.get_level_values("CATEGORIA").unique(),
                ],
                names=["DATA", "CATEGORIA"]
            ),
            fill_value=0
        ).reset_index()

        fig = px.line(
            df_monthly,
            x="DATA",
            y="value",
            color="CATEGORIA",
            markers=True,
            color_discrete_map=COLORS.category_colors
        )

        fig.update_layout(
            xaxis_title="Período",
            yaxis_title="Faturamento (R$)",
            hovermode="x unified",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            autosize=True,
            height=CHART_CONFIG.default_height,
            margin=dict(l=0, r=0, t=30, b=0)
        )

        fig.update_traces(
            hovertemplate="<b>%{fullData.name}</b><br>R$ %{y:,.2f}<extra></extra>"
        )

        st.plotly_chart(fig, use_container_width=True)

    def render_category_details(self, df: pd.DataFrame):
        """Renderiza detalhes por categoria"""
        st.subheader("Detalhes por Categoria")

        categories = df["CATEGORIA"].unique()

        for category in categories:
            category_data = df[df["CATEGORIA"] == category]

            with st.expander(
                f"📦 {CATEGORY_DISPLAY_NAMES.get(category, category)} "
                f"({len(category_data)} serviços)",
                expanded=False
            ):
                col1, col2, col3 = st.columns(3)

                with col1:
                    MetricCard.render(
                        "Faturamento",
                        Formatting.format_monetary(category_data["FATURAMENTO"].sum())
                    )

                with col2:
                    MetricCard.render(
                        "Lucro Líquido",
                        Formatting.format_monetary(category_data["LUCRO LIQUIDO"].sum())
                    )

                with col3:
                    MetricCard.render(
                        "Ticket Médio",
                        Formatting.format_monetary(category_data["FATURAMENTO"].mean())
                    )

    def render_technician_performance(self, df: pd.DataFrame):
        """Renderiza análise de performance por técnico"""
        df_copy = df.copy()
        df_copy["DATA"] = pd.to_datetime(df_copy["DATA"], format="%d/%m/%Y", errors='coerce')

        df_melt = df_copy.melt(
            id_vars=["DATA", "TECNICO"],
            value_vars=["VALOR DO TÉCNICO"]
        )

        df_melt.set_index("DATA", inplace=True)
        df_monthly = df_melt.groupby([pd.Grouper(freq="M"), "TECNICO"]).sum().reset_index()

        # Preencher valores ausentes
        df_monthly.set_index(["DATA", "TECNICO"], inplace=True)
        df_monthly = df_monthly.reindex(
            pd.MultiIndex.from_product(
                [
                    pd.date_range(
                        start=df_monthly.index.get_level_values("DATA").min(),
                        end=df_monthly.index.get_level_values("DATA").max(),
                        freq="M"
                    ),
                    df_monthly.index.get_level_values("TECNICO").unique(),
                ],
                names=["DATA", "TECNICO"]
            ),
            fill_value=0
        ).reset_index()

        fig = px.line(
            df_monthly,
            x="DATA",
            y="value",
            color="TECNICO",
            markers=True,
            color_discrete_map=COLORS.technician_colors
        )

        fig.update_layout(
            xaxis_title="Período",
            yaxis_title="Receita do Técnico (R$)",
            hovermode="x unified",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            autosize=True,
            height=CHART_CONFIG.default_height,
            margin=dict(l=0, r=0, t=30, b=0)
        )

        fig.update_traces(
            hovertemplate="<b>%{fullData.name}</b><br>R$ %{y:,.2f}<extra></extra>"
        )

        st.plotly_chart(fig, use_container_width=True)

    def render_technician_details(self, df: pd.DataFrame):
        """Renderiza detalhes por técnico"""
        st.subheader("Detalhes por Técnico")

        technicians = df["TECNICO"].unique()

        cols = st.columns(len(technicians))

        for idx, technician in enumerate(technicians):
            tech_data = df[df["TECNICO"] == technician]
            top_category = tech_data.groupby("CATEGORIA")["FATURAMENTO"].sum().idxmax()

            with cols[idx]:
                with st.container(border=True):
                    st.markdown(f"### 👨‍🔧 {technician}")

                    MetricCard.render(
                        "Serviços Realizados",
                        f"{len(tech_data):,}"
                    )

                    MetricCard.render(
                        "Receita Acumulada",
                        Formatting.format_monetary(tech_data["VALOR DO TÉCNICO"].sum())
                    )

                    st.markdown(f"**Especialidade:** {CATEGORY_DISPLAY_NAMES.get(top_category, top_category)}")

    def render_distribution_charts(self, df: pd.DataFrame):
        """Renderiza gráficos de distribuição"""
        col1, col2 = st.columns(2)

        with col1:
            ChartContainer.render(
                "Formas de Pagamento",
                lambda: self._render_payment_distribution(df),
                "Distribuição dos métodos de pagamento utilizados"
            )

        with col2:
            ChartContainer.render(
                "Status dos Serviços",
                lambda: self._render_status_distribution(df),
                "Distribuição dos serviços por status"
            )

    def _render_payment_distribution(self, df: pd.DataFrame):
        """Renderiza distribuição de formas de pagamento"""
        df_filtered = df.dropna(subset=["F/PAGAMENTO"])

        if not df_filtered.empty:
            fig = px.histogram(
                df_filtered,
                x="F/PAGAMENTO",
                histnorm="percent",
                text_auto=".1f",
                color_discrete_sequence=[COLORS.blue]
            )

            fig.update_layout(
                xaxis_title="Forma de Pagamento",
                yaxis_title="Porcentagem (%)",
                showlegend=False,
                autosize=True,
                height=400,
                margin=dict(l=0, r=0, t=30, b=0)
            )

            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Nenhum dado disponível")

    def _render_status_distribution(self, df: pd.DataFrame):
        """Renderiza distribuição de status"""
        df_filtered = df.dropna(subset=["STATUS"])

        if not df_filtered.empty:
            fig = px.histogram(
                df_filtered,
                y="STATUS",
                orientation="h",
                histnorm="percent",
                text_auto=".1f",
                color_discrete_sequence=[COLORS.green]
            )

            fig.update_layout(
                xaxis_title="Porcentagem (%)",
                yaxis_title="Status",
                showlegend=False,
                autosize=True,
                height=400,
                margin=dict(l=0, r=0, t=30, b=0)
            )

            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Nenhum dado disponível")

    def render_additional_insights(self, df: pd.DataFrame):
        """Renderiza insights adicionais"""
        col1, col2 = st.columns([1, 1])

        with col1:
            ChartContainer.render(
                "Distribuição de Serviços por Técnico",
                lambda: self._render_service_distribution(df),
                "Proporção de serviços realizados por cada técnico"
            )

        with col2:
            ChartContainer.render(
                "Top 10 Clientes",
                lambda: self._render_top_clients(df),
                "Clientes com maior volume de faturamento"
            )

    def _render_service_distribution(self, df: pd.DataFrame):
        """Renderiza distribuição de serviços por técnico"""
        df_filtered = df.dropna(subset=["PRODUTO/SERVIÇO"])
        df_grouped = df_filtered.groupby("TECNICO").size().reset_index(name="count")

        if not df_grouped.empty:
            fig = px.pie(
                df_grouped,
                values="count",
                names="TECNICO",
                color="TECNICO",
                color_discrete_map=COLORS.technician_colors,
                hole=0.4
            )

            fig.update_traces(
                textposition="inside",
                textinfo="percent+label",
                textfont_size=14
            )

            fig.update_layout(
                autosize=True,
                height=450,
                margin=dict(l=0, r=0, t=30, b=0)
            )

            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Nenhum dado disponível")

    def _render_top_clients(self, df: pd.DataFrame):
        """Renderiza top 10 clientes"""
        top_clients = df.groupby("CLIENTE").agg({
            "FATURAMENTO": "sum",
            "PRODUTO/SERVIÇO": "count"
        }).sort_values("FATURAMENTO", ascending=False).head(10)

        top_clients.columns = ["Faturamento Total", "Nº Serviços"]
        top_clients["Faturamento Total"] = top_clients["Faturamento Total"].apply(
            lambda x: Formatting.format_monetary(x)
        )

        st.dataframe(top_clients, use_container_width=True, height=450)

    def main(self):
        """Método principal que renderiza o dashboard"""
        # Header
        self.render_header()

        # Filtro de data na sidebar
        date_filter = DateFilter(self.df, "DATA")
        filtered_df = date_filter.filter_by_date()

        # Insights automáticos
        st.divider()
        self.render_insights_panel(filtered_df)

        # KPIs principais
        st.divider()
        self.render_kpi_row(filtered_df)

        # Análise Financeira
        st.divider()
        st.header("📈 Análise Financeira Mensal")

        # Gráfico principal em largura completa
        ChartContainer.render(
            "Desempenho Financeiro ao Longo do Tempo",
            lambda: self.render_financial_trend_chart(filtered_df),
            "Evolução mensal de faturamento, despesas e lucro"
        )

        # Detalhes por categoria em seção separada
        st.divider()
        self.render_category_details(filtered_df)

        # Análise por Categoria
        st.divider()
        st.header("📦 Análise por Categoria")

        ChartContainer.render(
            "Faturamento por Categoria",
            lambda: self.render_category_performance(filtered_df),
            "Evolução do faturamento de cada categoria ao longo do tempo"
        )

        # Análise por Técnico
        st.divider()
        st.header("👨‍🔧 Análise por Técnico")

        # Gráfico de desempenho em largura completa
        ChartContainer.render(
            "Receita Mensal por Técnico",
            lambda: self.render_technician_performance(filtered_df),
            "Evolução da receita de cada técnico ao longo do tempo"
        )

        # Detalhes dos técnicos abaixo do gráfico
        st.markdown("---")
        self.render_technician_details(filtered_df)

        # Distribuições
        st.divider()
        st.header("📊 Distribuições")
        self.render_distribution_charts(filtered_df)

        # Insights adicionais
        st.divider()
        st.header("🔍 Análises Complementares")
        self.render_additional_insights(filtered_df)

        # Footer
        st.divider()
        st.caption("📱 Connect-Cell Dashboard | Atualizado em tempo real")


if __name__ == "__main__":
    dashboard = DashboardV2()
    dashboard.main()
