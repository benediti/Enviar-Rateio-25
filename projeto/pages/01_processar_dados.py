import streamlit as st
import pandas as pd
import os
import uuid
from datetime import datetime
from io import BytesIO
import sys

# Adicionar diretório raiz ao path para imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config_segura import ConfigSegura

# ========================================
# CONFIGURAÇÃO DA PÁGINA
# ========================================
st.set_page_config(
    page_title="NIBO - Processar Dados",
    page_icon="�",
    layout="wide"
)

# ========================================
# FUNÇÕES AUXILIARES
# ========================================
def gerar_id_unico():
    return str(uuid.uuid4())

def converter_valor_americano(valor):
    if pd.isna(valor):
        return 0.0
    try:
        if isinstance(valor, str):
            valor = valor.replace(',', '.')
        return float(valor)
    except:
        return 0.0

def buscar_stakeholder_id(matricula, df_stakeholders):
    if df_stakeholders is not None and 'matricula' in df_stakeholders.columns:
        try:
            if isinstance(matricula, str):
                matricula = int(matricula.replace('.', '').replace(',', '').replace(' ', ''))
            else:
                matricula = int(matricula)
        except:
            pass
        
        resultado = df_stakeholders[df_stakeholders['matricula'] == matricula]
        if not resultado.empty:
            # A terceira coluna (índice 2) contém o ID do stakeholder
            if len(df_stakeholders.columns) >= 3:
                return resultado.iloc[0, 2]  # Coluna2 com os IDs
    return None

def buscar_cost_center_id(idsetor, df_cost_centers):
    if df_cost_centers is not None and 'id empresa' in df_cost_centers.columns and 'id cliente' in df_cost_centers.columns:
        resultado = df_cost_centers[df_cost_centers['id empresa'] == idsetor]
        if not resultado.empty:
            return resultado['id cliente'].iloc[0]
    return None

def verificar_ja_processado(df):
    if 'jafoiprocessado' in df.columns:
        processados = df['jafoiprocessado'] == True
        return df, processados.sum()
    else:
        df['jafoiprocessado'] = False
        return df, 0

# ========================================
# INTERFACE PRINCIPAL
# ========================================

st.markdown("""
# 📤 Etapa 1: Processar Planilha
### Transforme sua planilha de benefícios em dados prontos para a API NIBO
---
""")

# ========================================
# SIDEBAR - CONFIGURAÇÕES
# ========================================
config_segura = ConfigSegura()

with st.sidebar:
    st.header("⚙️ Configurações")
    
    # API Configuration (opcional nesta etapa)
    with st.expander("🔑 API NIBO (Opcional)", expanded=False):
        st.info("💡 A configuração da API é opcional nesta etapa. Será necessária na Etapa 2.")
        
        perfis_salvos = config_segura.listar_perfis()
        
        perfil_selecionado = ""
        if perfis_salvos:
            perfil_selecionado = st.selectbox("Perfil salvo:", [""] + perfis_salvos)
        
        if perfil_selecionado:
            api_url_salva, api_token_salvo = config_segura.carregar_config(perfil_selecionado)
            api_url = api_url_salva or ""
            api_token = api_token_salvo or ""
            st.success(f"✅ Perfil '{perfil_selecionado}' carregado")
        else:
            api_url, api_token = config_segura.carregar_config("default")
            api_url = api_url or ""
            api_token = api_token or ""
        
        api_url_input = st.text_input("URL da API:", value=api_url, placeholder="https://api.nibo.com.br/empresas/v1/")
        api_token_input = st.text_input("Token:", value=api_token, type="password")
        
        col1, col2 = st.columns(2)
        with col1:
            nome_perfil = st.text_input("Nome perfil:", value="default")
        with col2:
            if st.button("� Salvar"):
                if api_url_input and api_token_input and nome_perfil:
                    if config_segura.salvar_config(api_url_input, api_token_input, nome_perfil):
                        st.success("✅ Salvo!")
                        st.rerun()
    
    # Status dos arquivos
    st.header("📁 Arquivos de Referência")
    arquivos_ref = {
        "FUNC.xlsx": "Funcionários", 
        "centros_de_custo.xlsx": "Centros de Custo", 
        "categorias_nibo.xlsx": "Categorias"
    }
    
    # Diretório base para procurar os arquivos
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    for arquivo, desc in arquivos_ref.items():
        caminho_arquivo = os.path.join(base_dir, arquivo)
        if os.path.exists(caminho_arquivo):
            st.success(f"✅ {desc}")
        else:
            st.error(f"❌ {desc}")

