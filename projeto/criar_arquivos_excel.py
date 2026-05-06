"""
Script para criar arquivos Excel de exemplo
Execute este script para gerar os arquivos Excel necessários para o sistema
"""

import pandas as pd
from datetime import datetime, timedelta
import random

def criar_func_xlsx():
    """Cria o arquivo FUNC.xlsx com dados de funcionários"""
    
    # Dados de exemplo de funcionários
    funcionarios = []
    
    nomes = [
        "João Silva", "Maria Santos", "Pedro Costa", "Ana Lima", "Carlos Oliveira",
        "Fernanda Souza", "Ricardo Pereira", "Juliana Alves", "Bruno Martins", "Camila Rocha",
        "André Cardoso", "Beatriz Fernandes", "Daniel Barbosa", "Elena Rodriguez", "Felipe Nascimento",
        "Gabriela Mendes", "Henrique Castro", "Isabella Torres", "Jorge Ramos", "Karina Dias"
    ]
    
    cargos = [
        "Analista", "Desenvolvedor", "Gerente", "Coordenador", "Assistente",
        "Supervisor", "Especialista", "Consultor", "Diretor", "Técnico"
    ]
    
    centros_custo = ["CC001", "CC002", "CC003", "CC004", "CC005"]
    
    for i, nome in enumerate(nomes, 1):
        funcionario = {
            "ID": i,
            "Nome": nome,
            "CPF": f"{random.randint(100,999)}.{random.randint(100,999)}.{random.randint(100,999)}-{random.randint(10,99)}",
            "Cargo": random.choice(cargos),
            "Centro_Custo": random.choice(centros_custo),
            "Salario": round(random.uniform(2000, 15000), 2),
            "Data_Admissao": (datetime.now() - timedelta(days=random.randint(30, 3650))).strftime("%Y-%m-%d"),
            "Status": random.choice(["Ativo", "Ativo", "Ativo", "Inativo"]),  # 75% ativos
            "Email": f"{nome.lower().replace(' ', '.')}@empresa.com",
            "Telefone": f"(11) 9{random.randint(1000,9999)}-{random.randint(1000,9999)}"
        }
        funcionarios.append(funcionario)
    
    df = pd.DataFrame(funcionarios)
    df.to_excel("FUNC.xlsx", index=False)
    print("✅ FUNC.xlsx criado com sucesso!")
    return df

def criar_centros_custo_xlsx():
    """Cria o arquivo centros_de_custo.xlsx"""
    
    centros = [
        {"Codigo": "CC001", "Nome": "Tecnologia da Informação", "Responsavel": "João Silva", "Orcamento": 500000.00},
        {"Codigo": "CC002", "Nome": "Recursos Humanos", "Responsavel": "Maria Santos", "Orcamento": 200000.00},
        {"Codigo": "CC003", "Nome": "Financeiro", "Responsavel": "Pedro Costa", "Orcamento": 300000.00},
        {"Codigo": "CC004", "Nome": "Marketing", "Responsavel": "Ana Lima", "Orcamento": 150000.00},
        {"Codigo": "CC005", "Nome": "Operações", "Responsavel": "Carlos Oliveira", "Orcamento": 400000.00},
        {"Codigo": "CC006", "Nome": "Vendas", "Responsavel": "Fernanda Souza", "Orcamento": 350000.00},
        {"Codigo": "CC007", "Nome": "Compras", "Responsavel": "Ricardo Pereira", "Orcamento": 180000.00},
        {"Codigo": "CC008", "Nome": "Qualidade", "Responsavel": "Juliana Alves", "Orcamento": 120000.00}
    ]
    
    df = pd.DataFrame(centros)
    df.to_excel("centros_de_custo.xlsx", index=False)
    print("✅ centros_de_custo.xlsx criado com sucesso!")
    return df

def criar_categorias_nibo_xlsx():
    """Cria o arquivo categorias_nibo.xlsx"""
    
    categorias = [
        {"ID": 1, "Codigo": "CAT001", "Nome": "Salários e Ordenados", "Tipo": "Despesa", "Conta_Contabil": "3.1.1.01"},
        {"ID": 2, "Codigo": "CAT002", "Nome": "Encargos Sociais", "Tipo": "Despesa", "Conta_Contabil": "3.1.1.02"},
        {"ID": 3, "Codigo": "CAT003", "Nome": "Benefícios", "Tipo": "Despesa", "Conta_Contabil": "3.1.1.03"},
        {"ID": 4, "Codigo": "CAT004", "Nome": "Vale Transporte", "Tipo": "Despesa", "Conta_Contabil": "3.1.1.04"},
        {"ID": 5, "Codigo": "CAT005", "Nome": "Vale Refeição", "Tipo": "Despesa", "Conta_Contabil": "3.1.1.05"},
        {"ID": 6, "Codigo": "CAT006", "Nome": "Plano de Saúde", "Tipo": "Despesa", "Conta_Contabil": "3.1.1.06"},
        {"ID": 7, "Codigo": "CAT007", "Nome": "Férias", "Tipo": "Provisão", "Conta_Contabil": "2.1.4.01"},
        {"ID": 8, "Codigo": "CAT008", "Nome": "13º Salário", "Tipo": "Provisão", "Conta_Contabil": "2.1.4.02"},
        {"ID": 9, "Codigo": "CAT009", "Nome": "FGTS", "Tipo": "Despesa", "Conta_Contabil": "3.1.1.07"},
        {"ID": 10, "Codigo": "CAT010", "Nome": "Horas Extras", "Tipo": "Despesa", "Conta_Contabil": "3.1.1.08"}
    ]
    
    df = pd.DataFrame(categorias)
    df.to_excel("categorias_nibo.xlsx", index=False)
    print("✅ categorias_nibo.xlsx criado com sucesso!")
    return df

def main():
    """Função principal para criar todos os arquivos Excel"""
    print("🔄 Criando arquivos Excel de exemplo...")
    print("=" * 50)
    
    try:
        # Criar os arquivos Excel
        df_func = criar_func_xlsx()
        df_centros = criar_centros_custo_xlsx()
        df_categorias = criar_categorias_nibo_xlsx()
        
        print("=" * 50)
        print("✅ Todos os arquivos Excel foram criados com sucesso!")
        print("\nResumo dos arquivos criados:")
        print(f"📋 FUNC.xlsx: {len(df_func)} funcionários")
        print(f"🏢 centros_de_custo.xlsx: {len(df_centros)} centros de custo")
        print(f"📂 categorias_nibo.xlsx: {len(df_categorias)} categorias")
        
        print("\n💡 Os arquivos foram criados no diretório atual.")
        print("   Você pode movê-los para a pasta do projeto se necessário.")
        
    except Exception as e:
        print(f"❌ Erro ao criar arquivos: {e}")
        print("Certifique-se de que o pandas está instalado: pip install pandas openpyxl")

if __name__ == "__main__":
    main()