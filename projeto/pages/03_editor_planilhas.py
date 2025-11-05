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
    page_icon="📝",
    layout="wide"
)

def salvar_backup(df, nome_arquivo):
    """Salva backup antes de alterar arquivo"""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = "backups"
        os.makedirs(backup_dir, exist_ok=True)
        
        backup_path = os.path.join(backup_dir, f"{nome_arquivo.replace('.xlsx', '')}_{timestamp}.xlsx")
        df.to_excel(backup_path, index=False)
        return backup_path
    except:
        return None

def salvar_planilha(df, nome_arquivo):
    """Salva planilha no diretório do projeto"""
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        caminho_arquivo = os.path.join(base_dir, nome_arquivo)
        
        # Fazer backup se arquivo já existe
        if os.path.exists(caminho_arquivo):
            df_atual = pd.read_excel(caminho_arquivo)
            backup_path = salvar_backup(df_atual, nome_arquivo)
            if backup_path:
                st.info(f"📦 Backup salvo: {backup_path}")
        
        # Salvar novo arquivo
        df.to_excel(caminho_arquivo, index=False)
        return True
    except Exception as e:
        st.error(f"Erro ao salvar: {e}")
        return False

def carregar_planilha(nome_arquivo):
    """Carrega planilha existente"""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    caminho_arquivo = os.path.join(base_dir, nome_arquivo)
    
    if os.path.exists(caminho_arquivo):
        return pd.read_excel(caminho_arquivo)
    return None

st.title("📝 Editor Web de Planilhas")
st.markdown("### Edite as planilhas de referência diretamente no navegador")

# Seleção de planilha
planilha_opcoes = {
    "FUNC.xlsx": "👥 Funcionários",
    "centros_de_custo.xlsx": "🏢 Centros de Custo", 
    "categorias_nibo.xlsx": "📂 Categorias Nibo"
}

planilha_selecionada = st.selectbox(
    "Selecione a planilha para editar:",
    list(planilha_opcoes.keys()),
    format_func=lambda x: planilha_opcoes[x]
)

# Carregar dados
df = carregar_planilha(planilha_selecionada)

if df is not None:
    st.success(f"✅ Planilha carregada: {len(df)} registros")
    
    # Tabs para diferentes operações
    tab1, tab2, tab3, tab4 = st.tabs(["📝 Editar", "➕ Adicionar", "📊 Visualizar", "📋 Estrutura"])
    
    with tab1:
        st.subheader("✏️ Editar Registros Existentes")
        
        # Editor de dados
        st.info("💡 Clique duas vezes em uma célula para editá-la")
        df_editado = st.data_editor(
            df,
            use_container_width=True,
            num_rows="dynamic"  # Permite adicionar/remover linhas
        )
        
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("💾 Salvar Alterações", type="primary"):
                if salvar_planilha(df_editado, planilha_selecionada):
                    st.success("✅ Planilha salva com sucesso!")
                    st.rerun()
        
        with col2:
            if st.button("🔄 Recarregar Original"):
                st.rerun()
    
    with tab2:
        st.subheader("➕ Adicionar Novo Registro")
        
        if planilha_selecionada == "FUNC.xlsx":
            # Formulário para funcionário
            with st.form("novo_funcionario"):
                col1, col2 = st.columns(2)
                
                with col1:
                    matricula = st.number_input("Matrícula", min_value=1)
                    nome = st.text_input("Nome Completo")
                    stakeholder_id = st.text_input("Stakeholder ID", value=str(uuid.uuid4()))
                
                with col2:
                    email = st.text_input("E-mail")
                    cargo = st.text_input("Cargo")
                    status = st.selectbox("Status", ["Ativo", "Inativo"])
                
                if st.form_submit_button("➕ Adicionar Funcionário"):
                    # Verificar se matrícula já existe
                    if matricula in df['matricula'].values:
                        st.error("❌ Matrícula já existe!")
                    else:
                        novo_registro = {
                            'matricula': matricula,
                            'nome': nome,
                            'Coluna2': stakeholder_id,  # Terceira coluna com ID
                            'email': email,
                            'cargo': cargo,
                            'status': status
                        }
                        
                        # Adicionar colunas que existem no DataFrame original
                        for col in df.columns:
                            if col not in novo_registro:
                                novo_registro[col] = ""
                        
                        # Adicionar ao DataFrame
                        df_novo = pd.concat([df, pd.DataFrame([novo_registro])], ignore_index=True)
                        
                        if salvar_planilha(df_novo, planilha_selecionada):
                            st.success("✅ Funcionário adicionado com sucesso!")
                            st.rerun()
        
        elif planilha_selecionada == "centros_de_custo.xlsx":
            # Formulário para centro de custo
            with st.form("novo_centro"):
                col1, col2 = st.columns(2)
                
                with col1:
                    id_empresa = st.text_input("ID Empresa")
                    nome_centro = st.text_input("Nome do Centro")
                
                with col2:
                    id_cliente = st.text_input("ID Cliente")
                    responsavel = st.text_input("Responsável")
                
                if st.form_submit_button("➕ Adicionar Centro de Custo"):
                    novo_registro = {
                        'id empresa': id_empresa,
                        'nome': nome_centro,
                        'id cliente': id_cliente,
                        'responsavel': responsavel
                    }
                    
                    # Adicionar colunas que existem no DataFrame original
                    for col in df.columns:
                        if col not in novo_registro:
                            novo_registro[col] = ""
                    
                    df_novo = pd.concat([df, pd.DataFrame([novo_registro])], ignore_index=True)
                    
                    if salvar_planilha(df_novo, planilha_selecionada):
                        st.success("✅ Centro de custo adicionado com sucesso!")
                        st.rerun()
        
        elif planilha_selecionada == "categorias_nibo.xlsx":
            # Formulário para categoria
            with st.form("nova_categoria"):
                col1, col2 = st.columns(2)
                
                with col1:
                    id_categoria = st.text_input("ID")
                    nome_categoria = st.text_input("Nome")
                
                with col2:
                    codigo = st.text_input("Código")
                    tipo = st.selectbox("Tipo", ["Despesa", "Receita", "Provisão"])
                
                if st.form_submit_button("➕ Adicionar Categoria"):
                    novo_registro = {
                        'ID': id_categoria,
                        'Nome': nome_categoria,
                        'Codigo': codigo,
                        'Tipo': tipo
                    }
                    
                    # Adicionar colunas que existem no DataFrame original
                    for col in df.columns:
                        if col not in novo_registro:
                            novo_registro[col] = ""
                    
                    df_novo = pd.concat([df, pd.DataFrame([novo_registro])], ignore_index=True)
                    
                    if salvar_planilha(df_novo, planilha_selecionada):
                        st.success("✅ Categoria adicionada com sucesso!")
                        st.rerun()
    
    with tab3:
        st.subheader("📊 Visualização Completa")
        st.dataframe(df, use_container_width=True)
        
        # Estatísticas
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📋 Total de Registros", len(df))
        with col2:
            st.metric("📝 Colunas", len(df.columns))
        with col3:
            if 'matricula' in df.columns:
                st.metric("👥 Matrículas Únicas", df['matricula'].nunique())
            elif 'ID' in df.columns:
                st.metric("🆔 IDs Únicos", df['ID'].nunique())
    
    with tab4:
        st.subheader("📋 Estrutura da Planilha")
        
        estrutura = []
        for i, col in enumerate(df.columns):
            estrutura.append({
                "Posição": i + 1,
                "Nome da Coluna": col,
                "Tipo": str(df[col].dtype),
                "Valores Únicos": df[col].nunique(),
                "Valores Nulos": df[col].isnull().sum(),
                "Exemplo": str(df[col].iloc[0]) if len(df) > 0 else ""
            })
        
        st.dataframe(pd.DataFrame(estrutura), use_container_width=True)

