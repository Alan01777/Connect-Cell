"""
Análise Avançada - Insights, Alertas e Previsões
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np

from utils import (
    DataLoader, ThemeManager, InsightBox,
    DataAnalyzer, MetricsCalculator, Formatting
)
from settings import page_settings
from config import COLORS, CATEGORY_DISPLAY_NAMES


class AdvancedAnalysis:
    """Análise avançada com alertas e previsões"""

    def __init__(self):
        page_settings("Análise Avançada", "🔬")
        ThemeManager.inject_custom_css()

        with st.spinner("🔬 Carregando análise avançada..."):
            self.df = DataLoader().load_data()

        if self.df.empty:
            st.error("❌ Não foi possível carregar os dados.")
            st.stop()

        self.df["DATA"] = pd.to_datetime(self.df["DATA"], format="%d/%m/%Y", errors='coerce')

    def render_header(self):
        """Renderiza cabeçalho"""
        st.title("🔬 Análise Avançada")
        st.markdown("*Insights profundos, alertas inteligentes e análises preditivas*")

    def render_alert_system(self):
        """Sistema de alertas inteligentes"""
        st.subheader("🚨 Sistema de Alertas")

        alerts = []

        # Alerta 1: Queda no faturamento
        last_month = self.df[self.df["DATA"] >= datetime.now() - timedelta(days=30)]
        prev_month = self.df[
            (self.df["DATA"] >= datetime.now() - timedelta(days=60)) &
            (self.df["DATA"] < datetime.now() - timedelta(days=30))
        ]

        if len(last_month) > 0 and len(prev_month) > 0:
            revenue_change = (
                (last_month["FATURAMENTO"].sum() - prev_month["FATURAMENTO"].sum()) /
                prev_month["FATURAMENTO"].sum() * 100
            )

            if revenue_change < -10:
                alerts.append({
                    "type": "error",
                    "message": f"⚠️ **ALERTA CRÍTICO**: Faturamento caiu {abs(revenue_change):.1f}% no último mês!"
                })
            elif revenue_change < -5:
                alerts.append({
                    "type": "warning",
                    "message": f"⚠️ Faturamento em queda: {abs(revenue_change):.1f}% no último mês"
                })

        # Alerta 2: Serviços pendentes
        pending_services = self.df[
            self.df["STATUS"].isin(["EM ANDAMENTO", "ORÇAMENTO"])
        ]
        if len(pending_services) > 10:
            alerts.append({
                "type": "warning",
                "message": f"📋 {len(pending_services)} serviços pendentes de conclusão"
            })

        # Alerta 3: Margem de lucro baixa
        recent_margin = (
            last_month["LUCRO LIQUIDO"].sum() / last_month["FATURAMENTO"].sum() * 100
            if last_month["FATURAMENTO"].sum() > 0 else 0
        )
        if recent_margin < 30:
            alerts.append({
                "type": "warning",
                "message": f"💰 Margem de lucro baixa no último mês: {recent_margin:.1f}%"
            })

        # Alerta 4: Concentração de cliente
        top_client_revenue = self.df.groupby("CLIENTE")["FATURAMENTO"].sum().max()
        total_revenue = self.df["FATURAMENTO"].sum()
        concentration = (top_client_revenue / total_revenue * 100) if total_revenue > 0 else 0

        if concentration > 30:
            top_client = self.df.groupby("CLIENTE")["FATURAMENTO"].sum().idxmax()
            alerts.append({
                "type": "info",
                "message": f"👤 Alta concentração em 1 cliente: {top_client} representa {concentration:.1f}% do faturamento"
            })

        # Alerta 5: Categoria em declínio
        monthly_by_cat = self.df.groupby([pd.Grouper(key="DATA", freq="M"), "CATEGORIA"])["FATURAMENTO"].sum()
        if len(monthly_by_cat) > 0:
            last_3_months = monthly_by_cat.tail(30)
            for category in self.df["CATEGORIA"].unique():
                cat_data = last_3_months[last_3_months.index.get_level_values(1) == category]
                if len(cat_data) >= 2:
                    trend = cat_data.values[-1] - cat_data.values[0]
                    if trend < 0 and abs(trend) > 1000:
                        alerts.append({
                            "type": "info",
                            "message": f"📉 {CATEGORY_DISPLAY_NAMES.get(category, category)} em tendência de queda"
                        })

        # Renderizar alertas
        if alerts:
            for alert in alerts:
                if alert["type"] == "error":
                    InsightBox.render_error(alert["message"])
                elif alert["type"] == "warning":
                    InsightBox.render_warning(alert["message"])
                else:
                    InsightBox.render_info(alert["message"])
        else:
            InsightBox.render_success("✅ Nenhum alerta crítico no momento!")

    def render_anomaly_detection(self):
        """Detecção de anomalias"""
        st.divider()
        st.subheader("🔍 Detecção de Anomalias")

        anomalies = DataAnalyzer.detect_anomalies(
            self.df,
            value_column="FATURAMENTO",
            threshold=2.0
        )

        if anomalies:
            st.markdown(f"**Encontradas {len(anomalies)} anomalias no faturamento:**")

            for anomaly in anomalies:
                emoji = "📈" if anomaly["type"] == "high" else "📉"
                date_str = anomaly["date"].strftime("%m/%Y")
                value_str = Formatting.format_monetary(anomaly["value"])

                InsightBox.render_warning(
                    f"{emoji} **{date_str}**: Faturamento {anomaly['type']} - {value_str} "
                    f"(Z-score: {anomaly['z_score']:.2f})"
                )
        else:
            InsightBox.render_success("✅ Nenhuma anomalia significativa detectada")

    def render_seasonality_analysis(self):
        """Análise de sazonalidade"""
        st.divider()
        st.subheader("📅 Análise de Sazonalidade")

        # Agrupar por mês do ano
        self.df["Mês"] = self.df["DATA"].dt.month
        self.df["Ano"] = self.df["DATA"].dt.year

        monthly_avg = self.df.groupby("Mês").agg({
            "FATURAMENTO": "mean",
            "PRODUTO/SERVIÇO": "count"
        }).reset_index()

        meses = [
            "Jan", "Fev", "Mar", "Abr", "Mai", "Jun",
            "Jul", "Ago", "Set", "Out", "Nov", "Dez"
        ]
        monthly_avg["Mês Nome"] = monthly_avg["Mês"].apply(lambda x: meses[x-1])

        col1, col2 = st.columns(2)

        with col1:
            # Gráfico de faturamento médio por mês
            fig = px.bar(
                monthly_avg,
                x="Mês Nome",
                y="FATURAMENTO",
                title="Faturamento Médio por Mês",
                color="FATURAMENTO",
                color_continuous_scale="Blues"
            )
            fig.update_layout(showlegend=False, xaxis_title="Mês", yaxis_title="Faturamento Médio (R$)")
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Gráfico de número de serviços por mês
            fig = px.bar(
                monthly_avg,
                x="Mês Nome",
                y="PRODUTO/SERVIÇO",
                title="Número Médio de Serviços por Mês",
                color="PRODUTO/SERVIÇO",
                color_continuous_scale="Greens"
            )
            fig.update_layout(showlegend=False, xaxis_title="Mês", yaxis_title="Nº Médio de Serviços")
            st.plotly_chart(fig, use_container_width=True)

        # Identificar meses de pico e vale
        peak_month = monthly_avg.loc[monthly_avg["FATURAMENTO"].idxmax()]
        low_month = monthly_avg.loc[monthly_avg["FATURAMENTO"].idxmin()]

        InsightBox.render_info(
            f"📈 **Mês de pico**: {peak_month['Mês Nome']} com faturamento médio de "
            f"{Formatting.format_monetary(peak_month['FATURAMENTO'])}"
        )
        InsightBox.render_info(
            f"📉 **Mês mais fraco**: {low_month['Mês Nome']} com faturamento médio de "
            f"{Formatting.format_monetary(low_month['FATURAMENTO'])}"
        )

    def render_customer_analysis(self):
        """Análise de clientes"""
        st.divider()
        st.subheader("👥 Análise de Clientes")

        # Análise RFM simplificada
        customer_stats = self.df.groupby("CLIENTE").agg({
            "DATA": "max",
            "FATURAMENTO": "sum",
            "PRODUTO/SERVIÇO": "count"
        }).reset_index()

        customer_stats.columns = ["Cliente", "Última Compra", "Faturamento Total", "Nº Serviços"]
        customer_stats["Dias desde última compra"] = (
            datetime.now() - customer_stats["Última Compra"]
        ).dt.days

        # Classificar clientes
        def classify_customer(row):
            if row["Dias desde última compra"] <= 30 and row["Faturamento Total"] > customer_stats["Faturamento Total"].median():
                return "🌟 VIP Ativo"
            elif row["Dias desde última compra"] <= 30:
                return "✅ Ativo"
            elif row["Dias desde última compra"] <= 90:
                return "⚠️ Em Risco"
            else:
                return "❌ Inativo"

        customer_stats["Classificação"] = customer_stats.apply(classify_customer, axis=1)

        # Contar por classificação
        classification_counts = customer_stats["Classificação"].value_counts()

        col1, col2 = st.columns(2)

        with col1:
            # Gráfico de pizza
            fig = px.pie(
                values=classification_counts.values,
                names=classification_counts.index,
                title="Distribuição de Clientes por Classificação"
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Top 10 clientes
            top10 = customer_stats.nlargest(10, "Faturamento Total")[
                ["Cliente", "Faturamento Total", "Nº Serviços", "Classificação"]
            ]
            top10["Faturamento Total"] = top10["Faturamento Total"].apply(Formatting.format_monetary)
            st.markdown("**Top 10 Clientes**")
            st.dataframe(top10, use_container_width=True, hide_index=True)

        # Alertas de clientes
        at_risk = customer_stats[customer_stats["Classificação"] == "⚠️ Em Risco"]
        if len(at_risk) > 0:
            InsightBox.render_warning(
                f"⚠️ {len(at_risk)} clientes em risco de churn (sem compras há 30-90 dias)"
            )

        inactive = customer_stats[customer_stats["Classificação"] == "❌ Inativo"]
        if len(inactive) > 0:
            InsightBox.render_info(
                f"💤 {len(inactive)} clientes inativos (sem compras há mais de 90 dias)"
            )

    def render_performance_forecast(self):
        """Previsão simples de performance"""
        st.divider()
        st.subheader("🔮 Previsão de Performance")

        # Agrupar por mês
        monthly = self.df.groupby(pd.Grouper(key="DATA", freq="M")).agg({
            "FATURAMENTO": "sum",
            "LUCRO LIQUIDO": "sum"
        }).reset_index()

        if len(monthly) < 3:
            InsightBox.render_warning("📊 Dados insuficientes para previsão (mínimo 3 meses)")
            return

        # Calcular média móvel simples (últimos 3 meses)
        monthly["MA_Revenue"] = monthly["FATURAMENTO"].rolling(window=3, min_periods=1).mean()

        # Previsão simples: média dos últimos 3 meses
        forecast_revenue = monthly["MA_Revenue"].iloc[-1]
        last_revenue = monthly["FATURAMENTO"].iloc[-1]

        # Gráfico com previsão
        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=monthly["DATA"],
            y=monthly["FATURAMENTO"],
            mode='lines+markers',
            name='Faturamento Real',
            line=dict(color=COLORS.blue, width=2)
        ))

        fig.add_trace(go.Scatter(
            x=monthly["DATA"],
            y=monthly["MA_Revenue"],
            mode='lines',
            name='Média Móvel (3 meses)',
            line=dict(color=COLORS.orange, width=2, dash='dash')
        ))

        # Adicionar previsão para próximo mês
        next_month = monthly["DATA"].iloc[-1] + pd.DateOffset(months=1)
        fig.add_trace(go.Scatter(
            x=[monthly["DATA"].iloc[-1], next_month],
            y=[last_revenue, forecast_revenue],
            mode='lines+markers',
            name='Previsão',
            line=dict(color=COLORS.green, width=2, dash='dot'),
            marker=dict(size=10)
        ))

        fig.update_layout(
            title="Previsão de Faturamento",
            xaxis_title="Mês",
            yaxis_title="Faturamento (R$)",
            hovermode="x unified"
        )

        st.plotly_chart(fig, use_container_width=True)

        # Insights da previsão
        variation = ((forecast_revenue - last_revenue) / last_revenue * 100) if last_revenue > 0 else 0

        if abs(variation) < 5:
            InsightBox.render_info(
                f"➡️ Previsão para próximo mês: {Formatting.format_monetary(forecast_revenue)} "
                f"(estável, {variation:+.1f}%)"
            )
        elif variation > 0:
            InsightBox.render_success(
                f"📈 Previsão para próximo mês: {Formatting.format_monetary(forecast_revenue)} "
                f"(crescimento de {variation:+.1f}%)"
            )
        else:
            InsightBox.render_warning(
                f"📉 Previsão para próximo mês: {Formatting.format_monetary(forecast_revenue)} "
                f"(queda de {variation:+.1f}%)"
            )

        st.caption("⚠️ Esta é uma previsão simples baseada em média móvel. Para previsões mais precisas, considere análises estatísticas avançadas.")

    def main(self):
        """Método principal"""
        self.render_header()

        st.divider()

        # Sistema de alertas
        self.render_alert_system()

        # Detecção de anomalias
        self.render_anomaly_detection()

        # Sazonalidade
        self.render_seasonality_analysis()

        # Análise de clientes
        self.render_customer_analysis()

        # Previsão
        self.render_performance_forecast()

        st.divider()
        st.caption("🔬 Análise Avançada | Insights Inteligentes")


if __name__ == "__main__":
    app = AdvancedAnalysis()
    app.main()
