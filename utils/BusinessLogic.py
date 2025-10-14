"""
Lógica de negócio e análises de dados
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
from config import APP_CONFIG


class DataAnalyzer:
    """Analisador de dados financeiros e operacionais"""

    @staticmethod
    def calculate_period_comparison(
        df: pd.DataFrame,
        date_column: str = "DATA",
        value_column: str = "FATURAMENTO"
    ) -> Dict[str, any]:
        """
        Calcula comparações período a período

        Returns:
            Dicionário com métricas e variações
        """
        df[date_column] = pd.to_datetime(df[date_column], format=APP_CONFIG.date_format, errors='coerce')

        # Mês atual vs mês anterior
        current_month = df[date_column].max().replace(day=1)
        last_month = (current_month - timedelta(days=1)).replace(day=1)

        current_data = df[df[date_column] >= current_month]
        last_month_data = df[
            (df[date_column] >= last_month) & (df[date_column] < current_month)
        ]

        current_value = current_data[value_column].sum()
        last_value = last_month_data[value_column].sum()

        # Calcular variação percentual
        if last_value > 0:
            variation = ((current_value - last_value) / last_value) * 100
        else:
            variation = 0 if current_value == 0 else 100

        return {
            "current_value": current_value,
            "last_value": last_value,
            "variation": variation,
            "variation_absolute": current_value - last_value,
            "trend": "up" if variation > 0 else "down" if variation < 0 else "stable"
        }

    @staticmethod
    def calculate_growth_rate(
        df: pd.DataFrame,
        date_column: str = "DATA",
        value_column: str = "FATURAMENTO",
        periods: int = 3
    ) -> float:
        """Calcula taxa de crescimento média dos últimos N períodos"""
        df[date_column] = pd.to_datetime(df[date_column], format=APP_CONFIG.date_format, errors='coerce')

        monthly_data = df.groupby(pd.Grouper(key=date_column, freq='M'))[value_column].sum()
        monthly_data = monthly_data.tail(periods)

        if len(monthly_data) < 2:
            return 0

        # Calcular taxa de crescimento composta
        try:
            first_value = monthly_data.iloc[0]
            last_value = monthly_data.iloc[-1]

            if first_value > 0:
                growth_rate = ((last_value / first_value) ** (1 / (len(monthly_data) - 1)) - 1) * 100
                return round(growth_rate, 2)
        except:
            pass

        return 0

    @staticmethod
    def identify_top_performers(
        df: pd.DataFrame,
        group_column: str,
        value_column: str = "FATURAMENTO",
        top_n: int = 5
    ) -> pd.DataFrame:
        """Identifica os top performers em uma categoria"""
        top = df.groupby(group_column)[value_column].sum().sort_values(ascending=False).head(top_n)
        return top.reset_index()

    @staticmethod
    def calculate_moving_average(
        df: pd.DataFrame,
        date_column: str = "DATA",
        value_column: str = "FATURAMENTO",
        window: int = 3
    ) -> pd.Series:
        """Calcula média móvel"""
        df[date_column] = pd.to_datetime(df[date_column], format=APP_CONFIG.date_format, errors='coerce')
        monthly_data = df.groupby(pd.Grouper(key=date_column, freq='M'))[value_column].sum()
        return monthly_data.rolling(window=window, min_periods=1).mean()

    @staticmethod
    def detect_anomalies(
        df: pd.DataFrame,
        date_column: str = "DATA",
        value_column: str = "FATURAMENTO",
        threshold: float = 2.0
    ) -> List[Dict]:
        """
        Detecta anomalias nos dados usando desvio padrão

        Args:
            threshold: Número de desvios padrão para considerar anomalia
        """
        df[date_column] = pd.to_datetime(df[date_column], format=APP_CONFIG.date_format, errors='coerce')
        monthly_data = df.groupby(pd.Grouper(key=date_column, freq='M'))[value_column].sum()

        mean = monthly_data.mean()
        std = monthly_data.std()

        anomalies = []
        for date, value in monthly_data.items():
            z_score = abs((value - mean) / std) if std > 0 else 0
            if z_score > threshold:
                anomalies.append({
                    "date": date,
                    "value": value,
                    "z_score": z_score,
                    "type": "high" if value > mean else "low"
                })

        return anomalies


class InsightGenerator:
    """Gerador de insights automáticos"""

    @staticmethod
    def generate_financial_insights(df: pd.DataFrame) -> List[str]:
        """Gera insights financeiros automáticos"""
        insights = []

        try:
            # Insight 1: Comparação mês atual vs anterior
            comparison = DataAnalyzer.calculate_period_comparison(df)
            if abs(comparison['variation']) > 10:
                trend_emoji = "📈" if comparison['variation'] > 0 else "📉"
                insights.append(
                    f"{trend_emoji} Faturamento {comparison['trend']} em "
                    f"{abs(comparison['variation']):.1f}% em relação ao mês anterior"
                )

            # Insight 2: Melhor categoria
            top_category = DataAnalyzer.identify_top_performers(
                df, "CATEGORIA", "FATURAMENTO", 1
            )
            if not top_category.empty:
                insights.append(
                    f"🏆 Categoria mais rentável: {top_category.iloc[0]['CATEGORIA']} "
                    f"(R$ {top_category.iloc[0]['FATURAMENTO']:,.2f})"
                )

            # Insight 3: Taxa de crescimento
            growth = DataAnalyzer.calculate_growth_rate(df)
            if abs(growth) > 5:
                trend_emoji = "🚀" if growth > 0 else "⚠️"
                insights.append(
                    f"{trend_emoji} Taxa de crescimento médio: {growth:+.1f}%/mês"
                )

            # Insight 4: Margem de lucro
            total_revenue = df["FATURAMENTO"].sum()
            total_profit = df["LUCRO LIQUIDO"].sum()
            if total_revenue > 0:
                margin = (total_profit / total_revenue) * 100
                margin_emoji = "💰" if margin > 40 else "💡" if margin > 20 else "⚠️"
                insights.append(
                    f"{margin_emoji} Margem de lucro líquido: {margin:.1f}%"
                )

            # Insight 5: Cliente mais valioso
            top_client = DataAnalyzer.identify_top_performers(
                df, "CLIENTE", "FATURAMENTO", 1
            )
            if not top_client.empty:
                insights.append(
                    f"👑 Cliente mais valioso: {top_client.iloc[0]['CLIENTE']} "
                    f"(R$ {top_client.iloc[0]['FATURAMENTO']:,.2f})"
                )

        except Exception as e:
            insights.append(f"⚠️ Erro ao gerar insights: {str(e)}")

        return insights

    @staticmethod
    def generate_operational_insights(df: pd.DataFrame) -> List[str]:
        """Gera insights operacionais"""
        insights = []

        try:
            # Distribuição por técnico
            tech_distribution = df.groupby("TECNICO").size()
            if len(tech_distribution) > 1:
                max_tech = tech_distribution.idxmax()
                max_count = tech_distribution.max()
                total = tech_distribution.sum()
                percentage = (max_count / total) * 100

                if percentage > 60:
                    insights.append(
                        f"⚖️ {max_tech} está sobrecarregado com {percentage:.0f}% dos serviços"
                    )

            # Status dos serviços
            pending = df[df["STATUS"].isin(["EM ANDAMENTO", "ORÇAMENTO"])].shape[0]
            total_services = len(df)

            if pending > 0:
                pending_percent = (pending / total_services) * 100
                if pending_percent > 20:
                    insights.append(
                        f"⏳ {pending} serviços pendentes ({pending_percent:.1f}% do total)"
                    )

        except Exception as e:
            insights.append(f"⚠️ Erro ao gerar insights operacionais: {str(e)}")

        return insights


class MetricsCalculator:
    """Calculadora de métricas de negócio"""

    @staticmethod
    def calculate_kpis(df: pd.DataFrame) -> Dict[str, any]:
        """Calcula KPIs principais"""
        return {
            # Financeiros
            "total_revenue": df["FATURAMENTO"].sum(),
            "total_expenses": df["DESPESAS"].sum(),
            "total_profit": df["LUCRO LIQUIDO"].sum(),
            "avg_ticket": df["FATURAMENTO"].mean(),
            "profit_margin": (df["LUCRO LIQUIDO"].sum() / df["FATURAMENTO"].sum() * 100)
            if df["FATURAMENTO"].sum() > 0 else 0,

            # Operacionais
            "total_services": len(df),
            "services_per_day": len(df) / max(1, (pd.to_datetime(df["DATA"], format=APP_CONFIG.date_format).max() -
                                                   pd.to_datetime(df["DATA"], format=APP_CONFIG.date_format).min()).days),

            # Por status
            "completed": df[df["STATUS"] == "FINALIZADO"].shape[0],
            "pending": df[df["STATUS"].isin(["EM ANDAMENTO", "ORÇAMENTO"])].shape[0],
        }

    @staticmethod
    def calculate_category_performance(df: pd.DataFrame) -> pd.DataFrame:
        """Calcula performance por categoria"""
        return df.groupby("CATEGORIA").agg({
            "FATURAMENTO": ["sum", "mean", "count"],
            "LUCRO LIQUIDO": ["sum", "mean"],
            "DESPESAS": "sum"
        }).round(2)

    @staticmethod
    def calculate_technician_performance(df: pd.DataFrame) -> pd.DataFrame:
        """Calcula performance por técnico"""
        return df.groupby("TECNICO").agg({
            "FATURAMENTO": ["sum", "mean", "count"],
            "VALOR DO TÉCNICO": "sum",
            "CATEGORIA": lambda x: x.mode()[0] if not x.mode().empty else "N/A"
        }).round(2)
