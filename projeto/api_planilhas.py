"""
API REST para Atualização de Planilhas
Permite atualizar planilhas via requisições HTTP
"""

from flask import Flask, request, jsonify
import pandas as pd
import os
from datetime import datetime
import uuid
import json

app = Flask(__name__)

# Diretório base
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def salvar_backup(df, nome_arquivo):
    """Salva backup antes de alterar arquivo"""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = os.path.join(BASE_DIR, "backups")
        os.makedirs(backup_dir, exist_ok=True)
        
        backup_path = os.path.join(backup_dir, f"{nome_arquivo.replace('.xlsx', '')}_{timestamp}.xlsx")
        df.to_excel(backup_path, index=False)
        return backup_path
    except:
        return None

def carregar_planilha(nome_arquivo):
    """Carrega planilha existente"""
    caminho_arquivo = os.path.join(BASE_DIR, nome_arquivo)
    if os.path.exists(caminho_arquivo):
        return pd.read_excel(caminho_arquivo)
    return None

def salvar_planilha(df, nome_arquivo):
    """Salva planilha"""
    try:
        caminho_arquivo = os.path.join(BASE_DIR, nome_arquivo)
        
        # Fazer backup se arquivo já existe
        if os.path.exists(caminho_arquivo):
            df_atual = pd.read_excel(caminho_arquivo)
            salvar_backup(df_atual, nome_arquivo)
        
        # Salvar novo arquivo
        df.to_excel(caminho_arquivo, index=False)
        return True
    except:
        return False

@app.route('/api/planilhas', methods=['GET'])
def listar_planilhas():
    """Lista planilhas disponíveis"""
    planilhas = []
    arquivos = ['FUNC.xlsx', 'centros_de_custo.xlsx', 'categorias_nibo.xlsx']
    
    for arquivo in arquivos:
        df = carregar_planilha(arquivo)
        planilhas.append({
            'nome': arquivo,
            'existe': df is not None,
            'registros': len(df) if df is not None else 0,
            'ultima_modificacao': datetime.fromtimestamp(
                os.path.getmtime(os.path.join(BASE_DIR, arquivo))
            ).isoformat() if os.path.exists(os.path.join(BASE_DIR, arquivo)) else None
        })
    
    return jsonify(planilhas)

@app.route('/api/planilhas/<nome_arquivo>/adicionar', methods=['POST'])
def adicionar_registro(nome_arquivo):
    """Adiciona novo registro à planilha"""
    if nome_arquivo not in ['FUNC.xlsx', 'centros_de_custo.xlsx', 'categorias_nibo.xlsx']:
        return jsonify({'erro': 'Planilha não permitida'}), 400
    
    dados = request.json
    if not dados:
        return jsonify({'erro': 'Dados não fornecidos'}), 400
    
    df = carregar_planilha(nome_arquivo)
    if df is None:
        # Criar planilha nova
        if nome_arquivo == 'FUNC.xlsx':
            df = pd.DataFrame(columns=['matricula', 'nome', 'Coluna2'])
        elif nome_arquivo == 'centros_de_custo.xlsx':
            df = pd.DataFrame(columns=['id empresa', 'nome', 'id cliente'])
        elif nome_arquivo == 'categorias_nibo.xlsx':
            df = pd.DataFrame(columns=['ID', 'Nome'])
    
    # Validações específicas
    if nome_arquivo == 'FUNC.xlsx':
        if 'matricula' not in dados:
            return jsonify({'erro': 'Matrícula é obrigatória'}), 400
        
        # Verificar se matrícula já existe
        if 'matricula' in df.columns and dados['matricula'] in df['matricula'].values:
            return jsonify({'erro': 'Matrícula já existe'}), 400
        
        # Gerar ID se não fornecido
        if 'Coluna2' not in dados:
            dados['Coluna2'] = str(uuid.uuid4())
    
    # Adicionar timestamp
    dados['_adicionado_em'] = datetime.now().isoformat()
    
    # Criar novo DataFrame com o registro
    df_novo = pd.concat([df, pd.DataFrame([dados])], ignore_index=True)
    
    if salvar_planilha(df_novo, nome_arquivo):
        return jsonify({
            'sucesso': True,
            'mensagem': 'Registro adicionado com sucesso',
            'total_registros': len(df_novo)
        })
    else:
        return jsonify({'erro': 'Erro ao salvar planilha'}), 500

if __name__ == '__main__':
    print(" Iniciando API de Planilhas...")
    app.run(debug=True, host='0.0.0.0', port=5000)
