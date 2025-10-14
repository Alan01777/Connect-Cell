"""
Motor de Previsão - Sistema de forecasting para métricas do negócio
Implementa múltiplos algoritmos de previsão sem dependências externas pesadas
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class ForecastResult:
    """Resultado de uma previsão"""
    dates: List[datetime]
    values: List[float]
    lower_bound: List[float]
    upper_bound: List[float]
    confidence: float
    method: str
    metric_name: str


class ForecastEngine:
    """Motor de previsão com múltiplos algoritmos"""

    @staticmethod
    def prepare_time_series(df: pd.DataFrame, date_column: str, value_column: str,
                           freq: str = 'M') -> pd.DataFrame:
        """
        Prepara série temporal para previsão

        Args:
            df: DataFrame com os dados
            date_column: Nome da coluna de data
            value_column: Nome da coluna de valor
            freq: Frequência ('D', 'W', 'M')

        Returns:
            DataFrame agrupado por período
        """
        df_copy = df.copy()
        df_copy[date_column] = pd.to_datetime(df_copy[date_column], format="%d/%m/%Y", errors='coerce')
        df_copy = df_copy.dropna(subset=[date_column, value_column])

        # Agrupar por período
        df_copy.set_index(date_column, inplace=True)
        ts_data = df_copy[value_column].resample(freq).sum()

        return ts_data.to_frame().reset_index()

    @staticmethod
    def moving_average_forecast(data: pd.Series, periods: int = 3,
                               window: int = 3) -> ForecastResult:
        """
        Previsão usando Média Móvel Simples

        Args:
            data: Série temporal de valores
            periods: Número de períodos a prever
            window: Janela da média móvel

        Returns:
            ForecastResult com previsões
        """
        # Calcular média móvel
        ma = data.rolling(window=window, min_periods=1).mean()

        # Últimos valores para previsão
        last_values = data.tail(window).values

        # Gerar previsões
        forecasts = []
        for _ in range(periods):
            forecast = np.mean(last_values)
            forecasts.append(forecast)
            last_values = np.append(last_values[1:], forecast)

        # Calcular desvio padrão para intervalos de confiança
        std = data.std()

        # Gerar datas futuras (assumindo frequência mensal)
        last_date = data.index[-1]
        future_dates = [last_date + timedelta(days=30 * (i + 1)) for i in range(periods)]

        # Intervalos de confiança (95%)
        margin = 1.96 * std
        lower = [f - margin for f in forecasts]
        upper = [f + margin for f in forecasts]

        # Calcular confiança baseada na estabilidade da série
        cv = std / data.mean() if data.mean() != 0 else 1
        confidence = max(0, min(100, 100 * (1 - cv)))

        return ForecastResult(
            dates=future_dates,
            values=forecasts,
            lower_bound=lower,
            upper_bound=upper,
            confidence=confidence,
            method="Média Móvel",
            metric_name="Valor"
        )

    @staticmethod
    def linear_trend_forecast(data: pd.Series, periods: int = 3) -> ForecastResult:
        """
        Previsão usando Regressão Linear (Tendência)

        Args:
            data: Série temporal de valores
            periods: Número de períodos a prever

        Returns:
            ForecastResult com previsões
        """
        # Preparar dados para regressão
        x = np.arange(len(data)).reshape(-1, 1)
        y = data.values

        # Calcular coeficientes da regressão linear (y = ax + b)
        x_mean = x.mean()
        y_mean = y.mean()

        numerator = ((x.flatten() - x_mean) * (y - y_mean)).sum()
        denominator = ((x.flatten() - x_mean) ** 2).sum()

        a = numerator / denominator if denominator != 0 else 0
        b = y_mean - a * x_mean

        # Gerar previsões
        future_x = np.arange(len(data), len(data) + periods)
        forecasts = a * future_x + b

        # Calcular erro padrão
        y_pred = a * x.flatten() + b
        residuals = y - y_pred
        std_error = np.std(residuals)

        # Gerar datas futuras
        last_date = data.index[-1]
        future_dates = [last_date + timedelta(days=30 * (i + 1)) for i in range(periods)]

        # Intervalos de confiança
        margin = 1.96 * std_error
        lower = forecasts - margin
        upper = forecasts + margin

        # Calcular R² para confiança
        ss_res = ((y - y_pred) ** 2).sum()
        ss_tot = ((y - y_mean) ** 2).sum()
        r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
        confidence = max(0, min(100, r_squared * 100))

        return ForecastResult(
            dates=future_dates,
            values=forecasts.tolist(),
            lower_bound=lower.tolist(),
            upper_bound=upper.tolist(),
            confidence=confidence,
            method="Tendência Linear",
            metric_name="Valor"
        )

    @staticmethod
    def seasonal_naive_forecast(data: pd.Series, periods: int = 3,
                               season_length: int = 12) -> ForecastResult:
        """
        Previsão Ingênua Sazonal - usa valores do mesmo período do ano anterior

        Args:
            data: Série temporal de valores
            periods: Número de períodos a prever
            season_length: Comprimento da sazonalidade (12 para mensal anual)

        Returns:
            ForecastResult com previsões
        """
        forecasts = []

        for i in range(periods):
            # Pegar valor do mesmo período no ano anterior
            look_back_idx = len(data) - season_length + i
            if look_back_idx >= 0 and look_back_idx < len(data):
                forecasts.append(data.iloc[look_back_idx])
            else:
                # Se não há dados sazonais, usar média
                forecasts.append(data.mean())

        # Calcular desvio padrão sazonal
        if len(data) >= season_length:
            seasonal_std = data.tail(season_length).std()
        else:
            seasonal_std = data.std()

        # Gerar datas futuras
        last_date = data.index[-1]
        future_dates = [last_date + timedelta(days=30 * (i + 1)) for i in range(periods)]

        # Intervalos de confiança
        margin = 1.96 * seasonal_std
        lower = [f - margin for f in forecasts]
        upper = [f + margin for f in forecasts]

        # Confiança baseada na estabilidade sazonal
        if len(data) >= season_length:
            recent_values = data.tail(season_length).values
            cv = seasonal_std / recent_values.mean() if recent_values.mean() != 0 else 1
            confidence = max(0, min(100, 100 * (1 - cv)))
        else:
            confidence = 50

        return ForecastResult(
            dates=future_dates,
            values=forecasts,
            lower_bound=lower,
            upper_bound=upper,
            confidence=confidence,
            method="Sazonal Ingênuo",
            metric_name="Valor"
        )

    @staticmethod
    def ensemble_forecast(data: pd.Series, periods: int = 3) -> ForecastResult:
        """
        Previsão Ensemble - combina múltiplos métodos

        Args:
            data: Série temporal de valores
            periods: Número de períodos a prever

        Returns:
            ForecastResult combinado
        """
        # Obter previsões de todos os métodos
        ma_forecast = ForecastEngine.moving_average_forecast(data, periods)
        trend_forecast = ForecastEngine.linear_trend_forecast(data, periods)
        seasonal_forecast = ForecastEngine.seasonal_naive_forecast(data, periods)

        # Combinar previsões (média ponderada)
        weights = {
            'ma': 0.3,
            'trend': 0.4,
            'seasonal': 0.3
        }

        ensemble_values = [
            weights['ma'] * ma_forecast.values[i] +
            weights['trend'] * trend_forecast.values[i] +
            weights['seasonal'] * seasonal_forecast.values[i]
            for i in range(periods)
        ]

        # Combinar intervalos (usar o mais amplo para ser conservador)
        lower = [
            min(
                ma_forecast.lower_bound[i],
                trend_forecast.lower_bound[i],
                seasonal_forecast.lower_bound[i]
            )
            for i in range(periods)
        ]

        upper = [
            max(
                ma_forecast.upper_bound[i],
                trend_forecast.upper_bound[i],
                seasonal_forecast.upper_bound[i]
            )
            for i in range(periods)
        ]

        # Média ponderada da confiança
        confidence = (
            weights['ma'] * ma_forecast.confidence +
            weights['trend'] * trend_forecast.confidence +
            weights['seasonal'] * seasonal_forecast.confidence
        )

        return ForecastResult(
            dates=ma_forecast.dates,
            values=ensemble_values,
            lower_bound=lower,
            upper_bound=upper,
            confidence=confidence,
            method="Ensemble (Combinado)",
            metric_name="Valor"
        )

    @staticmethod
    def auto_forecast(df: pd.DataFrame, date_column: str, value_column: str,
                     periods: int = 3, freq: str = 'M') -> Dict[str, ForecastResult]:
        """
        Gera previsões automáticas usando todos os métodos

        Args:
            df: DataFrame com os dados
            date_column: Nome da coluna de data
            value_column: Nome da coluna de valor
            periods: Períodos a prever
            freq: Frequência

        Returns:
            Dicionário com resultados de cada método
        """
        # Preparar série temporal
        ts_df = ForecastEngine.prepare_time_series(df, date_column, value_column, freq)

        if len(ts_df) < 3:
            return {}

        # Preparar série
        ts_df.set_index(ts_df.columns[0], inplace=True)
        data = ts_df.iloc[:, 0]

        # Gerar todas as previsões
        results = {
            'moving_average': ForecastEngine.moving_average_forecast(data, periods),
            'linear_trend': ForecastEngine.linear_trend_forecast(data, periods),
            'seasonal': ForecastEngine.seasonal_naive_forecast(data, periods),
            'ensemble': ForecastEngine.ensemble_forecast(data, periods)
        }

        # Adicionar nome da métrica
        for result in results.values():
            result.metric_name = value_column

        return results
