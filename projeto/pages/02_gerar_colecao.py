import streamlit as st
import pandas as pd
import json
from datetime import datetime

def main():
    st.set_page_config(
        page_title="Gerar Coleção",
        page_icon="📋",
        layout="wide"
    )
    
    st.title("📋 Gerar Coleção")
    st.markdown("---")
    
    st.markdown("""
    ## Geração de Coleção para Envio
    
    Configure os parâmetros e gere a coleção de dados para envio.
    """)
    
    # Verificar se há dados processados (simulado)
    if "dados_processados" not in st.session_state:
        st.warning("⚠️ Nenhum dado processado encontrado. Vá para a página 'Processar Dados' primeiro.")
        return
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("⚙️ Configurações da Coleção")
        
        # Parâmetros de configuração
        nome_colecao = st.text_input(
            "Nome da Coleção",
            value=f"Rateio_{datetime.now().strftime('%Y%m%d_%H%M')}"
        )
        
        descricao = st.text_area(
            "Descrição",
            value="Coleção de rateio gerada automaticamente"
        )
        
        # Filtros
        st.subheader("🔍 Filtros")
        
        filtro_periodo = st.date_input(
            "Período",
            value=datetime.now().date()
        )
        
        filtro_centro_custo = st.multiselect(
            "Centros de Custo",
            options=["CC001", "CC002", "CC003"],  # Seria carregado dos dados reais
            default=["CC001"]
        )
        
        incluir_inativos = st.checkbox("Incluir funcionários inativos")
        
    with col2:
        st.subheader("📊 Resumo")
        
        # Métricas simuladas
        col_a, col_b = st.columns(2)
        with col_a:
            st.metric("Total de Registros", "150")
            st.metric("Centros de Custo", len(filtro_centro_custo))
        
        with col_b:
            st.metric("Valor Total", "R$ 45.678,90")
            st.metric("Funcionários", "87")
    
    st.markdown("---")
    
    # Preview dos dados
    st.subheader("👀 Preview da Coleção")
    
    # Dados simulados para preview
    preview_data = {
        "ID": [1, 2, 3, 4, 5],
        "Funcionário": ["João Silva", "Maria Santos", "Pedro Costa", "Ana Lima", "Carlos Oliveira"],
        "Centro de Custo": ["CC001", "CC001", "CC002", "CC002", "CC003"],
        "Valor": ["R$ 1.250,00", "R$ 950,00", "R$ 1.800,00", "R$ 1.100,00", "R$ 2.200,00"],
        "Status": ["Ativo", "Ativo", "Ativo", "Inativo", "Ativo"]
    }
    
    df_preview = pd.DataFrame(preview_data)
    st.dataframe(df_preview, use_container_width=True)
    
    st.markdown("---")
    
    # Botões de ação
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("💾 Salvar Coleção", type="primary"):
            with st.spinner("Salvando coleção..."):
                # Aqui seria implementada a lógica de salvamento
                st.success("✅ Coleção salva com sucesso!")
    
    with col2:
        if st.button("📤 Exportar JSON"):
            # Criar dados para exportação
            export_data = {
                "nome": nome_colecao,
                "descricao": descricao,
                "data_geracao": datetime.now().isoformat(),
                "filtros": {
                    "periodo": str(filtro_periodo),
                    "centros_custo": filtro_centro_custo,
                    "incluir_inativos": incluir_inativos
                },
                "dados": preview_data
            }
            
            st.download_button(
                label="⬇️ Download JSON",
                data=json.dumps(export_data, indent=2, ensure_ascii=False),
                file_name=f"{nome_colecao}.json",
                mime="application/json"
            )
    
    with col3:
        if st.button("📧 Enviar Coleção"):
            with st.spinner("Enviando coleção..."):
                # Aqui seria implementada a lógica de envio
                st.success("✅ Coleção enviada com sucesso!")
                st.balloons()
    
    st.markdown("---")
    st.info("💡 **Dica:** Verifique sempre o preview antes de enviar a coleção.")

if __name__ == "__main__":
    main()