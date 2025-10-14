"""
Componentes reutilizáveis para o dashboard
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from typing import Optional, Dict, Any, List
from streamlit_extras.stylable_container import stylable_container
from utils.ThemeManager import ThemeManager
from config import COLORS, CHART_CONFIG


class MetricCard:
    """Card de métrica com estilo consistente"""

    @staticmethod
    def render(
        label: str,
        value: Any,
        delta: Optional[str] = None,
        delta_color: str = "normal",
        help_text: Optional[str] = None,
        icon: Optional[str] = None
    ):
        """Renderiza um card de métrica estilizado"""
        with stylable_container(
            key=f"metric_{label}",
            css_styles=ThemeManager.get_metric_card_style()
        ):
            if icon:
                st.markdown(f"### {icon} {label}")
            st.metric(
                label="" if icon else label,
                value=value,
                delta=delta,
                delta_color=delta_color,
                help=help_text
            )


class ChartContainer:
    """Container para gráficos com estilo consistente"""

    @staticmethod
    def render(title: str, chart_func, caption: Optional[str] = None, key: Optional[str] = None):
        """Renderiza um container de gráfico estilizado"""
        container_key = key or f"chart_{title.replace(' ', '_')}"

        with stylable_container(
            key=container_key,
            css_styles=ThemeManager.get_chart_container_style()
        ):
            st.header(title)
            chart_func()
            if caption:
                st.caption(caption)


class InsightBox:
    """Caixa de insight/alerta"""

    @staticmethod
    def render_info(message: str, icon: str = "ℹ️"):
        """Renderiza uma caixa de informação"""
        with stylable_container(
            key=f"info_{hash(message)}",
            css_styles=ThemeManager.get_info_box_style()
        ):
            st.markdown(f"{icon} {message}")

    @staticmethod
    def render_warning(message: str, icon: str = "⚠️"):
        """Renderiza uma caixa de aviso"""
        with stylable_container(
            key=f"warning_{hash(message)}",
            css_styles=ThemeManager.get_warning_box_style()
        ):
            st.markdown(f"{icon} {message}")

    @staticmethod
    def render_success(message: str, icon: str = "✅"):
        """Renderiza uma caixa de sucesso"""
        with stylable_container(
            key=f"success_{hash(message)}",
            css_styles=ThemeManager.get_success_box_style()
        ):
            st.markdown(f"{icon} {message}")

    @staticmethod
    def render_error(message: str, icon: str = "❌"):
        """Renderiza uma caixa de erro"""
        with stylable_container(
            key=f"error_{hash(message)}",
            css_styles=ThemeManager.get_error_box_style()
        ):
            st.markdown(f"{icon} {message}")


class LoadingSpinner:
    """Componente de loading"""

    @staticmethod
    def show(message: str = "Carregando dados..."):
        """Mostra um spinner de loading"""
        return st.spinner(message)


class DataTable:
    """Tabela de dados estilizada"""

    @staticmethod
    def render(
        df: pd.DataFrame,
        title: Optional[str] = None,
        height: Optional[int] = None,
        use_container_width: bool = True
    ):
        """Renderiza uma tabela de dados"""
        if title:
            st.subheader(title)

        st.dataframe(
            df,
            height=height,
            use_container_width=use_container_width
        )


class KPIRow:
    """Linha de KPIs"""

    @staticmethod
    def render(kpis: List[Dict[str, Any]]):
        """
        Renderiza uma linha de KPIs

        Args:
            kpis: Lista de dicionários com as chaves:
                - label: str
                - value: Any
                - delta: Optional[str]
                - icon: Optional[str]
        """
        cols = st.columns(len(kpis))

        for col, kpi in zip(cols, kpis):
            with col:
                MetricCard.render(
                    label=kpi.get("label", ""),
                    value=kpi.get("value", ""),
                    delta=kpi.get("delta"),
                    icon=kpi.get("icon")
                )


class ComparisonChart:
    """Gráfico de comparação com sparkline"""

    @staticmethod
    def render_sparkline(
        data: List[float],
        color: str = COLORS.blue,
        height: int = 50
    ) -> go.Figure:
        """Cria um mini gráfico sparkline"""
        fig = go.Figure()

        fig.add_trace(go.Scatter(
            y=data,
            mode='lines',
            line=dict(color=color, width=2),
            fill='tozeroy',
            fillcolor=f'rgba({int(color[1:3], 16)}, {int(color[3:5], 16)}, {int(color[5:7], 16)}, 0.2)'
        ))

        fig.update_layout(
            showlegend=False,
            height=height,
            margin=dict(l=0, r=0, t=0, b=0),
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            hovermode=False
        )

        return fig


class FilterPanel:
    """Painel de filtros reutilizável"""

    @staticmethod
    def render_search_and_filters(
        df: pd.DataFrame,
        search_columns: List[str],
        filter_columns: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        Renderiza painel de busca e filtros

        Args:
            df: DataFrame para filtrar
            search_columns: Lista de colunas para busca textual
            filter_columns: Dicionário {nome_coluna: label_display}

        Returns:
            Dicionário com valores dos filtros
        """
        filters = {}

        # Busca textual
        col1, col2 = st.columns(2)
        with col1:
            filters['search'] = st.text_input(
                "🔍 Buscar",
                placeholder="Digite para buscar..."
            )

        # Filtros por coluna
        filter_cols = st.columns(len(filter_columns))
        for idx, (col_name, label) in enumerate(filter_columns.items()):
            with filter_cols[idx]:
                unique_values = ["TODOS"] + sorted(df[col_name].unique().tolist())
                filters[col_name] = st.selectbox(
                    label,
                    unique_values
                )

        return filters


class ExportButton:
    """Botão de exportação de dados"""

    @staticmethod
    def render_csv_download(df: pd.DataFrame, filename: str = "dados.csv"):
        """Renderiza botão para download em CSV"""
        csv = df.to_csv(index=False).encode('utf-8')

        st.download_button(
            label="📥 Baixar CSV",
            data=csv,
            file_name=filename,
            mime='text/csv',
        )

    @staticmethod
    def render_excel_download(df: pd.DataFrame, filename: str = "dados.xlsx"):
        """Renderiza botão para download em Excel"""
        try:
            import io
            from openpyxl import Workbook

            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Dados')

            excel_data = output.getvalue()

            st.download_button(
                label="📥 Baixar Excel",
                data=excel_data,
                file_name=filename,
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            )
        except ImportError:
            st.warning("Instale openpyxl para exportar para Excel: pip install openpyxl")
