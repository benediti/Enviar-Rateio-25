import streamlit as st

def main():
    st.set_page_config(
        page_title="Enviar Rateio",
        page_icon="💰",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("💰 Sistema de Envio de Rateio")
    st.markdown("---")
    
    st.markdown("""
    ## Bem-vindo ao Sistema de Envio de Rateio
    
    Este sistema permite:
    
    - 📊 **Processar Dados**: Importar e processar planilhas de dados
    - 📋 **Gerar Coleção**: Criar coleções para envio
    
    ### Como usar:
    1. Use a barra lateral para navegar entre as páginas
    2. Comece processando os dados na página "Processar Dados"
    3. Em seguida, gere a coleção na página "Gerar Coleção"
    
    ### Arquivos necessários:
    - `FUNC.xlsx` - Dados dos funcionários
    - `centros_de_custo.xlsx` - Centros de custo
    - `categorias_nibo.xlsx` - Categorias do Nibo
    """)
    
    st.markdown("---")
    st.info("👈 Use o menu lateral para navegar entre as páginas")

if __name__ == "__main__":
    main()