import streamlit as st
import pandas as pd
import json
import io
import zipfile
from datetime import datetime

# Configuração da página
st.set_page_config(
    page_title="NIBO - Gerar Coleção Postman",
    page_icon="🚀",
    layout="wide"
)

# ========================================
# FUNÇÕES AUXILIARES
# ========================================

def validar_colunas_obrigatorias(df):
    """Valida se a planilha contém todas as colunas obrigatórias"""
    colunas_obrigatorias = [
        'stakeholderId', 'description', 'reference', 'date', 
        'Vencimento', 'categoryId', 'value', 'costCenterId'
    ]
    
    colunas_faltando = [col for col in colunas_obrigatorias if col not in df.columns]
    
    if colunas_faltando:
        st.error(f"❌ Colunas obrigatórias não encontradas: {', '.join(colunas_faltando)}")
        st.info("📋 Colunas obrigatórias:")
        for col in colunas_obrigatorias:
            st.text(f"  • {col}")
        return False
    
    return True

def validar_dados(df):
    """Valida os dados da planilha"""
    erros = []
    
    # Verificar se há linhas vazias
    linhas_vazias = df.isnull().all(axis=1).sum()
    if linhas_vazias > 0:
        erros.append(f"📝 {linhas_vazias} linha(s) completamente vazia(s) encontrada(s)")
    
    # Verificar valores monetários
    try:
        pd.to_numeric(df['value'], errors='coerce')
    except:
        erros.append("💰 Coluna 'value' contém valores não numéricos")
    
    # Verificar datas
    valores_nulos = df[['stakeholderId', 'description', 'date', 'Vencimento']].isnull().sum()
    for coluna, nulos in valores_nulos.items():
        if nulos > 0:
            erros.append(f"📅 {nulos} valor(es) nulo(s) na coluna '{coluna}'")
    
    return erros

def converter_planilha_para_json(df, token_api, nome_colecao):
    """Converte a planilha em formato JSON para coleção Postman"""
    json_list = []
    
    for _, row in df.iterrows():
        if pd.isna(row).all():
            continue
            
        json_data = {
            "stakeholderId": str(row["stakeholderId"]) if pd.notna(row["stakeholderId"]) else "",
            "description": str(row["description"]) if pd.notna(row["description"]) else "",
            "reference": str(row["reference"]) if pd.notna(row["reference"]) else "",
            "scheduleDate": str(row["date"]) if pd.notna(row["date"]) else "",
            "dueDate": str(row["Vencimento"]) if pd.notna(row["Vencimento"]) else "",
            "accrualDate": str(row["date"]) if pd.notna(row["date"]) else "",
            "categories": [
                {
                    "categoryId": str(row["categoryId"]) if pd.notna(row["categoryId"]) else "",
                    "value": float(row["value"]) if pd.notna(row["value"]) else 0.0
                }
            ],
            "costCenterValueType": 0,
            "costCenters": [
                {
                    "costCenterId": str(row["costCenterId"]) if pd.notna(row["costCenterId"]) else "",
                    "value": float(row["value"]) if pd.notna(row["value"]) else 0.0
                }
            ]
        }
        json_list.append(json_data)
    
    # Criar coleção Postman
    colecao_postman = {
        "info": {
            "name": nome_colecao,
            "_postman_id": f"auto-generated-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json",
            "description": f"Coleção gerada automaticamente em {datetime.now().strftime('%d/%m/%Y às %H:%M')}"
        },
        "item": []
    }
    
    for i, item in enumerate(json_list):
        colecao_postman["item"].append({
            "name": f"Agendamento {i+1} - {item['description'][:50]}{'...' if len(item['description']) > 50 else ''}",
            "request": {
                "method": "POST",
                "header": [
                    {"key": "Content-Type", "value": "application/json"},
                    {"key": "ApiToken", "value": token_api}
                ],
                "url": {
                    "raw": "https://api.nibo.com.br/empresas/v1/schedules/debit",
                    "protocol": "https",
                    "host": ["api", "nibo", "com", "br"],
                    "path": ["empresas", "v1", "schedules", "debit"]
                },
                "body": {
                    "mode": "raw",
                    "raw": json.dumps(item, indent=2, ensure_ascii=False)
                }
            },
            "response": []
        })
    
    return colecao_postman, len(json_list), json_list

