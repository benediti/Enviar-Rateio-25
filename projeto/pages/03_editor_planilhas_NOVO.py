"""
Editor Web de Planilhas
Interface Streamlit para editar planilhas diretamente no navegador
"""

import streamlit as st
import pandas as pd
import os
from datetime import datetime
import uuid

# Configuração da página
st.set_page_config(
    page_title="Editor de Planilhas", 
    page_icon="📊",
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

def criar_backup(nome_arquivo):
    """Cria backup da planilha antes de editar"""
    try:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        caminho_original = os.path.join(base_dir, nome_arquivo)
        
        if os.path.exists(caminho_original):
            backup_dir = os.path.join(base_dir, "backups")
            os.makedirs(backup_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nome_backup = f"{nome_arquivo.split('.')[0]}_backup_{timestamp}.xlsx"
            caminho_backup = os.path.join(backup_dir, nome_backup)
            
            df = pd.read_excel(caminho_original)
            df.to_excel(caminho_backup, index=False)
            
            return True
    except Exception as e:
        st.error(f"Erro ao criar backup: {e}")
        return False

st.markdown("""
# 📊 Editor de Planilhas
### Edite as planilhas de referência diretamente no navegador
---
""")

# Sidebar com informações
with st.sidebar:
    st.header("📁 Planilhas Disponíveis")
    
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    planilhas_disponiveis = [
        "FUNC.xlsx",
        "centros_de_custo.xlsx", 
        "categorias_nibo.xlsx"
    ]
    
    # Status das planilhas
    for planilha in planilhas_disponiveis:
        caminho = os.path.join(base_dir, planilha)
        if os.path.exists(caminho):
            st.success(f"✅ {planilha}")
        else:
            st.error(f"❌ {planilha}")

# Seleção da planilha
planilha_selecionada = st.selectbox(
    "Selecione a planilha para editar:",
    planilhas_disponiveis,
    help="Escolha qual planilha você deseja editar"
)

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
caminho_planilha = os.path.join(base_dir, planilha_selecionada)

if os.path.exists(caminho_planilha):
    # Criar backup antes de editar
    if st.button("🔄 Criar Backup"):
        if criar_backup(planilha_selecionada):
            st.success("✅ Backup criado com sucesso!")
    
    # Carregar dados
    try:
        df = pd.read_excel(caminho_planilha)
        
        st.subheader(f"📊 Editando: {planilha_selecionada}")
        st.info(f"Registros: {len(df)} | Colunas: {len(df.columns)}")
        
        # Duas abas: Visualizar/Editar e Adicionar
        tab1, tab2 = st.tabs(["👁️ Visualizar/Editar", "➕ Adicionar Registro"])
        
        with tab1:
            st.markdown("### 📝 Edição Inline")
            st.info("💡 Dica: Clique duas vezes em uma célula para editá-la")
            
            # Configurar colunas apropriadamente baseado no tipo
            column_config = {}
            for col in df.columns:
                if df[col].dtype in ['int64', 'int32']:
                    column_config[col] = st.column_config.NumberColumn(
                        col,
                        format="%d",
                        min_value=0
                    )
                elif df[col].dtype in ['float64', 'float32']:
                    column_config[col] = st.column_config.NumberColumn(
                        col,
                        format="%.2f"
                    )
                else:
                    column_config[col] = st.column_config.TextColumn(col)
            
            # Editor de dados
            df_editado = st.data_editor(
                df,
                use_container_width=True,
                num_rows="dynamic",
                column_config=column_config,
                key="editor_planilhas"
            )
            
            # Botões de ação
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("💾 Salvar Alterações", type="primary"):
                    if salvar_planilha(df_editado, planilha_selecionada):
                        st.success("✅ Planilha salva com sucesso!")
                        st.rerun()
            
            with col2:
                if st.button("🔄 Recarregar"):
                    st.rerun()
            
            with col3:
                if st.button("📊 Estatísticas"):
                    with st.expander("📈 Análise dos Dados", expanded=True):
                        col_a, col_b = st.columns(2)
                        with col_a:
                            st.metric("Total de Registros", len(df_editado))
                            st.metric("Total de Colunas", len(df_editado.columns))
                        with col_b:
                            for col in df_editado.columns:
                                if df_editado[col].dtype in ['int64', 'float64']:
                                    st.metric(f"Valores únicos - {col}", df_editado[col].nunique())
        
        with tab2:
            st.markdown("### ➕ Adicionar Novo Registro")
            
            if planilha_selecionada == "FUNC.xlsx":
                with st.form("adicionar_funcionario"):
                    st.subheader("👤 Novo Funcionário")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        matricula = st.number_input("Matrícula:", min_value=1, step=1)
                        nome = st.text_input("Nome:")
                    with col2:
                        email = st.text_input("Email:")
                        cargo = st.text_input("Cargo:")
                    
                    if st.form_submit_button("➕ Adicionar Funcionário", type="primary"):
                        if matricula and nome:
                            # Verificar se matrícula já existe
                            if matricula in df['matricula'].values:
                                st.error("❌ Matrícula já existe!")
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
                                    st.success("✅ Funcionário adicionado com sucesso!")
                                    st.rerun()
                        else:
                            st.error("❌ Matrícula e Nome são obrigatórios!")
            
            elif planilha_selecionada == "centros_de_custo.xlsx":
                with st.form("adicionar_centro_custo"):
                    st.subheader("🏢 Novo Centro de Custo")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        id_empresa = st.number_input("ID Empresa:", min_value=1, step=1)
                        nome_centro = st.text_input("Nome do Centro:")
                    with col2:
                        id_cliente = st.text_input("ID Cliente:")
                        descricao = st.text_area("Descrição:")
                    
                    if st.form_submit_button("➕ Adicionar Centro", type="primary"):
                        if id_empresa and nome_centro and id_cliente:
                            novo_registro = {
                                'id empresa': id_empresa,
                                'nome': nome_centro,
                                'id cliente': id_cliente,
                                'descricao': descricao
                            }
                            
                            df_novo = pd.concat([df, pd.DataFrame([novo_registro])], ignore_index=True)
                            
                            if salvar_planilha(df_novo, planilha_selecionada):
                                st.success("✅ Centro de custo adicionado!")
                                st.rerun()
                        else:
                            st.error("❌ Todos os campos obrigatórios devem ser preenchidos!")
            
            elif planilha_selecionada == "categorias_nibo.xlsx":
                with st.form("adicionar_categoria"):
                    st.subheader("🏷️ Nova Categoria")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        codigo = st.text_input("Código:")
                        nome_categoria = st.text_input("Nome:")
                    with col2:
                        tipo = st.selectbox("Tipo:", ["Receita", "Despesa", "Outro"])
                        ativo = st.checkbox("Ativo", value=True)
                    
                    if st.form_submit_button("➕ Adicionar Categoria", type="primary"):
                        if codigo and nome_categoria:
                            novo_registro = {
                                'codigo': codigo,
                                'nome': nome_categoria,
                                'tipo': tipo,
                                'ativo': ativo
                            }
                            
                            df_novo = pd.concat([df, pd.DataFrame([novo_registro])], ignore_index=True)
                            
                            if salvar_planilha(df_novo, planilha_selecionada):
                                st.success("✅ Categoria adicionada!")
                                st.rerun()
                        else:
                            st.error("❌ Código e Nome são obrigatórios!")
    
    except Exception as e:
        st.error(f"❌ Erro ao carregar planilha: {e}")

else:
    st.warning(f"⚠️ Planilha '{planilha_selecionada}' não encontrada no diretório do projeto")

# Informações de ajuda
with st.sidebar:
    st.markdown("---")
    st.header("💡 Como Usar")
    st.markdown("""
    **Edição Inline:**
    - Clique duas vezes na célula
    - Edite o valor
    - Clique em "Salvar Alterações"
    
    **Adicionar Registros:**
    - Use a aba "Adicionar Registro"
    - Preencha os campos
    - Clique em "Adicionar"
    
    **Recursos:**
    - 🔄 Backup automático
    - 📊 Visualização
    - 📋 Análise de estrutura
    """)
    
    # Status dos backups
    backup_dir = os.path.join(base_dir, "backups")
    if os.path.exists(backup_dir):
        backups = [f for f in os.listdir(backup_dir) if f.endswith('.xlsx')]
        if backups:
            st.subheader("📦 Backups Recentes")
            for backup in sorted(backups)[-5:]:  # Últimos 5
                st.text(f"• {backup}")

st.markdown("---")
st.markdown("*💡 Todas as alterações são salvas diretamente nos arquivos do projeto*")