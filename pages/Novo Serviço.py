"""
Novo Serviço - Versão Refatorada
Formulário inteligente para registro de serviços com validações e cálculos automáticos
"""
import streamlit as st
import pandas as pd
from datetime import datetime, date

from utils import DataInserter, Formatting, ThemeManager, InsightBox, MetricCard
from settings import page_settings
from config import (
    get_status_options, get_categoria_options,
    get_tecnico_options, get_forma_pagamento_options,
    Tecnico
)


class ServiceRegistryV2:
    """Registro de serviços refatorado com validações"""

    def __init__(self):
        """Inicializa a aplicação"""
        page_settings("Novo Serviço", "➕")
        ThemeManager.inject_custom_css()

        # Inicializar estado da sessão
        if 'form_submitted' not in st.session_state:
            st.session_state.form_submitted = False

    def render_header(self):
        """Renderiza cabeçalho da página"""
        col1, col2 = st.columns([4, 1])

        with col1:
            st.title("➕ Novo Serviço")
            st.markdown("*Registre um novo serviço de forma rápida e prática*")

        with col2:
            if st.button("📋 Ver Tabela", use_container_width=True):
                st.switch_page("pages/Tabela de Serviços.py")

    def validate_form_data(self, data: dict) -> tuple[bool, list]:
        """
        Valida os dados do formulário

        Args:
            data: Dicionário com os dados do formulário

        Returns:
            Tupla (is_valid, errors)
        """
        errors = []

        # Validar campos obrigatórios
        if not data['client'] or data['client'].strip() == "":
            errors.append("❌ Nome do cliente é obrigatório")

        if not data['contact'] or data['contact'].strip() == "":
            errors.append("❌ Contato é obrigatório")

        if not data['product'] or data['product'].strip() == "":
            errors.append("❌ Descrição do produto/serviço é obrigatória")

        # Validar valores numéricos
        if data['service_value'] <= 0:
            errors.append("❌ Valor do serviço deve ser maior que zero")

        if data['part_value'] < 0:
            errors.append("❌ Despesas não podem ser negativas")

        if data['service_value'] < data['part_value']:
            errors.append("⚠️ Aviso: O valor do serviço é menor que as despesas (lucro negativo)")

        return (len(errors) == 0, errors)

    def calculate_financial_values(
        self,
        service_value: float,
        part_value: float,
        technician: str,
        technician_percentage: int
    ) -> dict:
        """
        Calcula valores financeiros

        Args:
            service_value: Valor do serviço
            part_value: Valor das peças
            technician: Nome do técnico
            technician_percentage: Percentual do técnico

        Returns:
            Dicionário com cálculos
        """
        brute_profit = service_value - part_value

        # Regras de negócio específicas
        if technician_percentage == 100 or technician == Tecnico.TIAGO.value:
            technician_value = brute_profit
            final_percentage = 100
        else:
            technician_value = brute_profit * (technician_percentage / 100)
            final_percentage = technician_percentage

        if technician == Tecnico.TIAGO.value:
            liquid_profit = brute_profit
        else:
            liquid_profit = brute_profit - technician_value

        return {
            "brute_profit": brute_profit,
            "technician_value": technician_value,
            "liquid_profit": liquid_profit,
            "final_percentage": final_percentage
        }

    def render_client_section(self) -> dict:
        """Renderiza seção de dados do cliente"""
        st.subheader("👤 Dados do Cliente")

        col1, col2, col3 = st.columns(3)

        with col1:
            client = st.text_input(
                "Nome do Cliente *",
                placeholder="Ex: João da Silva",
                help="Nome completo do cliente"
            )

        with col2:
            contact = st.text_input(
                "Contato *",
                placeholder="Ex: (99) 99999-9999",
                help="Telefone, WhatsApp ou email"
            )

        with col3:
            service_date = st.date_input(
                "Data do Serviço",
                value=date.today(),
                help="Data de registro do serviço",
                format="DD/MM/YYYY"
            )

        return {
            "client": client,
            "contact": contact,
            "date": service_date
        }

    def render_service_section(self) -> dict:
        """Renderiza seção de detalhes do serviço"""
        st.subheader("🔧 Detalhes do Serviço")

        col1, col2 = st.columns(2)

        with col1:
            category = st.selectbox(
                "Categoria *",
                get_categoria_options(),
                help="Tipo de serviço"
            )

            technician = st.selectbox(
                "Técnico Responsável *",
                get_tecnico_options(),
                help="Técnico que realizará o serviço"
            )

        with col2:
            status = st.selectbox(
                "Status *",
                get_status_options(),
                index=0,  # EM ANDAMENTO por padrão
                help="Status atual do serviço"
            )

            payment_method = st.selectbox(
                "Forma de Pagamento *",
                get_forma_pagamento_options(),
                help="Método de pagamento utilizado"
            )

        product = st.text_area(
            "Descrição do Produto/Serviço *",
            placeholder="Ex: Troca de tela iPhone 12, incluindo película protetora",
            help="Descreva detalhadamente o serviço realizado",
            height=100
        )

        return {
            "category": category,
            "status": status,
            "technician": technician,
            "payment_method": payment_method,
            "product": product
        }

    def render_financial_section(self, technician: str) -> dict:
        """Renderiza seção financeira com cálculos em tempo real"""
        st.subheader("💰 Detalhes Financeiros")

        col1, col2 = st.columns(2)

        with col1:
            part_value = st.number_input(
                "Despesas com Peças (R$)",
                min_value=0.0,
                value=0.0,
                step=10.0,
                format="%.2f",
                help="Custo total com peças e materiais"
            )

            service_value = st.number_input(
                "Valor do Serviço (R$) *",
                min_value=0.0,
                value=0.0,
                step=10.0,
                format="%.2f",
                help="Valor total cobrado do cliente"
            )

        with col2:
            technician_percentage = st.selectbox(
                "Comissão do Técnico (%)",
                [30, 50, 80, 100],
                index=1,  # 50% por padrão
                help="Percentual de comissão do técnico sobre o lucro bruto"
            )

        # Calcular valores em tempo real
        calculations = self.calculate_financial_values(
            service_value,
            part_value,
            technician,
            technician_percentage
        )

        # Exibir preview dos cálculos
        st.divider()
        st.markdown("### 📊 Resumo Financeiro")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            MetricCard.render(
                "Lucro Bruto",
                Formatting.format_monetary(calculations['brute_profit']),
                help_text="Faturamento - Despesas"
            )

        with col2:
            MetricCard.render(
                "Valor do Técnico",
                Formatting.format_monetary(calculations['technician_value']),
                help_text=f"{calculations['final_percentage']}% do lucro bruto"
            )

        with col3:
            MetricCard.render(
                "Lucro Líquido",
                Formatting.format_monetary(calculations['liquid_profit']),
                help_text="Lucro após comissões"
            )

        with col4:
            margin = (calculations['liquid_profit'] / service_value * 100) if service_value > 0 else 0
            MetricCard.render(
                "Margem",
                f"{margin:.1f}%",
                help_text="Percentual de lucro líquido"
            )

        # Alertas
        if calculations['liquid_profit'] < 0:
            InsightBox.render_error(
                "⚠️ Atenção: Este serviço está com prejuízo! "
                "O valor do serviço é menor que as despesas."
            )
        elif margin < 20:
            InsightBox.render_warning(
                f"⚠️ Margem de lucro baixa ({margin:.1f}%). "
                "Considere revisar os valores."
            )

        return {
            "part_value": part_value,
            "service_value": service_value,
            "technician_percentage": technician_percentage,
            **calculations
        }

    def prepare_data_for_insert(
        self,
        client_data: dict,
        service_data: dict,
        financial_data: dict
    ) -> pd.DataFrame:
        """
        Prepara dados para inserção

        Args:
            client_data: Dados do cliente
            service_data: Dados do serviço
            financial_data: Dados financeiros

        Returns:
            DataFrame pronto para inserção
        """
        data = {
            "DATA": [client_data['date'].strftime("%d/%m/%Y")],
            "CLIENTE": [client_data['client']],
            "CONTATO": [client_data['contact']],
            "STATUS": [service_data['status']],
            "PRODUTO/SERVIÇO": [service_data['product']],
            "CATEGORIA": [service_data['category']],
            "DESPESAS": [financial_data['part_value']],
            "FATURAMENTO": [financial_data['service_value']],
            "TECNICO": [service_data['technician']],
            "% DO TÉCNICO": [financial_data['final_percentage'] / 100],
            "LUCRO BRUTO": [financial_data['brute_profit']],
            "VALOR DO TÉCNICO": [financial_data['technician_value']],
            "LUCRO LIQUIDO": [financial_data['liquid_profit']],
            "F/PAGAMENTO": [service_data['payment_method']],
        }

        return pd.DataFrame.from_dict(data)

    def render_submit_section(
        self,
        client_data: dict,
        service_data: dict,
        financial_data: dict
    ):
        """Renderiza seção de submissão do formulário"""
        st.divider()

        col1, col2, col3 = st.columns([2, 1, 1])

        with col1:
            st.caption("* Campos obrigatórios")

        with col2:
            if st.button("🔄 Limpar Formulário", use_container_width=True):
                st.rerun()

        with col3:
            if st.button("💾 Salvar Serviço", type="primary", use_container_width=True):
                # Validar dados
                form_data = {**client_data, **service_data, **financial_data}
                is_valid, errors = self.validate_form_data(form_data)

                if not is_valid:
                    for error in errors:
                        st.error(error)
                else:
                    # Preparar e inserir dados
                    with st.spinner("Salvando serviço..."):
                        try:
                            df = self.prepare_data_for_insert(
                                client_data,
                                service_data,
                                financial_data
                            )

                            DataInserter().insert_data(df)

                            st.success("✅ Serviço cadastrado com sucesso!")
                            st.balloons()

                            # Limpar cache
                            from utils import DataLoader
                            DataLoader.clear_cache()

                            # Aguardar um pouco antes de recarregar
                            import time
                            time.sleep(1)

                            st.rerun()

                        except Exception as e:
                            st.error(f"❌ Erro ao salvar serviço: {e}")

    def render_tips(self):
        """Renderiza dicas de uso"""
        with st.expander("💡 Dicas de Preenchimento", expanded=False):
            st.markdown("""
            ### Como preencher o formulário:

            **👤 Dados do Cliente:**
            - Sempre preencha o nome completo do cliente
            - Adicione um contato válido para facilitar comunicação
            - A data será preenchida automaticamente com hoje

            **🔧 Detalhes do Serviço:**
            - Escolha a categoria correta para facilitar análises
            - Descreva o serviço de forma clara e detalhada
            - Atualize o status conforme o andamento

            **💰 Detalhes Financeiros:**
            - Informe as despesas com peças de forma precisa
            - O valor do serviço deve incluir mão de obra + peças
            - A comissão é calculada automaticamente sobre o lucro bruto
            - Observe o resumo financeiro para garantir margem adequada

            **⚠️ Atenção:**
            - Campos marcados com * são obrigatórios
            - Os cálculos são atualizados em tempo real
            - Não esqueça de clicar em "Salvar Serviço" ao final
            """)

    def main(self):
        """Método principal"""
        # Header
        self.render_header()

        st.divider()

        # Formulário
        client_data = self.render_client_section()

        st.divider()

        service_data = self.render_service_section()

        st.divider()

        financial_data = self.render_financial_section(service_data['technician'])

        # Submit
        self.render_submit_section(client_data, service_data, financial_data)

        st.divider()

        # Dicas
        self.render_tips()


if __name__ == "__main__":
    app = ServiceRegistryV2()
    app.main()