def criar_jsons_individuais(df):
    """Cria JSONs individuais para cada linha da planilha"""
    json_list = []
    
    for i, row in df.iterrows():
        if pd.isna(row).all():
            continue
            
        json_data = {
            "stakeholderId": str(row["stakeholderId"]) if pd.notna(row["stakeholderId"]) else "",
            "description": str(row["description"]) if pd.notna(row["description"]) else "",
            "reference": str(row["reference"]) if pd.notna(row["reference"]) else "",
            "scheduleDate": str(row["date"]) if pd.notna(row["date"]) else "",
            "dueDate": str(row["Vencimento"]) if pd.notna(row["Vencimento"]) else "",
            "accrualDate": str(row["date"]) if pd.notna(row["date"]) else "",
            "categories": [
                {
                    "categoryId": str(row["categoryId"]) if pd.notna(row["categoryId"]) else "",
                    "value": float(row["value"]) if pd.notna(row["value"]) else 0.0
                }
            ],
            "costCenterValueType": 0,
            "costCenters": [
                {
                    "costCenterId": str(row["costCenterId"]) if pd.notna(row["costCenterId"]) else "",
                    "value": float(row["value"]) if pd.notna(row["value"]) else 0.0
                }
            ]
        }
        json_list.append(json_data)
    
    return json_list

def criar_zip_com_jsons(json_list):
    """Cria arquivo ZIP com JSONs individuais"""
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        control_data = []
        
        for i, json_data in enumerate(json_list):
            descricao_limpa = "".join(c for c in json_data["description"] if c.isalnum() or c in (' ', '-', '_')).rstrip()
            nome_arquivo = f"agendamento_{i+1:03d}_{descricao_limpa[:30]}.json"
            
            json_string = json.dumps(json_data, indent=2, ensure_ascii=False)
            zip_file.writestr(nome_arquivo, json_string)
            
            control_data.append({"file": nome_arquivo})
        
        control_json = json.dumps(control_data, indent=2, ensure_ascii=False)
        zip_file.writestr("data.json", control_json)
        
        readme_content = f"""# Nibo API - JSONs Individuais
Gerado em: {datetime.now().strftime('%d/%m/%Y às %H:%M')}

## Arquivos inclusos:
- {len(json_list)} arquivos JSON individuais (agendamento_XXX_*.json)
- data.json: Arquivo de controle para Collection Runner do Postman

## Como usar no Postman Collection Runner:

1. **Crie uma requisição POST** para: https://api.nibo.com.br/empresas/v1/schedules/debit
2. **Adicione os headers**:
   - Content-Type: application/json
   - ApiToken: SEU_TOKEN_AQUI

3. **Pre-request Script** (copie e cole):
```javascript
const fs = require('fs');
const path = require('path');

// Caminho onde você extraiu os JSONs
const basePath = "C:/caminho/para/seus/jsons"; // AJUSTE ESTE CAMINHO

// Obtém o nome do arquivo da variável "file"
const fileName = pm.iterationData.get("file");
const filePath = path.join(basePath, fileName);

// Lê o conteúdo do JSON e define como body
const fileContent = fs.readFileSync(filePath, 'utf8');
pm.request.body.raw = fileContent;

console.log("Carregando arquivo:", fileName);
```

4. **No Collection Runner**:
   - Selecione o arquivo data.json como Data File
   - Configure o número de iterações: {len(json_list)}
   - Execute a coleção
"""
        zip_file.writestr("README.md", readme_content)
    
    zip_buffer.seek(0)
    return zip_buffer