else:
    st.warning(f"⚠️ Planilha '{planilha_selecionada}' não encontrada")
    st.info("💡 A planilha será criada quando você adicionar o primeiro registro")
    
    # Criar planilha vazia
    if st.button("📄 Criar Planilha Vazia"):
        if planilha_selecionada == "FUNC.xlsx":
            df_novo = pd.DataFrame(columns=['matricula', 'nome', 'Coluna2'])
        elif planilha_selecionada == "centros_de_custo.xlsx":
            df_novo = pd.DataFrame(columns=['id empresa', 'nome', 'id cliente'])
        elif planilha_selecionada == "categorias_nibo.xlsx":
            df_novo = pd.DataFrame(columns=['ID', 'Nome', 'Codigo', 'Tipo'])
        
        if salvar_planilha(df_novo, planilha_selecionada):
            st.success("✅ Planilha criada com sucesso!")
            st.rerun()

# Sidebar com informações
with st.sidebar:
    st.header("📝 Editor Web")
    
    st.markdown("""
    ### 🎯 Como usar:
    1. **Selecione** a planilha
    2. **Edite** diretamente na tabela
    3. **Adicione** novos registros
    4. **Salve** as alterações
    
    ### ✅ Vantagens:
    - ✓ Interface amigável
    - ✓ Validação automática
    - ✓ Backup automático
    - ✓ Não precisa Excel
    
    ### 🔧 Recursos:
    - 📝 Edição inline
    - ➕ Adicionar registros
    - 📊 Visualização
    - 📋 Análise de estrutura
    """)
    
    # Status dos backups
    if os.path.exists("backups"):
        backups = [f for f in os.listdir("backups") if f.endswith('.xlsx')]
        if backups:
            st.subheader("📦 Backups Recentes")
            for backup in sorted(backups)[-5:]:  # Últimos 5
                st.text(f"• {backup}")

st.markdown("---")
st.markdown("st.markdown("---")
st.markdown("*💡 Todas as alterações são salvas diretamente nos arquivos do projeto*")")
=======
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

>>>>>>> f03094932d26bbfc5ee440370ed9c39ab2e74eee