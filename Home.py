import streamlit as st
from settings import page_settings

page_settings("Painel", "📊")

def main():

    st.title("Dados financeiros da empresa")
    st.write("Aqui você encontra informações sobre os dados financeiros da empresa.")
    st.write("Para começar, selecione uma das opções no menu à esquerda.")


    st.header("Sobre este painel")
    st.write("Este painel foi criado para ajudar a visualizar e analisar os dados financeiros da empresa. "
             "Você pode filtrar os dados por status, técnico e data, e também pode buscar por cliente ou técnico.")

    st.header("Como usar")
    st.write("Use o menu à esquerda para navegar entre as diferentes páginas do painel. "
             "Em cada página, você encontrará diferentes visualizações e informações sobre os dados.")


if __name__ == "__main__":
    main()