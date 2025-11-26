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

# Dica sobre atualização de arquivo
if 'df_processado' in st.session_state:
    st.info("💡 **Dica:** Se você editou o arquivo Excel e quer reprocessar, clique em '🔄 Limpar Cache' e faça upload novamente.")

col_upload, col_limpar = st.columns([3, 1])

with col_upload:
    uploaded_file = st.file_uploader(
        "Selecione: Modelo Planilha Imprt Beneficios.xlsx",
        type=['xlsx', 'xls'],
        help="Arquivo deve conter: matricula, idsetor, valor",
        key=f"file_uploader_{datetime.now().strftime('%Y%m%d')}"
    )

with col_limpar:
    st.write("")  # Espaçamento
    st.write("")  # Espaçamento
    if st.button("🔄 Limpar Cache", help="Limpa o cache e recarrega os dados"):
        st.cache_data.clear()
        if 'df_processado' in st.session_state:
            del st.session_state['df_processado']
        if 'registros_novos' in st.session_state:
            del st.session_state['registros_novos']
        st.success("✅ Cache limpo! Faça upload do arquivo novamente.")
        st.rerun()

if uploaded_file is not None:
    try:
        # Mostrar informações do arquivo carregado
        st.info(f"📁 **Arquivo:** {uploaded_file.name} | **Tamanho:** {uploaded_file.size / 1024:.1f} KB | **Carregado em:** {datetime.now().strftime('%H:%M:%S')}")
        
        # Ler arquivo com configurações mais específicas
        df_input = pd.read_excel(uploaded_file, engine='openpyxl')
        
        # Verificar se há múltiplas abas
        if hasattr(uploaded_file, 'name'):
            xls = pd.ExcelFile(uploaded_file)
            if len(xls.sheet_names) > 1:
                st.info(f"📋 Planilha possui {len(xls.sheet_names)} abas: {', '.join(xls.sheet_names)}")
                aba_selecionada = st.selectbox("Selecione a aba:", xls.sheet_names)
                df_input = pd.read_excel(uploaded_file, sheet_name=aba_selecionada, engine='openpyxl')
        
        # Limpar dados iniciais
        df_input = df_input.dropna(how='all')  # Remove linhas completamente vazias
        df_input = df_input.dropna(how='all', axis=1)  # Remove colunas completamente vazias
        
        # Normalizar nomes das colunas
        df_input.columns = df_input.columns.str.lower().str.strip()
        
        st.success(f"✅ Arquivo carregado: {uploaded_file.name}")
        st.info(f"📊 Dados reais encontrados: {len(df_input)} linhas, {len(df_input.columns)} colunas")
        
        # Verificar colunas
        required_columns = ['matricula', 'idsetor', 'valor']
        missing_columns = [col for col in required_columns if col not in df_input.columns]
        
        if missing_columns:
            st.error(f"❌ Colunas obrigatórias não encontradas: {missing_columns}")
            st.info("Colunas disponíveis: " + ", ".join(df_input.columns.tolist()))
            st.stop()
        
        # Limpeza automática inicial dos dados
        registros_originais = len(df_input)
        df_original_backup = df_input.copy()  # Backup para comparação
        
        # Rastrear o que foi removido em cada etapa
        indices_removidos_por_etapa = {
            'vazias': set(),
            'obrigatorios': set(),
            'duplicatas': set(),
            'conversao': set(),
            'valores_invalidos': set()
        }
        
        # 1. Remove linhas completamente vazias
        indices_antes = set(df_input.index)
        df_input = df_input.dropna(how='all')
        indices_removidos_por_etapa['vazias'] = indices_antes - set(df_input.index)
        
        # 2. Remove linhas com valores obrigatórios vazios
        indices_antes = set(df_input.index)
        df_input = df_input.dropna(subset=['matricula', 'idsetor', 'valor'])
        indices_removidos_por_etapa['obrigatorios'] = indices_antes - set(df_input.index)
        
        # 3. Remove duplicatas completas (APENAS duplicatas exatas)
        indices_antes = set(df_input.index)
        df_input = df_input.drop_duplicates(subset=['matricula', 'idsetor', 'valor'], keep='first')
        indices_removidos_por_etapa['duplicatas'] = indices_antes - set(df_input.index)
        
        # 4. Converte tipos e corrige formatação
        try:
            # Tratar valores primeiro (pode ter vírgula como separador decimal)
            if df_input['valor'].dtype == 'object':
                # Se for texto, trocar vírgula por ponto
                df_input['valor'] = df_input['valor'].astype(str).str.replace(',', '.').str.replace(r'[^\d\.]', '', regex=True)
            df_input['valor'] = pd.to_numeric(df_input['valor'], errors='coerce')
            
            # Tratar matrículas como string primeiro para remover zeros desnecessários
            df_input['matricula'] = df_input['matricula'].astype(str).str.replace(r'\.0$', '', regex=True)
            
            # Converter para inteiro (remove zeros à direita automaticamente)
            df_input['matricula'] = pd.to_numeric(df_input['matricula'], errors='coerce').astype('Int64')
            df_input['idsetor'] = pd.to_numeric(df_input['idsetor'], errors='coerce').astype('Int64')
            
            # Remove registros onde a conversão falhou
            indices_antes = set(df_input.index)
            df_input = df_input.dropna(subset=['matricula', 'idsetor', 'valor'])
            indices_removidos_por_etapa['conversao'] = indices_antes - set(df_input.index)
            
            # Remove valores <= 0
            indices_antes = set(df_input.index)
            df_input = df_input[
                (df_input['matricula'] > 0) & 
                (df_input['idsetor'] > 0) & 
                (df_input['valor'] > 0)
            ]
            indices_removidos_por_etapa['valores_invalidos'] = indices_antes - set(df_input.index)
            
            # Converter matrículas e setores para int normal (sem zeros extras)
            df_input['matricula'] = df_input['matricula'].astype(int)
            df_input['idsetor'] = df_input['idsetor'].astype(int)
            
        except Exception as e:
            st.error(f"❌ Erro na conversão de tipos: {e}")
            st.stop()
        
        registros_limpos = len(df_input)
        registros_removidos = registros_originais - registros_limpos
        
        if registros_limpos == 0:
            st.error("❌ Nenhum registro válido encontrado após limpeza!")
            st.stop()
        
        if registros_removidos > 0:
            st.success(f"🧹 Limpeza automática: {registros_removidos} registros inválidos removidos")
            
            # Mostrar detalhes dos dados removidos
            with st.expander(f"🔍 Ver detalhes dos {registros_removidos} registros removidos", expanded=False):
                # Identificar quais registros foram removidos
                indices_mantidos = df_input.index
                df_removidos = df_original_backup[~df_original_backup.index.isin(indices_mantidos)]
                
                if not df_removidos.empty:
                    st.warning(f"**{len(df_removidos)} registros foram removidos durante a limpeza:**")
                    
                    # Categorizar os problemas
                    col1, col2, col3, col4, col5 = st.columns(5)
                    
                    # Contar tipos de problemas usando os índices rastreados
                    qtd_vazias = len(indices_removidos_por_etapa['vazias'])
                    qtd_obrigatorios = len(indices_removidos_por_etapa['obrigatorios'])
                    qtd_duplicatas = len(indices_removidos_por_etapa['duplicatas'])
                    qtd_conversao = len(indices_removidos_por_etapa['conversao'])
                    qtd_valores_invalidos = len(indices_removidos_por_etapa['valores_invalidos'])
                    
                    with col1:
                        if qtd_vazias > 0:
                            st.metric("🗑️ Linhas vazias", qtd_vazias)
                    with col2:
                        if qtd_obrigatorios > 0:
                            st.metric("⚠️ Campos vazios", qtd_obrigatorios)
                    with col3:
                        if qtd_duplicatas > 0:
                            st.metric("🔁 Duplicatas", qtd_duplicatas)
                    with col4:
                        if qtd_conversao > 0:
                            st.metric("❌ Erro conversão", qtd_conversao)
                    with col5:
                        if qtd_valores_invalidos > 0:
                            st.metric("⚪ Valores ≤ 0", qtd_valores_invalidos)
                    
                    # Mostrar dados removidos em tabela
                    st.markdown("---")
                    st.markdown("**📋 Registros removidos:**")
                    
                    # Adicionar coluna indicando o motivo
                    df_removidos_display = df_removidos.copy()
                    motivos = []
                    
                    for idx in df_removidos_display.index:
                        linha = df_removidos_display.loc[idx]
                        motivo_lista = []
                        
                        # Verificar qual foi o motivo da remoção
                        if idx in indices_removidos_por_etapa['vazias']:
                            motivo_lista.append("Linha vazia")
                        if idx in indices_removidos_por_etapa['obrigatorios']:
                            if pd.isna(linha.get('matricula')):
                                motivo_lista.append("Matrícula vazia")
                            if pd.isna(linha.get('idsetor')):
                                motivo_lista.append("Setor vazio")
                            if pd.isna(linha.get('valor')):
                                motivo_lista.append("Valor vazio")
                        if idx in indices_removidos_por_etapa['duplicatas']:
                            motivo_lista.append("Duplicata")
                        if idx in indices_removidos_por_etapa['conversao']:
                            motivo_lista.append("Erro na conversão de tipo")
                        if idx in indices_removidos_por_etapa['valores_invalidos']:
                            motivo_lista.append("Valor ≤ 0")
                        
                        motivos.append(", ".join(motivo_lista) if motivo_lista else "Outro")
                    
                    df_removidos_display['Motivo'] = motivos
                    
                    # Mostrar tabela
                    st.dataframe(
                        df_removidos_display,
                        use_container_width=True,
                        height=min(400, len(df_removidos_display) * 35 + 38)
                    )
                    
                    # Opção de download
                    st.markdown("---")
                    csv_removidos = df_removidos_display.to_csv(index=False)
                    st.download_button(
                        label="📥 Baixar registros removidos (CSV)",
                        data=csv_removidos,
                        file_name=f"registros_removidos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv",
                        help="Baixe um arquivo com todos os registros que foram removidos"
                    )
                    
                    st.info("💡 **Dica:** Revise estes registros para corrigir os problemas no arquivo original se necessário")
        
        # Estatísticas básicas
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📊 Total de Registros", f"{len(df_input):,}")
        with col2:
            st.metric("💰 Valor Total", f"R$ {df_input['valor'].sum():,.2f}")
        with col3:
            st.metric("👥 Matrículas Únicas", f"{df_input['matricula'].nunique():,}")
            
            # Análise de dados e alertas
            registros_vazios = df_input.isnull().all(axis=1).sum()
            duplicatas = len(df_input) - len(df_input.drop_duplicates())
            valores_zero = (df_input['valor'] == 0).sum()
            
            if registros_vazios > 0 or duplicatas > 0 or valores_zero > 0:
                st.warning("⚠️ **Problemas detectados nos dados:**")
                col1, col2, col3 = st.columns(3)
                with col1:
                    if registros_vazios > 0:
                        st.error(f"🗑️ {registros_vazios} linhas completamente vazias")
                with col2:
                    if duplicatas > 0:
                        st.warning(f"� {duplicatas} registros duplicados")
                with col3:
                    if valores_zero > 0:
                        st.info(f"⚪ {valores_zero} registros com valor zero")
                
                # Opções de limpeza
                st.subheader("🧹 Limpeza de Dados")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    remover_vazios = st.checkbox("Remover linhas vazias", value=True)
                with col2:
                    remover_duplicatas = st.checkbox("Remover duplicatas", value=True)
                with col3:
                    remover_zeros = st.checkbox("Remover valores zero", value=False)
                
                if st.button("🧹 Aplicar Limpeza", type="secondary"):
                    df_original = df_input.copy()
                    
                    if remover_vazios:
                        df_input = df_input.dropna(how='all')
                        st.success(f"✅ Removidas {len(df_original) - len(df_input)} linhas vazias")
                    
                    if remover_duplicatas:
                        df_antes = len(df_input)
                        df_input = df_input.drop_duplicates()
                        st.success(f"✅ Removidas {df_antes - len(df_input)} duplicatas")
                    
                    if remover_zeros:
                        df_antes = len(df_input)
                        df_input = df_input[df_input['valor'] != 0]
                        st.success(f"✅ Removidos {df_antes - len(df_input)} registros com valor zero")
                    
                    st.info(f"📊 Dataset limpo: {len(df_input)} registros restantes")
                    st.rerun()
            
            # Verificar se o dataset é muito grande
            if len(df_input) > 10000:
                st.warning(f"⚠️ **Dataset muito grande:** {len(df_input)} registros")
                st.info("� **Recomendações:**")
                st.markdown("""
                - Considere processar em lotes menores
                - Verifique se há dados duplicados desnecessários
                - O processamento pode ser mais lento
                """)
                
                processar_lotes = st.checkbox("Processar em lotes de 1000 registros", value=True)
                if processar_lotes:
                    st.session_state['processar_lotes'] = True
            
            # Preview dos dados
            with st.expander("👁️ Visualizar dados", expanded=False):
                st.dataframe(df_input.head(20), use_container_width=True)
                if len(df_input) > 20:
                    st.info(f"Mostrando as primeiras 20 linhas de {len(df_input)} registros")
            
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
                # Validação antes do processamento
                if len(df_input) == 0:
                    st.error("❌ Nenhum dado para processar após a limpeza!")
                    st.stop()
                
                # Alerta para grandes volumes
                if len(df_input) > 50000:
                    st.error(f"❌ Dataset muito grande: {len(df_input)} registros")
                    st.warning("⚠️ Por favor, reduza o dataset para menos de 50.000 registros")
                    st.info("💡 Sugestões: remova duplicatas, valores zero ou processe em partes menores")
                    st.stop()
                elif len(df_input) > 10000:
                    st.warning(f"⚠️ Processando {len(df_input)} registros - isso pode demorar...")
                
                with st.spinner("🔄 Processando dados..."):
                    # Carregar arquivos de referência
                    df_stakeholders = None
                    df_cost_centers = None
                    
                    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                    func_file = os.path.join(base_dir, "FUNC.xlsx")
                    centros_file = os.path.join(base_dir, "centros_de_custo.xlsx")
                    
                    # Progress bar para carregamento
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    status_text.text("📂 Carregando arquivo de funcionários...")
                    progress_bar.progress(10)
                    
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
                    
                    status_text.text("🏢 Carregando centros de custo...")
                    progress_bar.progress(20)
                    
                    if os.path.exists(centros_file):
                        df_cost_centers = pd.read_excel(centros_file)
                        df_cost_centers.columns = df_cost_centers.columns.str.lower()
                    
                    # Processar dados
                    status_text.text("⚙️ Processando dados do arquivo...")
                    progress_bar.progress(30)
                    
                    df_resultado = df_input.copy()
                    
                    # Normalizar matrícula
                    status_text.text("🔢 Normalizando matrículas...")
                    progress_bar.progress(40)
                    
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
                    
                    # Gerar campos básicos
                    status_text.text("📝 Gerando campos básicos...")
                    progress_bar.progress(50)
                    
                    df_resultado['id'] = [gerar_id_unico() for _ in range(len(df_resultado))]
                    df_resultado['categoryid'] = category_id
                    df_resultado['value'] = df_resultado['valor'].apply(converter_valor_americano)
                    df_resultado['date'] = str(schedule_date)
                    df_resultado['vencimento'] = str(due_date)
                    df_resultado['data_competencia'] = str(accrual_date)
                    df_resultado['description'] = description
                    df_resultado['reference'] = reference
                    
                    # Buscar IDs - Otimizado para grandes volumes
                    status_text.text("🔍 Buscando Stakeholder IDs...")
                    progress_bar.progress(60)
                    
                    # Usar merge para melhor performance em grandes datasets
                    if df_stakeholders is not None:
                        # Criar mapeamento de stakeholders
                        stakeholder_map = df_stakeholders.set_index('matricula')['Coluna2'].to_dict()
                        df_resultado['stakeholderid'] = df_resultado['matricula'].map(stakeholder_map)
                    else:
                        df_resultado['stakeholderid'] = None
                    
                    status_text.text("🏢 Buscando Cost Center IDs...")
                    progress_bar.progress(70)
                    
                    if df_cost_centers is not None:
                        # Criar mapeamento de centros de custo
                        cost_center_map = df_cost_centers.set_index('id empresa')['id cliente'].to_dict()
                        df_resultado['costcenterid'] = df_resultado['idsetor'].map(cost_center_map)
                    else:
                        df_resultado['costcenterid'] = None
                    
                    # Validar resultados
                    status_text.text("✅ Validando dados processados...")
                    progress_bar.progress(80)
                    
                    invalidos = df_resultado[
                        (df_resultado['stakeholderid'].isna()) | 
                        (df_resultado['costcenterid'].isna()) |
                        (df_resultado['value'] <= 0)
                    ]
                    
                    progress_bar.progress(90)
                    
                    # Limpar elementos de progresso
                    status_text.text("🎉 Processamento concluído!")
                    progress_bar.progress(100)
                    
                    # Aguardar um pouco e limpar
                    import time
                    time.sleep(1)
                    progress_bar.empty()
                    status_text.empty()
                    
                    if not invalidos.empty:
                        st.error(f"❌ {len(invalidos)} registros inválidos encontrados de {len(df_resultado)} total!")
                        
                        # Análise detalhada dos problemas
                        problemas = []
                        stakeholders_faltando = invalidos['stakeholderid'].isna().sum()
                        centros_faltando = invalidos['costcenterid'].isna().sum() 
                        valores_invalidos = (invalidos['value'] <= 0).sum()
                        
                        if stakeholders_faltando > 0:
                            matriculas_problematicas = invalidos[invalidos['stakeholderid'].isna()]['matricula'].unique()
                            st.warning(f"🔍 **{stakeholders_faltando} matrículas não encontradas no FUNC.xlsx**")
                            with st.expander(f"📋 Ver {len(matriculas_problematicas)} matrículas problemáticas"):
                                st.write(matriculas_problematicas.tolist())
                                st.info("💡 **Solução:** Adicione estas matrículas no arquivo FUNC.xlsx usando o Editor de Planilhas")
                        
                        if centros_faltando > 0:
                            setores_problematicos = invalidos[invalidos['costcenterid'].isna()]['idsetor'].unique()
                            st.warning(f"🏢 **{centros_faltando} setores não encontrados no centros_de_custo.xlsx**")
                            with st.expander(f"📋 Ver {len(setores_problematicos)} setores problemáticos"):
                                st.write("**IDs de Setor faltando:**")
                                for setor in setores_problematicos:
                                    st.write(f"• **ID Empresa:** {setor}")
                                st.info("� **Solução:** Adicione estes setores no arquivo centros_de_custo.xlsx usando o Editor de Planilhas")
                                st.markdown("---")
                                st.markdown("**🔧 Como adicionar no Editor:**")
                                st.markdown("""
                                1. Vá em "editor planilhas NOVO" no menu lateral
                                2. Selecione "centros_de_custo.xlsx"
                                3. Na aba "Adicionar Registro":
                                   - Preencha o "ID Empresa" com os valores acima
                                   - Preencha "Nome do Centro" 
                                   - Preencha "ID Cliente" (obtido da API NIBO)
                                4. Clique em "Adicionar Centro"
                                5. Volte aqui e reprocesse
                                """)
                        
                        if valores_invalidos > 0:
                            problemas.append(f"💰 {valores_invalidos} registros com valor zero ou negativo")
                        
                        with st.expander("👁️ Ver registros problemáticos (primeiros 100)"):
                            invalidos_display = invalidos[['matricula', 'idsetor', 'stakeholderid', 'costcenterid', 'value']].copy()
                            st.dataframe(invalidos_display.head(100), use_container_width=True)
                            if len(invalidos_display) > 100:
                                st.info(f"Mostrando os primeiros 100 de {len(invalidos_display)} registros problemáticos")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            continuar = st.checkbox("Continuar mesmo assim (processar apenas válidos)", value=True)
                        with col2:
                            if st.button("📊 Baixar Registros Problemáticos"):
                                csv = invalidos_display.to_csv(index=False)
                                st.download_button(
                                    label="📄 Download CSV",
                                    data=csv,
                                    file_name=f"registros_problematicos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                                    mime="text/csv"
                                )
                        
                        if continuar:
                            df_resultado = df_resultado[
                                (~df_resultado['stakeholderid'].isna()) & 
                                (~df_resultado['costcenterid'].isna()) &
                                (df_resultado['value'] > 0)
                            ]
                            st.success(f"✅ Processando {len(df_resultado)} registros válidos!")
                        else:
                            st.stop()
                    else:
                        st.success("✅ Todos os dados processados com sucesso!")
                    
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