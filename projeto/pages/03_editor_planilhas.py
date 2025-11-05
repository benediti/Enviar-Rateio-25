import streamlit as st
import pandas as pd
import os
from datetime import datetime
import uuid

st.set_page_config(
    page_title="Editor de Planilhas",
    page_icon="",
    layout="wide"
)

def salvar_planilha(df, nome_arquivo):
    """Salva planilha no diretório do projeto"""
    try:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        caminho_arquivo = os.path.join(base_dir, nome_arquivo)
        df.to_excel(caminho_arquivo, index=False)
        return True
    except Exception as e:
        st.error(f"Erro ao salvar: {e}")
        return False

def carregar_planilha(nome_arquivo):
    """Carrega planilha existente"""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    caminho_arquivo = os.path.join(base_dir, nome_arquivo)
    
    if os.path.exists(caminho_arquivo):
        return pd.read_excel(caminho_arquivo)
    return None

st.title(" Editor Web de Planilhas")
st.markdown("### Edite as planilhas de referência diretamente no navegador")

planilha_opcoes = {
    "FUNC.xlsx": " Funcionários",
    "centros_de_custo.xlsx": " Centros de Custo", 
    "categorias_nibo.xlsx": " Categorias Nibo"
}

planilha_selecionada = st.selectbox(
    "Selecione a planilha para editar:",
    list(planilha_opcoes.keys()),
    format_func=lambda x: planilha_opcoes[x]
)

df = carregar_planilha(planilha_selecionada)

if df is not None:
    st.success(f" Planilha carregada: {len(df)} registros")
    
    tab1, tab2 = st.tabs([" Editar", " Adicionar"])
    
    with tab1:
        st.subheader(" Editar Registros Existentes")
        df_editado = st.data_editor(df, use_container_width=True, num_rows="dynamic")
        
        if st.button(" Salvar Alterações", type="primary"):
            if salvar_planilha(df_editado, planilha_selecionada):
                st.success(" Planilha salva com sucesso!")
                st.rerun()
    
    with tab2:
        st.subheader(" Adicionar Novo Registro")
        
        if planilha_selecionada == "FUNC.xlsx":
            with st.form("novo_funcionario"):
                matricula = st.number_input("Matrícula", min_value=1)
                nome = st.text_input("Nome Completo")
                email = st.text_input("E-mail")
                cargo = st.text_input("Cargo")
                
                if st.form_submit_button(" Adicionar Funcionário"):
                    if matricula in df['matricula'].values:
                        st.error(" Matrícula já existe!")
                    else:
                        novo_registro = {
                            'matricula': matricula,
                            'nome': nome,
                            'Coluna2': str(uuid.uuid4()),
                            'email': email,
                            'cargo': cargo
                        }
                        
                        df_novo = pd.concat([df, pd.DataFrame([novo_registro])], ignore_index=True)
                        
                        if salvar_planilha(df_novo, planilha_selecionada):
                            st.success(" Funcionário adicionado com sucesso!")
                            st.rerun()
else:
    st.warning(f" Planilha '{planilha_selecionada}' não encontrada")