def criar_colecao_com_runner(df, token_api, nome_colecao):
    """Cria coleção otimizada para Collection Runner com arquivo de dados"""
    json_list = []
    data_file_list = []
    
    for i, row in df.iterrows():
        if pd.isna(row).all():
            continue
            
        json_data = {
            "stakeholderId": str(row["stakeholderId"]) if pd.notna(row["stakeholderId"]) else "",
            "description": str(row["description"]) if pd.notna(row["description"]) else "",
            "reference": str(row["reference"]) if pd.notna(row["reference"]) else "",
            "scheduleDate": str(row["date"]) if pd.notna(row["date"]) else "",
            "dueDate": str(row["Vencimento"]) if pd.notna(row["Vencimento"]) else "",
            "accrualDate": str(row["date"]) if pd.notna(row["date"]) else "",
            "categories": [
                {
                    "categoryId": str(row["categoryId"]) if pd.notna(row["categoryId"]) else "",
                    "value": float(row["value"]) if pd.notna(row["value"]) else 0.0
                }
            ],
            "costCenterValueType": 0,
            "costCenters": [
                {
                    "costCenterId": str(row["costCenterId"]) if pd.notna(row["costCenterId"]) else "",
                    "value": float(row["value"]) if pd.notna(row["value"]) else 0.0
                }
            ]
        }
        
        json_list.append(json_data)
        data_file_list.append({
            "requestData": json.dumps(json_data, ensure_ascii=False),
            "description": json_data["description"]
        })
    
    pre_request_script = '''
// Script para carregar dados dinamicamente no Collection Runner
const requestData = pm.iterationData.get("requestData");

if (requestData) {
    // Define o body da requisição com os dados da iteração atual
    pm.request.body.raw = requestData;
    
    // Log para debug
    console.log("Enviando dados:", JSON.parse(requestData).description);
}
'''
    
    colecao_runner = {
        "info": {
            "name": f"{nome_colecao} - Collection Runner",
            "_postman_id": f"runner-generated-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json",
            "description": f"Coleção otimizada para Collection Runner - {datetime.now().strftime('%d/%m/%Y às %H:%M')}"
        },
        "item": [
            {
                "name": "Criar Agendamento Nibo",
                "event": [
                    {
                        "listen": "prerequest",
                        "script": {
                            "exec": pre_request_script.split('\n'),
                            "type": "text/javascript"
                        }
                    }
                ],
                "request": {
                    "method": "POST",
                    "header": [
                        {"key": "Content-Type", "value": "application/json"},
                        {"key": "ApiToken", "value": token_api}
                    ],
                    "url": {
                        "raw": "https://api.nibo.com.br/empresas/v1/schedules/debit",
                        "protocol": "https",
                        "host": ["api", "nibo", "com", "br"],
                        "path": ["empresas", "v1", "schedules", "debit"]
                    },
                    "body": {
                        "mode": "raw",
                        "raw": "// Este body será substituído pelo Pre-request Script"
                    }
                },
                "response": []
            }
        ]
    }
    
    return colecao_runner, data_file_list, len(json_list)

# ========================================
# INTERFACE PRINCIPAL
# ========================================

st.markdown("""
# 🚀 Etapa 2: Gerar Coleção Postman
### Transforme seus dados processados em coleção Postman pronta para uso
---
""")

# ========================================
# SIDEBAR - CONFIGURAÇÕES
# ========================================

with st.sidebar:
    st.header("⚙️ Configurações")
    
    # Token da API
    token_api = st.text_input(
        "🔑 Token da API Nibo:",
        type="password",
        help="Insira seu token de autenticação da API Nibo"
    )
    
    if token_api:
        st.success("✅ Token configurado")
    else:
        st.warning("⚠️ Token não configurado")
    
    # Nome da coleção
    nome_colecao = st.text_input(
        "📝 Nome da Coleção:",
        value="Nibo Agendamentos Automáticos",
        help="Nome que aparecerá na coleção do Postman"
    )
    
    st.markdown("---")
    st.markdown("### 📋 Colunas Esperadas:")
    colunas_esperadas = [
        'stakeholderId', 'description', 'reference', 'date', 
        'Vencimento', 'categoryId', 'value', 'costCenterId'
    ]
    for col in colunas_esperadas:
        st.text(f"• {col}")

# ========================================
# ÁREA PRINCIPAL
# ========================================

