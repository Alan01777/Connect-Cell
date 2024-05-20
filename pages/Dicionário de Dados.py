import streamlit as st
from settings import page_settings


class DataDictionaryPage:
    def __init__(self):
        self.data_dictionary = {
            "DATA": {
                "type": "date",
                "description": "Data da transação",
                "format": "DD/MM/AAAA",
                "example": "02/06/2023",
                "details": "Esta coluna representa a data em que a transação ocorreu. O formato da data é dia/mês/ano.",
            },
            "CLIENTE": {
                "type": "string",
                "description": "Nome do cliente",
                "example": "João da Silva",
                "details": "Esta coluna contém o nome do cliente associado à transação.",
            },
            "CONTATO": {
                "type": "string",
                "description": "Informações de contato do cliente",
                "example": "99984256978",
                "details": "Esta coluna contém as informações de contato do cliente, como número de telefone ou e-mail.",
            },
            "STATUS": {
                "type": "string",
                "description": "Status da transação",
                "example": "concluído",
                "details": "Esta coluna indica o status atual da transação, podendo ser 'Em andamento', 'Concluído', 'Cancelado', entre outros.",
            },
            "PRODUTO/SERVIÇO": {
                "type": "string",
                "description": "Nome do produto ou serviço",
                "example": "troca de tela iphone X",
                "details": "Esta coluna contém o nome do produto ou serviço associado à transação.",
            },
            "CATEGORIA": {
                "type": "string",
                "description": "Categoria do produto ou serviço",
                "example": "REPARO HARDWARE",
                "details": "Esta coluna indica a categoria do produto ou serviço, como 'REPARO HARDWARE', 'REPARO SOFTWARE', 'VENDA DE PEÇAS', etc.",
            },
            "(R$)PEÇA": {
                "type": "float",
                "description": "Valor em reais de cada peça",
                "format": "R$0,00",
                "example": "200",
                "details": "Esta coluna indica o valor em reais das peças utilizadas no serviço.",
            },
            "VALOR TOTAL DO SERVIÇO": {
                "type": "float",
                "description": "Valor total do serviço",
                "format": "R$0,00",
                "example": "450",
                "details": "Esta coluna representa o valor total do serviço prestado (não inclui o preço de peças).",
            },
            "TECNICO": {
                "type": "string",
                "description": "Nome do técnico responsável",
                "example": "TIAGO",
                "details": "Esta coluna contém o nome do técnico responsável pela realização do serviço.",
            },
            "% DO TÉCNICO": {
                "type": "float",
                "description": "Percentual de comissão do técnico",
                "format": "0.00%",
                "example": "30",
                "details": "Esta coluna indica o percentual de comissão que o técnico recebe sobre o lucro do serviço.",
            },
            "LUCRO BRUTO": {
                "type": "float",
                "description": "Lucro obtido com o serviço",
                "format": "R$0,00",
                "example": "250",
                "details": "Esta coluna representa o lucro obtido com a realização do serviço, calculado como 'Valor Total do Serviço - Valor das Peças'.",
            },
            "VALOR DO TÉCNICO": {
                "type": "float",
                "description": "Valor recebido pelo técnico",
                "format": "R$0,00",
                "example": "150",
                "details": "Esta coluna indica o valor que o técnico recebe pelo serviço, calculado como 'Percentual do Técnico * Lucro'.",
            },
            "LUCRO LIQUIDO": {
                "type": "float",
                "description": "Lucro final obtido",
                "format": "R$0,00",
                "example": "150",
                "details": "Esta coluna representa o lucro final para a assitência, obtido após o técnico receber sua comissão, calculado como 'Lucro - Valor do Técnico'.",
            },
            "F/PAGAMENTO": {
                "type": "string",
                "description": "Forma de pagamento",
                "example": "PIX",
                "details": "Esta coluna indica a forma de pagamento utilizada para realizar a transação, como 'DINHEIRO', 'DÉBITO', 'CRÉDITO', 'PIX', 'OUTRO', etc.",
            },
        }

    def display_page(self):
        st.title("Dicionário de Dados")
        for column_name, column_info in self.data_dictionary.items():
            st.subheader(f"Coluna: {column_name}")
            st.markdown(f"- Tipo de Dados: {column_info['type']}")
            st.markdown(f"- Descrição: {column_info['description']}")
            st.markdown(f"- Detalhes: {column_info['details']}")
            if "format" in column_info:
                st.markdown(f"- Formato: {column_info['format']}")
            st.markdown(f"- Exemplo: {column_info['example']}")


def main():
    page_settings("Dicionário de Dados", "📊")
    data_dictionary_page = DataDictionaryPage()
    data_dictionary_page.display_page()


if __name__ == "__main__":
    main()
