"""
Previsões - Sistema de Forecasting Inteligente
Previsões de faturamento, lucro e outras métricas usando múltiplos algoritmos
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

from utils import (
    DataLoader, ThemeManager, MetricCard, ChartContainer,
    InsightBox, ForecastEngine, ForecastResult, Formatting
)
from settings import page_settings
from config import COLORS


class ForecastDashboard:
    """Dashboard de Previsões"""

    def __init__(self):
        page_settings("Previsões", "🔮")
        ThemeManager.inject_custom_css()

        with st.spinner("🔮 Carregando previsões..."):
            self.df = DataLoader().load_data()

        if self.df.empty:
            st.error("❌ Não foi possível carregar os dados.")
            st.stop()

    def render_header(self):
        """Renderiza cabeçalho"""
        st.title("🔮 Previsões Inteligentes")
        st.markdown("*Previsões automáticas baseadas em dados históricos usando múltiplos algoritmos*")

    def render_metric_selector(self):
        """Seletor de métrica para previsão"""
        st.subheader("📊 Configure sua Previsão")

        col1, col2, col3 = st.columns(3)

        with col1:
            metric = st.selectbox(
                "Métrica a Prever",
                ["FATURAMENTO", "LUCRO LIQUIDO", "DESPESAS"],
                help="Selecione qual métrica deseja prever"
            )

        with col2:
            periods = st.slider(
                "Períodos Futuros",
                min_value=1,
                max_value=12,
                value=3,
                help="Quantos meses à frente prever"
            )

        with col3:
            method = st.selectbox(
                "Método de Previsão",
                ["Ensemble (Recomendado)", "Tendência Linear", "Média Móvel", "Sazonal"],
                help="Algoritmo de previsão a usar"
            )

        return metric, periods, method

    def render_forecast_chart(self, df: pd.DataFrame, metric: str,
                             forecast_result: ForecastResult):
        """
        Renderiza gráfico de previsão

        Args:
            df: DataFrame histórico
            metric: Nome da métrica
            forecast_result: Resultado da previsão
        """
        # Preparar dados históricos
        df_copy = df.copy()
        df_copy["DATA"] = pd.to_datetime(df_copy["DATA"], format="%d/%m/%Y", errors='coerce')
        df_monthly = df_copy.set_index("DATA")[metric].resample('M').sum().reset_index()

        # Criar figura
        fig = go.Figure()

        # Adicionar linha histórica
        fig.add_trace(go.Scatter(
            x=df_monthly["DATA"],
            y=df_monthly[metric],
            name="Histórico",
            mode='lines+markers',
            line=dict(color=COLORS.blue, width=2),
            marker=dict(size=6)
        ))

        # Adicionar previsão
        fig.add_trace(go.Scatter(
            x=forecast_result.dates,
            y=forecast_result.values,
            name="Previsão",
            mode='lines+markers',
            line=dict(color=COLORS.green, width=2, dash='dash'),
            marker=dict(size=8, symbol='star')
        ))

        # Adicionar intervalo de confiança
        fig.add_trace(go.Scatter(
            x=forecast_result.dates + forecast_result.dates[::-1],
            y=forecast_result.upper_bound + forecast_result.lower_bound[::-1],
            fill='toself',
            fillcolor=f'rgba(46, 160, 67, 0.2)',
            line=dict(color='rgba(255,255,255,0)'),
            showlegend=True,
            name='Intervalo de Confiança (95%)',
            hoverinfo='skip'
        ))

        # Adicionar linha conectando último histórico com primeira previsão
        if not df_monthly.empty and forecast_result.dates:
            last_historical = df_monthly.iloc[-1]
            fig.add_trace(go.Scatter(
                x=[last_historical["DATA"], forecast_result.dates[0]],
                y=[last_historical[metric], forecast_result.values[0]],
                mode='lines',
                line=dict(color=COLORS.gray, width=1, dash='dot'),
                showlegend=False,
                hoverinfo='skip'
            ))

        # Configurar layout
        fig.update_layout(
            xaxis_title="Período",
            yaxis_title=f"{metric} (R$)",
            hovermode="x unified",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            autosize=True,
            height=500,
            margin=dict(l=0, r=0, t=30, b=0)
        )

        st.plotly_chart(fig, use_container_width=True)

    def render_forecast_details(self, forecast_result: ForecastResult):
        """Renderiza detalhes da previsão"""
        st.subheader("📋 Detalhes da Previsão")

        # Métricas de confiança
        col1, col2, col3 = st.columns(3)

        with col1:
            MetricCard.render(
                "Método Utilizado",
                forecast_result.method
            )

        with col2:
            confidence_color = "normal"
            if forecast_result.confidence >= 70:
                confidence_emoji = "🟢"
            elif forecast_result.confidence >= 50:
                confidence_emoji = "🟡"
            else:
                confidence_emoji = "🔴"

            MetricCard.render(
                "Confiança",
                f"{confidence_emoji} {forecast_result.confidence:.1f}%"
            )

        with col3:
            total_forecast = sum(forecast_result.values)
            MetricCard.render(
                "Total Previsto",
                Formatting.format_monetary(total_forecast)
            )

        # Tabela de previsões
        st.markdown("---")
        st.markdown("**📅 Previsões Detalhadas por Período**")

        forecast_df = pd.DataFrame({
            "Período": [d.strftime("%m/%Y") for d in forecast_result.dates],
            "Previsão": [Formatting.format_monetary(v) for v in forecast_result.values],
            "Limite Inferior": [Formatting.format_monetary(l) for l in forecast_result.lower_bound],
            "Limite Superior": [Formatting.format_monetary(u) for u in forecast_result.upper_bound],
        })

        st.dataframe(forecast_df, use_container_width=True, hide_index=True)

    def render_method_comparison(self, df: pd.DataFrame, metric: str, periods: int):
        """Compara todos os métodos de previsão"""
        st.subheader("🔍 Comparação de Métodos")

        # Gerar previsões com todos os métodos
        all_forecasts = ForecastEngine.auto_forecast(df, "DATA", metric, periods)

        if not all_forecasts:
            st.warning("Dados insuficientes para comparação")
            return

        # Criar gráfico comparativo
        fig = go.Figure()

        # Preparar dados históricos
        df_copy = df.copy()
        df_copy["DATA"] = pd.to_datetime(df_copy["DATA"], format="%d/%m/%Y", errors='coerce')
        df_monthly = df_copy.set_index("DATA")[metric].resample('M').sum().reset_index()

        # Adicionar histórico
        fig.add_trace(go.Scatter(
            x=df_monthly["DATA"],
            y=df_monthly[metric],
            name="Histórico",
            mode='lines',
            line=dict(color=COLORS.gray, width=2)
        ))

        # Cores para cada método
        method_colors = {
            'ensemble': COLORS.green,
            'linear_trend': COLORS.blue,
            'moving_average': COLORS.orange,
            'seasonal': COLORS.purple
        }

        # Adicionar cada previsão
        for method_key, forecast in all_forecasts.items():
            fig.add_trace(go.Scatter(
                x=forecast.dates,
                y=forecast.values,
                name=forecast.method,
                mode='lines+markers',
                line=dict(
                    color=method_colors.get(method_key, COLORS.gray),
                    width=2,
                    dash='dash'
                )
            ))

        fig.update_layout(
            xaxis_title="Período",
            yaxis_title=f"{metric} (R$)",
            hovermode="x unified",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            autosize=True,
            height=500,
            margin=dict(l=0, r=0, t=30, b=0)
        )

        st.plotly_chart(fig, use_container_width=True)

        # Tabela comparativa de confiança
        st.markdown("**📊 Comparação de Confiança**")

        comparison_df = pd.DataFrame([
            {
                "Método": forecast.method,
                "Confiança": f"{forecast.confidence:.1f}%",
                "Próximo Período": Formatting.format_monetary(forecast.values[0]),
                "Total Previsto": Formatting.format_monetary(sum(forecast.values))
            }
            for forecast in all_forecasts.values()
        ]).sort_values("Confiança", ascending=False)

        st.dataframe(comparison_df, use_container_width=True, hide_index=True)

    def render_insights(self, df: pd.DataFrame, metric: str, forecast_result: ForecastResult):
        """Renderiza insights sobre a previsão"""
        st.subheader("💡 Insights da Previsão")

        # Calcular tendência
        values = forecast_result.values
        if values[0] > values[-1]:
            trend = "decrescente"
            trend_icon = "📉"
            trend_color = "warning"
        elif values[0] < values[-1]:
            trend = "crescente"
            trend_icon = "📈"
            trend_color = "success"
        else:
            trend = "estável"
            trend_icon = "➡️"
            trend_color = "info"

        # Calcular variação
        variation = ((values[-1] - values[0]) / values[0] * 100) if values[0] != 0 else 0

        # Gerar insights
        insights = []

        insights.append(
            f"{trend_icon} A previsão indica uma tendência **{trend}** "
            f"com variação de **{variation:+.1f}%** no período."
        )

        if forecast_result.confidence >= 70:
            insights.append(
                f"🟢 Alta confiança ({forecast_result.confidence:.1f}%) - "
                f"Os dados históricos apresentam padrão consistente."
            )
        elif forecast_result.confidence >= 50:
            insights.append(
                f"🟡 Confiança moderada ({forecast_result.confidence:.1f}%) - "
                f"Considere analisar fatores externos que podem influenciar."
            )
        else:
            insights.append(
                f"🔴 Baixa confiança ({forecast_result.confidence:.1f}%) - "
                f"Dados históricos apresentam alta volatilidade. Use com cautela."
            )

        # Comparar com média histórica
        df_copy = df.copy()
        df_copy["DATA"] = pd.to_datetime(df_copy["DATA"], format="%d/%m/%Y", errors='coerce')
        historical_avg = df_copy[metric].mean()
        forecast_avg = sum(values) / len(values)

        diff_from_historical = ((forecast_avg - historical_avg) / historical_avg * 100) if historical_avg != 0 else 0

        if abs(diff_from_historical) > 20:
            insights.append(
                f"⚠️ A previsão média é **{diff_from_historical:+.1f}%** "
                f"diferente da média histórica. Verifique se há mudanças significativas no negócio."
            )

        # Renderizar insights
        for insight in insights:
            InsightBox.render_info(insight)

    def main(self):
        """Método principal"""
        self.render_header()

        st.divider()

        # Seletor de configurações
        metric, periods, method_name = self.render_metric_selector()

        st.divider()

        # Mapear nome do método para chave
        method_map = {
            "Ensemble (Recomendado)": "ensemble",
            "Tendência Linear": "linear_trend",
            "Média Móvel": "moving_average",
            "Sazonal": "seasonal"
        }

        method_key = method_map[method_name]

        # Gerar previsões
        with st.spinner("🔮 Gerando previsões..."):
            all_forecasts = ForecastEngine.auto_forecast(self.df, "DATA", metric, periods)

            if not all_forecasts:
                st.error("❌ Dados insuficientes para gerar previsões. São necessários pelo menos 3 períodos de dados.")
                st.stop()

            forecast_result = all_forecasts[method_key]

        # Gráfico principal
        ChartContainer.render(
            f"Previsão de {metric}",
            lambda: self.render_forecast_chart(self.df, metric, forecast_result),
            f"Previsão para os próximos {periods} meses usando {method_name}"
        )

        st.divider()

        # Detalhes da previsão
        self.render_forecast_details(forecast_result)

        st.divider()

        # Insights
        self.render_insights(self.df, metric, forecast_result)

        st.divider()

        # Comparação de métodos
        self.render_method_comparison(self.df, metric, periods)

        # Footer
        st.divider()
        st.caption("🔮 Sistema de Previsões | Os resultados são baseados em dados históricos e devem ser usados como referência")


if __name__ == "__main__":
    dashboard = ForecastDashboard()
    dashboard.main()