# ========================================
# ÁREA PRINCIPAL
# ========================================

# Upload de arquivo
st.header("📤 Upload da Planilha")
uploaded_file = st.file_uploader(
    "Selecione: Modelo Planilha Imprt Beneficios.xlsx",
    type=['xlsx', 'xls'],
    help="Arquivo deve conter: matricula, idsetor, valor"
)

if uploaded_file is not None:
    try:
        # Ler arquivo
        df_input = pd.read_excel(uploaded_file)
        df_input.columns = df_input.columns.str.lower()
        
        st.success(f"✅ Arquivo carregado: {uploaded_file.name}")
        
        # Verificar colunas
        required_columns = ['matricula', 'idsetor', 'valor']
        missing_columns = [col for col in required_columns if col not in df_input.columns]
        
        if missing_columns:
            st.error(f"❌ Colunas faltando: {missing_columns}")
        else:
            # Preview
            with st.expander("👁️ Visualizar dados", expanded=False):
                st.dataframe(df_input.head(10))
            
            # Estatísticas básicas
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("📊 Total de Registros", len(df_input))
            with col2:
                st.metric("💰 Valor Total", f"R$ {df_input['valor'].sum():,.2f}")
            with col3:
                st.metric("👥 Matrículas Únicas", df_input['matricula'].nunique())
            
            # ========================================
            # CONFIGURAÇÃO DOS CAMPOS
            # ========================================
            st.markdown("---")
            st.header("📋 Configuração dos Dados")
            
            with st.form("config_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("🏷️ Categoria")
                    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                    categorias_file = os.path.join(base_dir, "categorias_nibo.xlsx")
                    
                    if os.path.exists(categorias_file):
                        df_cat = pd.read_excel(categorias_file)
                        # Usar as colunas corretas: 'Nome' e 'ID'
                        if 'Nome' in df_cat.columns:
                            categorias = df_cat['Nome'].tolist()
                            categoria_selecionada = st.selectbox("Categoria:", categorias)
                            if categoria_selecionada and 'ID' in df_cat.columns:
                                category_id = df_cat[df_cat['Nome'] == categoria_selecionada]['ID'].iloc[0]
                            else:
                                category_id = st.text_input("Category ID:")
                        else:
                            categoria_selecionada = st.text_input("Nome da categoria:")
                            category_id = st.text_input("Category ID:")
                    else:
                        categoria_selecionada = st.text_input("Nome da categoria:")
                        category_id = st.text_input("Category ID:")
                    
                    st.subheader("📝 Detalhes")
                    description = st.text_area("Descrição:", value="Benefício processado automaticamente")
                    reference = st.text_input("Referência:", value="PROC")
                
                with col2:
                    st.subheader("📅 Datas")
                    schedule_date = st.date_input("Agendamento:", value=datetime.now().date())
                    due_date = st.date_input("Vencimento:", value=datetime.now().date())
                    accrual_date = st.date_input("Competência:", value=datetime.now().date())
                
                processar_clicked = st.form_submit_button("📄 Processar Dados", type="primary", use_container_width=True)
            
            # ========================================
            # PROCESSAMENTO
            # ========================================
            if processar_clicked:
                with st.spinner("🔄 Processando dados..."):
                    # Carregar arquivos de referência
                    df_stakeholders = None
                    df_cost_centers = None
                    
                    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                    func_file = os.path.join(base_dir, "FUNC.xlsx")
                    centros_file = os.path.join(base_dir, "centros_de_custo.xlsx")
                    
                    if os.path.exists(func_file):
                        df_stakeholders = pd.read_excel(func_file)
                        if 'matricula' in df_stakeholders.columns:
                            def _norm_matricula_func(x):
                                if pd.isna(x):
                                    return None
                                try:
                                    s = str(x).replace('.', '').replace(',', '').replace(' ', '')
                                    return int(s) if s.isdigit() else None
                                except:
                                    return None
                            df_stakeholders['matricula'] = df_stakeholders['matricula'].apply(_norm_matricula_func)
                    
                    if os.path.exists(centros_file):
                        df_cost_centers = pd.read_excel(centros_file)
                        df_cost_centers.columns = df_cost_centers.columns.str.lower()
                    
                    # Processar dados
                    df_resultado = df_input.copy()
                    
                    # Normalizar matrícula
                    def normalizar_matricula(x):
                        if pd.isna(x):
                            return ''
                        s = str(x).strip().replace('.', '').replace(',', '').replace(' ', '')
                        try:
                            if s == '':
                                return ''
                            if s.isdigit():
                                return int(s)
                            return int(float(s))
                        except:
                            return s
                    
                    df_resultado['matricula'] = df_resultado['matricula'].apply(normalizar_matricula)
                    df_resultado, ja_processados = verificar_ja_processado(df_resultado)
                    
                    # Gerar campos
                    df_resultado['id'] = [gerar_id_unico() for _ in range(len(df_resultado))]
                    df_resultado['categoryid'] = category_id
                    df_resultado['value'] = df_resultado['valor'].apply(converter_valor_americano)
                    df_resultado['date'] = str(schedule_date)
                    df_resultado['vencimento'] = str(due_date)
                    df_resultado['data_competencia'] = str(accrual_date)
                    df_resultado['description'] = description
                    df_resultado['reference'] = reference
                    
                    # Buscar IDs
                    df_resultado['stakeholderid'] = df_resultado['matricula'].apply(
                        lambda x: buscar_stakeholder_id(x, df_stakeholders)
                    )
                    df_resultado['costcenterid'] = df_resultado['idsetor'].apply(
                        lambda x: buscar_cost_center_id(x, df_cost_centers)
                    )
                    
                    # Validar
                    invalidos = df_resultado[
                        (df_resultado['stakeholderid'].isna()) | 
                        (df_resultado['costcenterid'].isna()) |
                        (df_resultado['value'] <= 0)
                    ]
                    
                    if not invalidos.empty:
                        st.error(f"❌ {len(invalidos)} registros inválidos encontrados!")
                        with st.expander("Ver registros problemáticos"):
                            invalidos_display = invalidos[['matricula', 'idsetor', 'stakeholderid', 'costcenterid', 'value']].copy()
                            st.dataframe(invalidos_display)
                        
                        if not st.checkbox("Continuar mesmo assim (ignorar inválidos)"):
                            st.stop()
                        else:
                            df_resultado = df_resultado[
                                (~df_resultado['stakeholderid'].isna()) & 
                                (~df_resultado['costcenterid'].isna()) &
                                (df_resultado['value'] > 0)
                            ]
                    
                    st.success("✅ Dados processados com sucesso!")
                    
                    # Determinar registros para processar
                    if ja_processados > 0:
                        st.warning(f"⚠️ {ja_processados} registros já processados")
                        apenas_novos = st.checkbox("Processar apenas novos", value=True)
                        if apenas_novos:
                            registros_para_processar = df_resultado[df_resultado['jafoiprocessado'] == False]
                        else:
                            registros_para_processar = df_resultado
                            df_resultado['jafoiprocessado'] = False
                    else:
                        registros_para_processar = df_resultado
                    
                    st.info(f"📊 {len(registros_para_processar)} registros prontos")
                    
                    # Salvar resultado em session_state
                    st.session_state['df_processado'] = df_resultado
                    st.session_state['registros_novos'] = registros_para_processar
                    
                    # ========================================
                    # ÁREA DE DOWNLOADS
                    # ========================================
                    st.markdown("---")
                    st.header("📥 Downloads - Dados Processados")
                    st.info("💡 **Importante:** Baixe o arquivo 'Dados Prontos para Postman' para usar na Etapa 2")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # Excel completo
                        try:
                            output = BytesIO()
                            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                                df_resultado.to_excel(writer, index=False)
                            st.download_button(
                                "📊 Excel Completo",
                                data=output.getvalue(),
                                file_name="dados_processados_completo.xlsx",
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                use_container_width=True,
                                help="Todos os registros processados"
                            )
                        except Exception as e:
                            st.error(f"❌ Erro ao gerar Excel: {str(e)}")
                    
                    with col2:
                        # Apenas novos - ARQUIVO PRINCIPAL PARA ETAPA 2
                        if len(registros_para_processar) > 0:
                            output_novos = BytesIO()
                            
                            # Preparar dados para salvar
                            df_para_salvar = registros_para_processar.copy()
                            
                            # Renomear colunas para formato esperado pela Etapa 2
                            df_para_salvar = df_para_salvar.rename(columns={
                                'stakeholderid': 'stakeholderId',
                                'costcenterid': 'costCenterId',
                                'categoryid': 'categoryId',
                                'vencimento': 'Vencimento'
                            })
                            
                            with pd.ExcelWriter(output_novos, engine='openpyxl') as writer:
                                df_para_salvar.to_excel(writer, index=False)
                            
                            st.download_button(
                                "📋 Dados Prontos para Postman ⭐",
                                data=output_novos.getvalue(),
                                file_name="dados_prontos_postman.xlsx",
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                use_container_width=True,
                                type="primary",
                                help="👉 Use este arquivo na Etapa 2 para gerar a coleção Postman"
                            )
                            
                            st.success(f"✅ {len(registros_para_processar)} registros prontos para Postman!")
                    
                    # Próximos passos
                    st.markdown("---")
                    st.markdown("### 🎯 Próximos Passos")
                    st.info("""
                    1. ✅ **Baixe** o arquivo "Dados Prontos para Postman"
                    2. 👉 **Vá para** "2️⃣ Gerar Coleção Postman" no menu lateral
                    3. 📤 **Faça upload** do arquivo baixado
                    4. 🚀 **Gere** sua coleção Postman
                    """)

    except Exception as e:
        st.error(f"❌ Erro ao processar arquivo: {str(e)}")

else:
    # Instruções quando não há arquivo
    st.info("📁 Faça upload da planilha para começar")
    
    with st.expander("📋 Instruções de Uso", expanded=True):
        st.markdown("""
        ### 🎯 Objetivo desta Etapa:
        Processar a planilha de benefícios e buscar automaticamente os IDs necessários.
        
        ### � Passo a Passo:
        1. **Prepare os arquivos de referência** (já devem estar na pasta do projeto):
           - `FUNC.xlsx` - Matrículas → StakeholderIDs
           - `centros_de_custo.xlsx` - Setores → CostCenterIDs
           - `categorias_nibo.xlsx` - Nomes → CategoryIDs
        
        2. **Faça upload** da planilha modelo com os benefícios
        
        3. **Configure**:
           - Categoria (será aplicada a todos os registros)
           - Datas (agendamento, vencimento, competência)
           - Descrição e referência
        
        4. **Clique em "Processar Dados"**
        
        5. **Baixe** o arquivo "Dados Prontos para Postman"
        
        6. **Vá para a Etapa 2** no menu lateral
        
        ### ✅ O que será feito automaticamente:
        - ✓ Busca de StakeholderID usando matrícula
        - ✓ Busca de CostCenterID usando setor
        - ✓ Validação de dados
        - ✓ Normalização de valores
        - ✓ Controle de duplicação
        """)

# Footer
st.markdown("---")
st.markdown("*📤 Etapa 1 de 2 - Processamento de Dados*")