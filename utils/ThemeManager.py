"""
Gerenciador de temas e estilos CSS centralizados
"""
from typing import Optional


class ThemeManager:
    """Gerencia estilos CSS reutilizáveis"""

    @staticmethod
    def get_card_style(
        background: str = "#f9f9f9",
        border_color: str = "rgba(49, 51, 63, 0.2)",
        shadow: bool = True
    ) -> str:
        """Retorna CSS para um card estilizado"""
        shadow_css = "box-shadow: 0px 10px 30px -5px rgba(0, 0, 0, 0.3);" if shadow else ""

        return f"""
            {{
                border: 1px solid {border_color};
                border-radius: 0.5rem;
                padding: calc(1em - 1px);
                {shadow_css}
                background-color: {background};
            }}
        """

    @staticmethod
    def get_metric_card_style() -> str:
        """Retorna CSS específico para cards de métricas"""
        return ThemeManager.get_card_style(shadow=True)

    @staticmethod
    def get_chart_container_style() -> str:
        """Retorna CSS para containers de gráficos"""
        return ThemeManager.get_card_style(shadow=True)

    @staticmethod
    def get_info_box_style(color: str = "#e3f2fd") -> str:
        """Retorna CSS para caixas de informação"""
        return f"""
            {{
                background-color: {color};
                padding: 1rem;
                border-radius: 0.5rem;
                border-left: 4px solid #2196f3;
                margin: 1rem 0;
            }}
        """

    @staticmethod
    def get_warning_box_style() -> str:
        """Retorna CSS para caixas de aviso"""
        return """
            {
                background-color: #fff3cd;
                padding: 1rem;
                border-radius: 0.5rem;
                border-left: 4px solid #ffc107;
                margin: 1rem 0;
            }
        """

    @staticmethod
    def get_error_box_style() -> str:
        """Retorna CSS para caixas de erro"""
        return """
            {
                background-color: #f8d7da;
                padding: 1rem;
                border-radius: 0.5rem;
                border-left: 4px solid #dc3545;
                margin: 1rem 0;
            }
        """

    @staticmethod
    def get_success_box_style() -> str:
        """Retorna CSS para caixas de sucesso"""
        return """
            {
                background-color: #d4edda;
                padding: 1rem;
                border-radius: 0.5rem;
                border-left: 4px solid #28a745;
                margin: 1rem 0;
            }
        """

    @staticmethod
    def inject_custom_css():
        """Injeta CSS customizado global"""
        import streamlit as st

        st.markdown("""
            <style>
            /* Estilos globais */
            .stMetric {
                background-color: #ffffff;
                padding: 1rem;
                border-radius: 0.5rem;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }

            /* Melhorar aparência das tabs */
            .stTabs [data-baseweb="tab-list"] {
                gap: 8px;
            }

            .stTabs [data-baseweb="tab"] {
                height: 50px;
                white-space: pre-wrap;
                background-color: #f0f2f6;
                border-radius: 4px 4px 0 0;
                gap: 1px;
                padding-top: 10px;
                padding-bottom: 10px;
            }

            .stTabs [aria-selected="true"] {
                background-color: #ffffff;
            }

            /* Melhorar dataframes */
            .dataframe {
                font-size: 14px;
            }

            /* Melhorar botões */
            .stButton>button {
                width: 100%;
                border-radius: 0.5rem;
                font-weight: 500;
                transition: all 0.3s ease;
            }

            .stButton>button:hover {
                transform: translateY(-2px);
                box-shadow: 0 4px 8px rgba(0,0,0,0.2);
            }

            /* Melhorar inputs */
            .stTextInput>div>div>input {
                border-radius: 0.5rem;
            }

            .stSelectbox>div>div>div {
                border-radius: 0.5rem;
            }

            /* Otimizar padding para monitores 1080p */
            .block-container {
                padding-top: 1rem;
                padding-bottom: 1rem;
                padding-left: 2rem;
                padding-right: 2rem;
                max-width: 100%;
            }

            /* Reduzir espaçamento entre seções */
            .element-container {
                margin-bottom: 0.5rem;
            }

            /* Estilo para cards de insights */
            .insight-card {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 1.5rem;
                border-radius: 1rem;
                margin: 1rem 0;
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            }

            /* Animação suave */
            * {
                transition: all 0.2s ease;
            }

            /* Garantir que os gráficos não estourem o container */
            .js-plotly-plot,
            .plot-container,
            .plotly {
                max-width: 100% !important;
                overflow-x: hidden !important;
            }

            /* Garantir overflow correto nos containers */
            .stPlotlyChart {
                overflow-x: hidden !important;
            }

            /* Garantir que as colunas não estourem */
            [data-testid="column"] {
                overflow-x: hidden !important;
            }
            </style>
        """, unsafe_allow_html=True)
