"""
Tabela de Serviços - Versão Refatorada
Visualização, filtros avançados e edição de serviços
"""
import streamlit as st
import pandas as pd
from datetime import datetime

from utils import (
    DataLoader, DateFilter, DataInserter, Formatting,
    ThemeManager, InsightBox, ExportButton, MetricCard, KPIRow
)
from settings import page_settings
from config import (
    get_status_options, get_categoria_options,
    get_tecnico_options, get_forma_pagamento_options,
    APP_CONFIG, COLORS
)


class ServiceTableV2:
    """Tabela de serviços refatorada com melhorias de UX"""

    def __init__(self):
        """Inicializa a aplicação"""
        page_settings("Tabela de Serviços", "📋")
        ThemeManager.inject_custom_css()

        with st.spinner("📊 Carregando dados..."):
            self.data = DataLoader().load_data()

        if self.data.empty:
            st.error("❌ Não foi possível carregar os dados.")
            st.stop()

    def render_header(self):
        """Renderiza cabeçalho da página"""
        col1, col2, col3, col4 = st.columns([3, 1, 1, 1])

        with col1:
            st.title("📋 Tabela de Serviços")
            st.markdown("*Visualize e edite os registros de serviços*")

        with col2:
            if st.button("🔄 Atualizar", use_container_width=True):
                DataLoader.clear_cache()
                st.rerun()

        with col3:
            ExportButton.render_csv_download(
                self.data,
                f"servicos_{datetime.now().strftime('%Y%m%d')}.csv"
            )

        with col4:
            if st.button("➕ Novo", use_container_width=True):
                st.switch_page("pages/Novo Serviço.py")

    def render_summary_kpis(self, df: pd.DataFrame):
        """Renderiza KPIs resumidos dos dados filtrados"""
        total_services = len(df)
        total_revenue = df["FATURAMENTO"].sum()
        total_profit = df["LUCRO LIQUIDO"].sum()
        avg_ticket = df["FATURAMENTO"].mean() if total_services > 0 else 0

        kpi_data = [
            {
                "label": "Total de Serviços",
                "value": f"{total_services:,}",
                "icon": "📊"
            },
            {
                "label": "Faturamento Total",
                "value": Formatting.format_monetary(total_revenue),
                "icon": "💰"
            },
            {
                "label": "Lucro Total",
                "value": Formatting.format_monetary(total_profit),
                "icon": "📈"
            },
            {
                "label": "Ticket Médio",
                "value": Formatting.format_monetary(avg_ticket),
                "icon": "🎯"
            },
        ]

        KPIRow.render(kpi_data)

    def render_filters(self, df: pd.DataFrame) -> dict:
        """
        Renderiza painel de filtros

        Returns:
            Dicionário com valores dos filtros
        """
        st.subheader("🔍 Filtros")

        filters = {}

        # Linha 1: Busca e Categoria
        col1, col2 = st.columns(2)
        with col1:
            filters['search'] = st.text_input(
                "🔎 Buscar",
                placeholder="Cliente, técnico, produto...",
                help="Busca em múltiplos campos"
            )
        with col2:
            filters['categoria'] = st.selectbox(
                "📦 Categoria",
                ["TODOS"] + get_categoria_options()
            )

        # Linha 2: Status e Técnico
        col1, col2 = st.columns(2)
        with col1:
            filters['status'] = st.selectbox(
                "📌 Status",
                ["TODOS"] + get_status_options()
            )
        with col2:
            filters['tecnico'] = st.selectbox(
                "👨‍🔧 Técnico",
                ["TODOS"] + get_tecnico_options()
            )

        return filters

    def apply_filters(self, df: pd.DataFrame, filters: dict) -> pd.DataFrame:
        """
        Aplica filtros ao DataFrame

        Args:
            df: DataFrame original
            filters: Dicionário com filtros

        Returns:
            DataFrame filtrado
        """
        filtered_df = df.copy()

        # Busca textual
        if filters['search']:
            search_term = filters['search'].lower()
            mask = (
                filtered_df["CLIENTE"].str.lower().str.contains(search_term, na=False) |
                filtered_df["TECNICO"].str.lower().str.contains(search_term, na=False) |
                filtered_df["CATEGORIA"].str.lower().str.contains(search_term, na=False) |
                filtered_df["PRODUTO/SERVIÇO"].str.lower().str.contains(search_term, na=False) |
                filtered_df["CONTATO"].astype(str).str.contains(search_term, na=False)
            )
            filtered_df = filtered_df[mask]

        # Filtro por categoria
        if filters['categoria'] != "TODOS":
            filtered_df = filtered_df[filtered_df["CATEGORIA"] == filters['categoria']]

        # Filtro por status
        if filters['status'] != "TODOS":
            filtered_df = filtered_df[filtered_df["STATUS"] == filters['status']]

        # Filtro por técnico
        if filters['tecnico'] != "TODOS":
            filtered_df = filtered_df[filtered_df["TECNICO"] == filters['tecnico']]

        return filtered_df

    def format_dataframe_for_display(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Formata DataFrame para exibição

        Args:
            df: DataFrame original

        Returns:
            DataFrame formatado
        """
        df_display = df.copy()

        # Converter data para string
        if df_display["DATA"].dtype != 'object':
            df_display["DATA"] = pd.to_datetime(df_display["DATA"], errors='coerce')
            df_display["DATA"] = df_display["DATA"].dt.strftime("%d/%m/%Y")

        return df_display

    def render_data_editor(self, filtered_df: pd.DataFrame) -> pd.DataFrame:
        """
        Renderiza editor de dados

        Args:
            filtered_df: DataFrame filtrado

        Returns:
            DataFrame editado
        """
        st.subheader("📊 Dados")

        # Configuração das colunas
        column_config = {
            "DATA": st.column_config.TextColumn(
                "Data",
                help="Data do serviço (DD/MM/AAAA)",
                width="small"
            ),
            "CLIENTE": st.column_config.TextColumn(
                "Cliente",
                help="Nome do cliente",
                width="medium"
            ),
            "CONTATO": st.column_config.TextColumn(
                "Contato",
                help="Telefone ou email",
                width="small"
            ),
            "STATUS": st.column_config.SelectboxColumn(
                "Status",
                help="Status atual do serviço",
                width="small",
                options=get_status_options(),
                required=True,
            ),
            "PRODUTO/SERVIÇO": st.column_config.TextColumn(
                "Produto/Serviço",
                help="Descrição do serviço",
                width="large"
            ),
            "CATEGORIA": st.column_config.SelectboxColumn(
                "Categoria",
                help="Categoria do serviço",
                width="medium",
                options=get_categoria_options(),
                required=True,
            ),
            "DESPESAS": st.column_config.NumberColumn(
                "Despesas",
                help="Custo com peças",
                format="R$ %.2f",
                width="small"
            ),
            "FATURAMENTO": st.column_config.NumberColumn(
                "Faturamento",
                help="Valor cobrado",
                format="R$ %.2f",
                width="small"
            ),
            "TECNICO": st.column_config.SelectboxColumn(
                "Técnico",
                help="Técnico responsável",
                width="small",
                options=get_tecnico_options(),
                required=True,
            ),
            "% DO TÉCNICO": st.column_config.SelectboxColumn(
                "% Técnico",
                help="Percentual de comissão",
                width="small",
                options=APP_CONFIG.technician_percentages,
                required=True,
            ),
            "LUCRO BRUTO": st.column_config.NumberColumn(
                "Lucro Bruto",
                help="Faturamento - Despesas",
                format="R$ %.2f",
                width="small",
                disabled=True
            ),
            "VALOR DO TÉCNICO": st.column_config.NumberColumn(
                "Valor Técnico",
                help="Comissão do técnico",
                format="R$ %.2f",
                width="small",
                disabled=True
            ),
            "LUCRO LIQUIDO": st.column_config.NumberColumn(
                "Lucro Líquido",
                help="Lucro após comissões",
                format="R$ %.2f",
                width="small",
                disabled=True
            ),
            "F/PAGAMENTO": st.column_config.SelectboxColumn(
                "Pagamento",
                help="Forma de pagamento",
                width="small",
                options=get_forma_pagamento_options(),
                required=True,
            ),
        }

        # Renderizar editor
        edited_df = st.data_editor(
            filtered_df,
            num_rows="fixed",
            use_container_width=True,
            column_config=column_config,
            hide_index=True,
            height=600
        )

        return edited_df

    def render_save_section(self, edited_df: pd.DataFrame, original_df: pd.DataFrame):
        """
        Renderiza seção de salvamento

        Args:
            edited_df: DataFrame editado
            original_df: DataFrame original
        """
        col1, col2, col3 = st.columns([2, 1, 1])

        with col1:
            st.caption("💾 Clique em 'Salvar Alterações' para sincronizar com o Google Sheets")

        with col2:
            if st.button("🔄 Resetar", use_container_width=True, help="Descartar alterações"):
                st.rerun()

        with col3:
            if st.button("💾 Salvar Alterações", type="primary", use_container_width=True):
                with st.spinner("Salvando alterações..."):
                    try:
                        DataInserter().update_data(edited_df, original_df)
                        st.success("✅ Dados salvos com sucesso!")
                        st.balloons()
                        DataLoader.clear_cache()
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Erro ao salvar dados: {e}")

    def render_tips(self):
        """Renderiza dicas de uso"""
        with st.expander("💡 Dicas de Uso", expanded=False):
            st.markdown("""
            ### Como usar esta tabela:

            **🔍 Busca e Filtros:**
            - Use a busca para encontrar serviços por cliente, técnico ou produto
            - Combine múltiplos filtros para refinar os resultados
            - Os filtros de data estão disponíveis na barra lateral

            **✏️ Edição:**
            - Clique em qualquer célula editável para modificar
            - Campos calculados (Lucro Bruto, Valor Técnico, Lucro Líquido) são automáticos
            - Não esqueça de clicar em "Salvar Alterações" quando terminar

            **📥 Exportação:**
            - Use o botão "Baixar CSV" no topo para exportar os dados
            - O arquivo incluirá todos os registros (não apenas os filtrados)

            **⚠️ Importante:**
            - As alterações só são salvas após clicar em "Salvar Alterações"
            - Use "Resetar" para descartar mudanças não salvas
            - A sincronização com Google Sheets pode levar alguns segundos
            """)

    def main(self):
        """Método principal"""
        # Header
        self.render_header()

        st.divider()

        # Filtro de data na sidebar
        date_filter = DateFilter(self.data, "DATA")
        filtered_by_date = date_filter.filter_by_date()

        # KPIs resumidos
        self.render_summary_kpis(filtered_by_date)

        st.divider()

        # Filtros
        filters = self.render_filters(filtered_by_date)

        # Aplicar filtros
        filtered_df = self.apply_filters(filtered_by_date, filters)

        # Mensagem de resultados
        total_results = len(filtered_df)
        if total_results == 0:
            InsightBox.render_warning(
                "Nenhum serviço encontrado com os filtros aplicados. "
                "Tente ajustar os critérios de busca."
            )
        else:
            if total_results < len(filtered_by_date):
                InsightBox.render_info(
                    f"Exibindo {total_results} de {len(filtered_by_date)} serviços "
                    f"(filtrados de {len(self.data)} no total)"
                )

        st.divider()

        # Formatar para exibição
        display_df = self.format_dataframe_for_display(filtered_df)

        # Editor de dados
        if not display_df.empty:
            edited_df = self.render_data_editor(display_df)

            st.divider()

            # Seção de salvamento
            self.render_save_section(edited_df, self.data)
        else:
            st.info("📭 Nenhum dado para exibir.")

        st.divider()

        # Dicas
        self.render_tips()


if __name__ == "__main__":
    app = ServiceTableV2()
    app.main()
