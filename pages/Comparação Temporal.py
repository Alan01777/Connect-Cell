"""
Comparação Temporal - Análise de Performance ao Longo do Tempo
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

from utils import (
    DataLoader, ThemeManager, MetricCard, ChartContainer,
    InsightBox, KPIRow, DataAnalyzer, Formatting
)
from settings import page_settings
from config import COLORS, CATEGORY_DISPLAY_NAMES


class TemporalComparison:
    """Dashboard de comparação temporal"""

    def __init__(self):
        page_settings("Comparação Temporal", "📅")
        ThemeManager.inject_custom_css()

        with st.spinner("📊 Carregando dados..."):
            self.df = DataLoader().load_data()

        if self.df.empty:
            st.error("❌ Não foi possível carregar os dados.")
            st.stop()

        # Preparar dados
        self.df["DATA"] = pd.to_datetime(self.df["DATA"], format="%d/%m/%Y", errors='coerce')

    def render_header(self):
        """Renderiza cabeçalho"""
        st.title("📅 Comparação Temporal")
        st.markdown("*Analise o desempenho ao longo do tempo e identifique tendências*")

    def render_period_selector(self) -> dict:
        """Renderiza seletor de períodos para comparação"""
        st.subheader("🗓️ Selecione os Períodos para Comparar")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**📊 Período 1**")
            period1_start = st.date_input(
                "Data Inicial",
                value=datetime.now().replace(day=1) - timedelta(days=60),
                key="p1_start"
            )
            period1_end = st.date_input(
                "Data Final",
                value=datetime.now().replace(day=1) - timedelta(days=31),
                key="p1_end"
            )

        with col2:
            st.markdown("**📊 Período 2**")
            period2_start = st.date_input(
                "Data Inicial",
                value=datetime.now().replace(day=1),
                key="p2_start"
            )
            period2_end = st.date_input(
                "Data Final",
                value=datetime.now(),
                key="p2_end"
            )

        return {
            "period1": {"start": period1_start, "end": period1_end},
            "period2": {"start": period2_start, "end": period2_end}
        }

    def filter_by_period(self, period: dict) -> pd.DataFrame:
        """Filtra dados por período"""
        mask = (
            (self.df["DATA"].dt.date >= period["start"]) &
            (self.df["DATA"].dt.date <= period["end"])
        )
        return self.df[mask]

    def calculate_metrics(self, df: pd.DataFrame) -> dict:
        """Calcula métricas de um período"""
        return {
            "total_services": len(df),
            "revenue": df["FATURAMENTO"].sum(),
            "expenses": df["DESPESAS"].sum(),
            "profit": df["LUCRO LIQUIDO"].sum(),
            "avg_ticket": df["FATURAMENTO"].mean() if len(df) > 0 else 0,
            "margin": (df["LUCRO LIQUIDO"].sum() / df["FATURAMENTO"].sum() * 100)
            if df["FATURAMENTO"].sum() > 0 else 0
        }

    def render_comparison_kpis(self, metrics1: dict, metrics2: dict):
        """Renderiza KPIs comparativos"""
        st.subheader("📊 Comparação de Métricas")

        def calc_variation(current, previous):
            if previous == 0:
                return 0
            return ((current - previous) / previous) * 100

        kpis = [
            {
                "label": "Faturamento",
                "value": Formatting.format_monetary(metrics2["revenue"]),
                "delta": f"{calc_variation(metrics2['revenue'], metrics1['revenue']):+.1f}%",
                "icon": "💰"
            },
            {
                "label": "Lucro Líquido",
                "value": Formatting.format_monetary(metrics2["profit"]),
                "delta": f"{calc_variation(metrics2['profit'], metrics1['profit']):+.1f}%",
                "icon": "📈"
            },
            {
                "label": "Serviços",
                "value": f"{metrics2['total_services']:,}",
                "delta": f"{calc_variation(metrics2['total_services'], metrics1['total_services']):+.1f}%",
                "icon": "🔧"
            },
            {
                "label": "Ticket Médio",
                "value": Formatting.format_monetary(metrics2["avg_ticket"]),
                "delta": f"{calc_variation(metrics2['avg_ticket'], metrics1['avg_ticket']):+.1f}%",
                "icon": "🎯"
            },
        ]

        KPIRow.render(kpis)

        # Insights automáticos
        insights = []

        revenue_var = calc_variation(metrics2["revenue"], metrics1["revenue"])
        if abs(revenue_var) > 10:
            emoji = "📈" if revenue_var > 0 else "📉"
            insights.append(
                f"{emoji} Faturamento {revenue_var:+.1f}% comparado ao período anterior"
            )

        services_var = calc_variation(metrics2["total_services"], metrics1["total_services"])
        if abs(services_var) > 15:
            emoji = "🔥" if services_var > 0 else "⚠️"
            insights.append(
                f"{emoji} Número de serviços {services_var:+.1f}% comparado ao período anterior"
            )

        margin_diff = metrics2["margin"] - metrics1["margin"]
        if abs(margin_diff) > 5:
            emoji = "💰" if margin_diff > 0 else "💸"
            insights.append(
                f"{emoji} Margem de lucro {margin_diff:+.1f} pontos percentuais"
            )

        if insights:
            st.divider()
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**💡 Insights da Comparação**")
                for insight in insights:
                    InsightBox.render_info(insight)

    def render_detailed_comparison(self, df1: pd.DataFrame, df2: pd.DataFrame, metrics1: dict, metrics2: dict):
        """Renderiza comparação detalhada"""
        st.divider()
        st.subheader("📋 Comparação Detalhada")

        # Criar DataFrame de comparação
        comparison_data = {
            "Métrica": [
                "Total de Serviços",
                "Faturamento Total",
                "Despesas Totais",
                "Lucro Líquido",
                "Ticket Médio",
                "Margem de Lucro"
            ],
            "Período 1": [
                f"{metrics1['total_services']:,}",
                Formatting.format_monetary(metrics1["revenue"]),
                Formatting.format_monetary(metrics1["expenses"]),
                Formatting.format_monetary(metrics1["profit"]),
                Formatting.format_monetary(metrics1["avg_ticket"]),
                f"{metrics1['margin']:.1f}%"
            ],
            "Período 2": [
                f"{metrics2['total_services']:,}",
                Formatting.format_monetary(metrics2["revenue"]),
                Formatting.format_monetary(metrics2["expenses"]),
                Formatting.format_monetary(metrics2["profit"]),
                Formatting.format_monetary(metrics2["avg_ticket"]),
                f"{metrics2['margin']:.1f}%"
            ]
        }

        # Calcular variações
        variations = []
        for i, metric_name in enumerate(["total_services", "revenue", "expenses", "profit", "avg_ticket", "margin"]):
            if metrics1[metric_name] == 0:
                var = 0
            else:
                var = ((metrics2[metric_name] - metrics1[metric_name]) / metrics1[metric_name]) * 100

            emoji = "📈" if var > 0 else "📉" if var < 0 else "➡️"
            variations.append(f"{emoji} {var:+.1f}%")

        comparison_data["Variação"] = variations

        comparison_df = pd.DataFrame(comparison_data)
        st.dataframe(comparison_df, use_container_width=True, hide_index=True)

    def render_category_comparison(self, df1: pd.DataFrame, df2: pd.DataFrame):
        """Renderiza comparação por categoria"""
        st.divider()
        st.subheader("📦 Comparação por Categoria")

        # Agregar por categoria
        cat1 = df1.groupby("CATEGORIA")["FATURAMENTO"].sum().reset_index()
        cat2 = df2.groupby("CATEGORIA")["FATURAMENTO"].sum().reset_index()

        cat1.columns = ["Categoria", "Período 1"]
        cat2.columns = ["Categoria", "Período 2"]

        # Merge
        cat_comparison = pd.merge(cat1, cat2, on="Categoria", how="outer").fillna(0)
        cat_comparison["Variação (%)"] = (
            (cat_comparison["Período 2"] - cat_comparison["Período 1"]) /
            cat_comparison["Período 1"] * 100
        ).fillna(0)

        # Aplicar nomes amigáveis
        cat_comparison["Categoria"] = cat_comparison["Categoria"].apply(
            lambda x: CATEGORY_DISPLAY_NAMES.get(x, x)
        )

        # Gráfico de barras comparativo
        fig = go.Figure()

        fig.add_trace(go.Bar(
            name='Período 1',
            x=cat_comparison["Categoria"],
            y=cat_comparison["Período 1"],
            marker_color=COLORS.blue,
            text=cat_comparison["Período 1"].apply(lambda x: f"R$ {x:,.0f}"),
            textposition='outside'
        ))

        fig.add_trace(go.Bar(
            name='Período 2',
            x=cat_comparison["Categoria"],
            y=cat_comparison["Período 2"],
            marker_color=COLORS.green,
            text=cat_comparison["Período 2"].apply(lambda x: f"R$ {x:,.0f}"),
            textposition='outside'
        ))

        fig.update_layout(
            barmode='group',
            xaxis_title="Categoria",
            yaxis_title="Faturamento (R$)",
            hovermode="x unified",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )

        st.plotly_chart(fig, use_container_width=True)

        # Tabela de dados
        st.dataframe(cat_comparison, use_container_width=True, hide_index=True)

    def render_technician_comparison(self, df1: pd.DataFrame, df2: pd.DataFrame):
        """Renderiza comparação por técnico"""
        st.divider()
        st.subheader("👨‍🔧 Comparação por Técnico")

        # Agregar por técnico
        tech1 = df1.groupby("TECNICO").agg({
            "FATURAMENTO": "sum",
            "PRODUTO/SERVIÇO": "count"
        }).reset_index()
        tech1.columns = ["Técnico", "Faturamento P1", "Serviços P1"]

        tech2 = df2.groupby("TECNICO").agg({
            "FATURAMENTO": "sum",
            "PRODUTO/SERVIÇO": "count"
        }).reset_index()
        tech2.columns = ["Técnico", "Faturamento P2", "Serviços P2"]

        # Merge
        tech_comparison = pd.merge(tech1, tech2, on="Técnico", how="outer").fillna(0)

        col1, col2 = st.columns(2)

        with col1:
            # Gráfico de faturamento
            fig = go.Figure()

            fig.add_trace(go.Bar(
                name='Período 1',
                x=tech_comparison["Técnico"],
                y=tech_comparison["Faturamento P1"],
                marker_color=COLORS.blue
            ))

            fig.add_trace(go.Bar(
                name='Período 2',
                x=tech_comparison["Técnico"],
                y=tech_comparison["Faturamento P2"],
                marker_color=COLORS.green
            ))

            fig.update_layout(
                barmode='group',
                title="Faturamento por Técnico",
                xaxis_title="Técnico",
                yaxis_title="Faturamento (R$)"
            )

            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Gráfico de número de serviços
            fig = go.Figure()

            fig.add_trace(go.Bar(
                name='Período 1',
                x=tech_comparison["Técnico"],
                y=tech_comparison["Serviços P1"],
                marker_color=COLORS.blue
            ))

            fig.add_trace(go.Bar(
                name='Período 2',
                x=tech_comparison["Técnico"],
                y=tech_comparison["Serviços P2"],
                marker_color=COLORS.green
            ))

            fig.update_layout(
                barmode='group',
                title="Número de Serviços por Técnico",
                xaxis_title="Técnico",
                yaxis_title="Quantidade"
            )

            st.plotly_chart(fig, use_container_width=True)

    def render_trend_analysis(self):
        """Renderiza análise de tendência mensal"""
        st.divider()
        st.subheader("📈 Tendência Mensal")

        # Agrupar por mês
        monthly = self.df.groupby(pd.Grouper(key="DATA", freq="M")).agg({
            "FATURAMENTO": "sum",
            "LUCRO LIQUIDO": "sum",
            "PRODUTO/SERVIÇO": "count"
        }).reset_index()

        monthly.columns = ["Mês", "Faturamento", "Lucro", "Serviços"]

        # Gráfico de linha com múltiplas métricas
        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=monthly["Mês"],
            y=monthly["Faturamento"],
            mode='lines+markers',
            name='Faturamento',
            line=dict(color=COLORS.green, width=3),
            yaxis='y'
        ))

        fig.add_trace(go.Scatter(
            x=monthly["Mês"],
            y=monthly["Lucro"],
            mode='lines+markers',
            name='Lucro',
            line=dict(color=COLORS.blue, width=3),
            yaxis='y'
        ))

        fig.add_trace(go.Scatter(
            x=monthly["Mês"],
            y=monthly["Serviços"],
            mode='lines+markers',
            name='Nº Serviços',
            line=dict(color=COLORS.orange, width=3),
            yaxis='y2'
        ))

        fig.update_layout(
            xaxis_title="Mês",
            yaxis_title="Valor (R$)",
            yaxis2=dict(
                title="Quantidade de Serviços",
                overlaying='y',
                side='right'
            ),
            hovermode="x unified",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )

        st.plotly_chart(fig, use_container_width=True)

        # Calcular taxa de crescimento
        if len(monthly) >= 2:
            recent_growth = DataAnalyzer.calculate_growth_rate(self.df, periods=3)

            if recent_growth != 0:
                emoji = "🚀" if recent_growth > 0 else "📉"
                InsightBox.render_info(
                    f"{emoji} Taxa de crescimento médio dos últimos 3 meses: {recent_growth:+.1f}%/mês"
                )

    def main(self):
        """Método principal"""
        self.render_header()

        st.divider()

        # Seletor de períodos
        periods = self.render_period_selector()

        st.divider()

        # Filtrar dados por período
        df1 = self.filter_by_period(periods["period1"])
        df2 = self.filter_by_period(periods["period2"])

        # Calcular métricas
        metrics1 = self.calculate_metrics(df1)
        metrics2 = self.calculate_metrics(df2)

        # KPIs comparativos
        self.render_comparison_kpis(metrics1, metrics2)

        # Comparação detalhada
        self.render_detailed_comparison(df1, df2, metrics1, metrics2)

        # Comparação por categoria
        self.render_category_comparison(df1, df2)

        # Comparação por técnico
        self.render_technician_comparison(df1, df2)

        # Tendência mensal
        self.render_trend_analysis()

        st.divider()
        st.caption("📅 Comparação Temporal | Análise de Performance")


if __name__ == "__main__":
    app = TemporalComparison()
    app.main()
