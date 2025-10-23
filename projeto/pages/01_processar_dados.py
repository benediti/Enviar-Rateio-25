import streamlit as st
import pandas as pd
import os

def main():
    st.set_page_config(
        page_title="Processar Dados",
        page_icon="📊",
        layout="wide"
    )
    
    st.title("📊 Processar Dados")
    st.markdown("---")
    
    st.markdown("""
    ## Upload e Processamento de Dados
    
    Faça upload dos arquivos Excel necessários para processamento:
    """)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("📋 FUNC.xlsx")
        func_file = st.file_uploader(
            "Escolha o arquivo FUNC.xlsx",
            type=['xlsx'],
            key="func"
        )
        
        if func_file is not None:
            st.success("✅ Arquivo carregado!")
            try:
                df_func = pd.read_excel(func_file)
                st.write(f"**Linhas:** {len(df_func)}")
                st.write(f"**Colunas:** {len(df_func.columns)}")
                
                with st.expander("Visualizar dados"):
                    st.dataframe(df_func.head())
                    
            except Exception as e:
                st.error(f"Erro ao ler arquivo: {e}")
    
    with col2:
        st.subheader("🏢 Centros de Custo")
        centros_file = st.file_uploader(
            "Escolha o arquivo centros_de_custo.xlsx",
            type=['xlsx'],
            key="centros"
        )
        
        if centros_file is not None:
            st.success("✅ Arquivo carregado!")
            try:
                df_centros = pd.read_excel(centros_file)
                st.write(f"**Linhas:** {len(df_centros)}")
                st.write(f"**Colunas:** {len(df_centros.columns)}")
                
                with st.expander("Visualizar dados"):
                    st.dataframe(df_centros.head())
                    
            except Exception as e:
                st.error(f"Erro ao ler arquivo: {e}")
    
    with col3:
        st.subheader("📂 Categorias Nibo")
        categorias_file = st.file_uploader(
            "Escolha o arquivo categorias_nibo.xlsx",
            type=['xlsx'],
            key="categorias"
        )
        
        if categorias_file is not None:
            st.success("✅ Arquivo carregado!")
            try:
                df_categorias = pd.read_excel(categorias_file)
                st.write(f"**Linhas:** {len(df_categorias)}")
                st.write(f"**Colunas:** {len(df_categorias.columns)}")
                
                with st.expander("Visualizar dados"):
                    st.dataframe(df_categorias.head())
                    
            except Exception as e:
                st.error(f"Erro ao ler arquivo: {e}")
    
    st.markdown("---")
    
    # Botão de processamento
    if st.button("🔄 Processar Dados", type="primary"):
        if func_file is not None and centros_file is not None and categorias_file is not None:
            with st.spinner("Processando dados..."):
                # Aqui seria implementada a lógica de processamento
                st.success("✅ Dados processados com sucesso!")
                st.balloons()
        else:
            st.error("❌ Por favor, carregue todos os arquivos necessários")
    
    st.markdown("---")
    st.info("💡 **Dica:** Após processar os dados, vá para a página 'Gerar Coleção' para criar a coleção de envio.")

if __name__ == "__main__":
    main()