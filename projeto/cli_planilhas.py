"""
Gerenciador de Planilhas por Linha de Comando
Script simples para adicionar/editar registros via terminal
"""

import pandas as pd
import os
import sys
import uuid
from datetime import datetime

class GerenciadorPlanilhas:
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.planilhas = {
            'func': 'FUNC.xlsx',
            'centros': 'centros_de_custo.xlsx',
            'categorias': 'categorias_nibo.xlsx'
        }
    
    def adicionar_funcionario(self, matricula, nome, email="", cargo=""):
        """Adiciona funcionário"""
        caminho = os.path.join(self.base_dir, self.planilhas['func'])
        
        if os.path.exists(caminho):
            df = pd.read_excel(caminho)
        else:
            df = pd.DataFrame(columns=['matricula', 'nome', 'Coluna2'])
        
        # Verificar se matrícula já existe
        if 'matricula' in df.columns and matricula in df['matricula'].values:
            print(f" Matrícula {matricula} já existe!")
            return False
        
        # Novo funcionário
        novo = {
            'matricula': int(matricula),
            'nome': nome,
            'Coluna2': str(uuid.uuid4()),
            'email': email,
            'cargo': cargo
        }
        
        df = pd.concat([df, pd.DataFrame([novo])], ignore_index=True)
        df.to_excel(caminho, index=False)
        print(f" Funcionário adicionado: {nome} (Matrícula: {matricula})")
        return True

if __name__ == "__main__":
    gerenciador = GerenciadorPlanilhas()
    
    if len(sys.argv) >= 4 and sys.argv[1] == "add-func":
        matricula = int(sys.argv[2])
        nome = sys.argv[3]
        email = sys.argv[4] if len(sys.argv) > 4 else ""
        cargo = sys.argv[5] if len(sys.argv) > 5 else ""
        gerenciador.adicionar_funcionario(matricula, nome, email, cargo)
    else:
        print("Uso: python cli_planilhas.py add-func <matricula> <nome> [email] [cargo]")