st.header("📤 Upload da Planilha Processada")
st.info("💡 Use o arquivo **'Dados Prontos para Postman'** baixado na Etapa 1")

uploaded_file = st.file_uploader(
    "Selecione a planilha processada:",
    type=['xlsx', 'xls', 'csv'],
    help="Arquivo gerado na Etapa 1 com todos os IDs preenchidos"
)

if uploaded_file is not None:
    try:
        # Ler o arquivo
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        
        st.success(f"✅ Arquivo carregado com sucesso! {len(df)} linha(s) encontrada(s)")
        
        # Mostrar preview dos dados
        with st.expander("👁️ Preview dos Dados", expanded=True):
            st.dataframe(df.head(10), use_container_width=True)
            if len(df) > 10:
                st.info(f"Mostrando as primeiras 10 linhas de {len(df)} total")
        
        # Validar colunas obrigatórias
        if validar_colunas_obrigatorias(df):
            st.success("✅ Todas as colunas obrigatórias encontradas!")
            
            # Validar dados
            erros = validar_dados(df)
            if erros:
                with st.expander("⚠️ Avisos de Validação", expanded=True):
                    for erro in erros:
                        st.warning(erro)
            
            # Estatísticas
            st.markdown("---")
            st.header("📊 Resumo dos Dados")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("📋 Total de Linhas", len(df))
            with col2:
                st.metric("💰 Valor Total", f"R$ {df['value'].sum():,.2f}")
            with col3:
                st.metric("🏢 Stakeholders Únicos", df['stakeholderId'].nunique())
            with col4:
                st.metric("🏷️ Categorias Únicas", df['categoryId'].nunique())
            
            # Opções de geração
            st.markdown("---")
            st.header("🎯 Tipo de Coleção")
            
            tipo_colecao = st.radio(
                "Escolha o formato de exportação:",
                ["📋 Coleção Tradicional", "⚡ Coleção para Collection Runner", "📦 JSONs Individuais (ZIP)"],
                help="""
                **Tradicional**: Uma requisição por linha da planilha (ideal para poucos registros)
                **Collection Runner**: Uma requisição única que usa dados externos (recomendado para muitos registros)
                **JSONs Individuais**: Cada linha vira um arquivo JSON separado (máxima flexibilidade)
                """
            )
            
            # Descrição do tipo selecionado
            if tipo_colecao == "📋 Coleção Tradicional":
                st.info("""
                **📋 Coleção Tradicional**
                - ✓ Cada linha vira uma requisição separada
                - ✓ Fácil de visualizar e testar individualmente
                - ✓ Ideal para até 50 registros
                - ⚠️ Pode ficar pesado com muitos registros
                """)
            elif tipo_colecao == "⚡ Coleção para Collection Runner":
                st.info("""
                **⚡ Collection Runner** (Recomendado)
                - ✓ Uma requisição reutilizável com dados externos
                - ✓ Controle de velocidade entre requests
                - ✓ Relatórios automáticos
                - ✓ Ideal para qualquer quantidade de registros
                """)
            else:
                st.info("""
                **📦 JSONs Individuais**
                - ✓ Máxima flexibilidade de uso
                - ✓ Fácil debugging de registros específicos
                - ✓ Pode ser usado com ou sem Postman
                - ✓ Inclui README com instruções
                """)
            
            # Botão para gerar coleção
            st.markdown("---")
            if st.button("🚀 Gerar Coleção", type="primary", use_container_width=True):
                if not token_api:
                    st.error("❌ Por favor, insira o token da API Nibo na barra lateral")
                elif not nome_colecao:
                    st.error("❌ Por favor, insira um nome para a coleção")
                else:
                    with st.spinner("🔄 Gerando coleção Postman..."):
                        if tipo_colecao == "📋 Coleção Tradicional":
                            # Coleção tradicional
                            colecao, total_requests, _ = converter_planilha_para_json(df, token_api, nome_colecao)
                            
                            json_string = json.dumps(colecao, indent=2, ensure_ascii=False)
                            
                            st.success(f"✅ Coleção tradicional gerada! {total_requests} requisições criadas")
                            
                            # Botão de download
                            st.download_button(
                                label="📥 Baixar Coleção Postman",
                                data=json_string,
                                file_name=f"nibo_collection_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                                mime="application/json",
                                use_container_width=True
                            )
                            
                            # Instruções
                            with st.expander("📖 Como importar no Postman"):
                                st.markdown("""
                                ### 📥 Passos para importar:
                                1. Abra o Postman
                                2. Clique em **"Import"** no canto superior esquerdo
                                3. Arraste o arquivo JSON baixado ou clique para selecioná-lo
                                4. A coleção será importada com todas as requisições
                                5. Você pode executar cada requisição individualmente
                                
                                ### ✅ Vantagens:
                                - Visualizar cada requisição separadamente
                                - Testar requisições individuais
                                - Modificar facilmente antes de enviar
                                """)
                            
                        elif tipo_colecao == "⚡ Coleção para Collection Runner":
                            # Coleção para Collection Runner
                            colecao_runner, data_file, total_requests = criar_colecao_com_runner(df, token_api, nome_colecao)
                            
                            # Criar arquivo de dados CSV para o runner
                            df_runner = pd.DataFrame(data_file)
                            csv_data = df_runner.to_csv(index=False, encoding='utf-8')
                            
                            json_string = json.dumps(colecao_runner, indent=2, ensure_ascii=False)
                            
                            st.success(f"✅ Coleção para Runner gerada! {total_requests} registros preparados")
                            
                            # Downloads
                            col1, col2 = st.columns(2)
                            with col1:
                                st.download_button(
                                    label="📥 Baixar Coleção",
                                    data=json_string,
                                    file_name=f"nibo_runner_collection_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                                    mime="application/json",
                                    use_container_width=True
                                )
                            with col2:
                                st.download_button(
                                    label="📊 Baixar Dados CSV",
                                    data=csv_data,
                                    file_name=f"nibo_runner_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                                    mime="text/csv",
                                    use_container_width=True
                                )
                            
                            # Instruções de uso
                            with st.expander("📖 Como usar no Collection Runner", expanded=True):
                                st.markdown("""
                                ### 🎯 Passos para usar no Postman:
                                
                                1. **Importe a coleção** no Postman (arquivo JSON)
                                2. **Clique em "Run Collection"** (botão play ao lado do nome da coleção)
                                3. **Upload do arquivo CSV** na seção "Data"
                                4. **Configure as iterações** para o número de linhas do CSV
                                5. **Ajuste o delay** entre requisições se necessário (ex: 500ms)
                                6. **Execute** a coleção
                                
                                ### ⚡ Vantagens do Collection Runner:
                                - ✅ **Mais eficiente** para muitas requisições
                                - ✅ **Controle de velocidade** (delay entre requisições)
                                - ✅ **Relatórios automáticos** de sucesso/falha
                                - ✅ **Logs detalhados** de cada execução
                                - ✅ **Pode pausar e retomar** a execução
                                
                                ### 📊 Monitoramento:
                                O Collection Runner mostra em tempo real:
                                - Número de requisições executadas
                                - Taxa de sucesso/falha
                                - Tempo total de execução
                                - Logs detalhados de cada iteração
                                """)
                        
                        else:
                            # JSONs Individuais em ZIP
                            json_list = criar_jsons_individuais(df)
                            zip_data = criar_zip_com_jsons(json_list)
                            
                            st.success(f"✅ ZIP com JSONs individuais gerado! {len(json_list)} arquivos criados")
                            
                            # Download do ZIP
                            st.download_button(
                                label="📦 Baixar ZIP com JSONs",
                                data=zip_data.getvalue(),
                                file_name=f"nibo_jsons_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
                                mime="application/zip",
                                use_container_width=True
                            )
                            
                            # Instruções de uso
                            with st.expander("📖 Como usar os JSONs individuais", expanded=True):
                                st.markdown(f"""
                                ### 📦 Conteúdo do ZIP:
                                - **{len(json_list)} arquivos JSON** individuais
                                - **data.json**: Arquivo de controle para Collection Runner
                                - **README.md**: Instruções completas de uso
                                
                                ### 🔧 Opção 1 - Collection Runner (Recomendado):
                                1. **Extraia o ZIP** em uma pasta no seu computador
                                2. **Crie uma requisição POST** no Postman para a API Nibo
                                3. **Copie o Pre-request Script** do README.md
                                4. **Use data.json** como Data File no Runner
                                5. **Ajuste o caminho** no script para a pasta extraída
                                
                                ### 📋 Opção 2 - Uso Manual:
                                - Cada arquivo JSON pode ser usado individualmente
                                - Copie e cole o conteúdo no body das requisições
                                - Ideal para testes específicos ou debugging
                                
                                ### 🎯 Vantagens dos JSONs separados:
                                - ✅ **Flexibilidade total** de uso
                                - ✅ **Fácil debugging** de registros específicos
                                - ✅ **Reutilização** de JSONs individuais
                                - ✅ **Controle granular** sobre cada requisição
                                - ✅ **Pode ser usado fora do Postman**
                                """)
                            
                            # Mostrar lista dos arquivos
                            with st.expander("📋 Preview dos arquivos no ZIP"):
                                st.markdown("### Arquivos que serão gerados:")
                                for i, json_data in enumerate(json_list[:10]):
                                    descricao_limpa = "".join(c for c in json_data["description"] if c.isalnum() or c in (' ', '-', '_')).rstrip()
                                    nome_arquivo = f"agendamento_{i+1:03d}_{descricao_limpa[:30]}.json"
                                    st.text(f"📄 {nome_arquivo}")
                                
                                if len(json_list) > 10:
                                    st.text(f"... e mais {len(json_list) - 10} arquivos")
                                
                                st.text("📄 data.json (arquivo de controle)")
                                st.text("📄 README.md (instruções de uso)")
                        
                        # Preview da coleção
                        if tipo_colecao != "📦 JSONs Individuais (ZIP)":
                            with st.expander("👁️ Preview da Coleção JSON"):
                                if tipo_colecao == "📋 Coleção Tradicional":
                                    st.json(colecao, expanded=False)
                                else:
                                    st.json(colecao_runner, expanded=False)
                        
                        # Próximos passos
                        st.markdown("---")
                        st.markdown("### 🎉 Processo Concluído!")
                        st.success("""
                        ✅ **Coleção gerada com sucesso!**
                        
                        **Próximos passos:**
                        1. Baixe o(s) arquivo(s) gerado(s)
                        2. Importe no Postman
                        3. Execute as requisições
                        4. Monitore os resultados
                        """)
    
    except Exception as e:
        st.error(f"❌ Erro ao processar o arquivo: {str(e)}")
        st.info("💡 Verifique se o arquivo está no formato correto e contém todas as colunas necessárias")

else:
    st.info("👆 Faça upload da planilha processada para começar")
    
    with st.expander("📋 Instruções", expanded=True):
        st.markdown("""
        ### 🎯 Objetivo desta Etapa:
        Gerar uma coleção Postman pronta para enviar os dados para a API NIBO.
        
        ### 📝 Passo a Passo:
        1. **Configure o token da API** na barra lateral
        2. **Faça upload** do arquivo "Dados Prontos para Postman" (da Etapa 1)
        3. **Escolha o tipo** de coleção desejado
        4. **Clique em "Gerar Coleção"**
        5. **Baixe** os arquivos gerados
        6. **Importe** no Postman e execute
        
        ### 📦 Tipos de Coleção:
        
        **📋 Tradicional**
        - Melhor para: Até 50 registros
        - Vantagem: Fácil visualização individual
        
        **⚡ Collection Runner**
        - Melhor para: Qualquer quantidade
        - Vantagem: Controle total da execução
        
        **📦 JSONs Individuais**
        - Melhor para: Máxima flexibilidade
        - Vantagem: Uso fora do Postman
        """)

# Footer
st.markdown("---")
st.markdown("*🚀 Etapa 2 de 2 - Geração de Coleção Postman*")