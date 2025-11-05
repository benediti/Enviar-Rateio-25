"""
Gerenciador de Planilhas por Linha de Comando
Script simples para adicionar/editar registros via terminal
"""

import pandas as pd
import os
import sys
import uuid
from datetime import datetime
import argparse

class GerenciadorPlanilhas:
    """Gerenciador de planilhas via linha de comando"""
    
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.planilhas = {
            'func': 'FUNC.xlsx',
            'centros': 'centros_de_custo.xlsx',
            'categorias': 'categorias_nibo.xlsx'
        }
    
    def carregar_planilha(self, nome_planilha):
        """Carrega planilha"""
        caminho = os.path.join(self.base_dir, self.planilhas[nome_planilha])
        if os.path.exists(caminho):
            return pd.read_excel(caminho)
        return None
    
    def salvar_planilha(self, df, nome_planilha):
        """Salva planilha"""
        caminho = os.path.join(self.base_dir, self.planilhas[nome_planilha])
        
        # Backup
        if os.path.exists(caminho):
            backup_dir = os.path.join(self.base_dir, "backups")
            os.makedirs(backup_dir, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = os.path.join(backup_dir, f"{nome_planilha}_{timestamp}.xlsx")
            
            try:
                import shutil
                shutil.copy2(caminho, backup_path)
                print(f"📦 Backup: {backup_path}")
            except:
                pass
        
        # Salvar
        df.to_excel(caminho, index=False)
        return True
    
    def adicionar_funcionario(self, matricula, nome, email="", cargo=""):
        """Adiciona funcionário"""
        df = self.carregar_planilha('func')
        if df is None:
            df = pd.DataFrame(columns=['matricula', 'nome', 'Coluna2'])
        
        # Verificar se matrícula já existe
        if 'matricula' in df.columns and matricula in df['matricula'].values:
            print(f"❌ Matrícula {matricula} já existe!")
            return False
        
        # Novo funcionário
        novo = {
            'matricula': int(matricula),
            'nome': nome,
            'Coluna2': str(uuid.uuid4()),
            'email': email,
            'cargo': cargo,
            'adicionado_em': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Adicionar colunas existentes
        for col in df.columns:
            if col not in novo:
                novo[col] = ""
        
        # Adicionar ao DataFrame
        df = pd.concat([df, pd.DataFrame([novo])], ignore_index=True)
        
        if self.salvar_planilha(df, 'func'):
            print(f"✅ Funcionário adicionado: {nome} (Matrícula: {matricula})")
            return True
        return False
    
    def buscar_funcionario(self, matricula):
        """Busca funcionário por matrícula"""
        df = self.carregar_planilha('func')
        if df is None:
            print("❌ Planilha FUNC.xlsx não encontrada")
            return None
        
        resultado = df[df['matricula'] == int(matricula)]
        if resultado.empty:
            print(f"❌ Funcionário com matrícula {matricula} não encontrado")
            return None
        
        funcionario = resultado.iloc[0]
        print(f"✅ Funcionário encontrado:")
        print(f"   Matrícula: {funcionario['matricula']}")
        print(f"   Nome: {funcionario['nome']}")
        if 'Coluna2' in funcionario:
            print(f"   Stakeholder ID: {funcionario['Coluna2']}")
        if 'email' in funcionario and funcionario['email']:
            print(f"   E-mail: {funcionario['email']}")
        if 'cargo' in funcionario and funcionario['cargo']:
            print(f"   Cargo: {funcionario['cargo']}")
        
        return funcionario
    
    def listar_funcionarios(self, limite=10):
        """Lista funcionários"""
        df = self.carregar_planilha('func')
        if df is None:
            print("❌ Planilha FUNC.xlsx não encontrada")
            return
        
        print(f"📋 Lista de Funcionários (mostrando {min(limite, len(df))} de {len(df)}):")
        print("-" * 60)
        
        for i, row in df.head(limite).iterrows():
            print(f"{row['matricula']:>6} | {row['nome'][:30]:<30} | {row.get('cargo', '')[:15]}")
        
        if len(df) > limite:
            print(f"... e mais {len(df) - limite} funcionários")
    
    def adicionar_centro_custo(self, id_empresa, nome, id_cliente, responsavel=""):
        """Adiciona centro de custo"""
        df = self.carregar_planilha('centros')
        if df is None:
            df = pd.DataFrame(columns=['id empresa', 'nome', 'id cliente'])
        
        # Verificar se já existe
        if 'id empresa' in df.columns and id_empresa in df['id empresa'].values:
            print(f"❌ Centro de custo {id_empresa} já existe!")
            return False
        
        # Novo centro
        novo = {
            'id empresa': id_empresa,
            'nome': nome,
            'id cliente': id_cliente,
            'responsavel': responsavel,
            'adicionado_em': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Adicionar colunas existentes
        for col in df.columns:
            if col not in novo:
                novo[col] = ""
        
        df = pd.concat([df, pd.DataFrame([novo])], ignore_index=True)
        
        if self.salvar_planilha(df, 'centros'):
            print(f"✅ Centro de custo adicionado: {nome} ({id_empresa})")
            return True
        return False
    
    def status_planilhas(self):
        """Mostra status das planilhas"""
        print("📊 Status das Planilhas:")
        print("=" * 50)
        
        for nome, arquivo in self.planilhas.items():
            caminho = os.path.join(self.base_dir, arquivo)
            if os.path.exists(caminho):
                try:
                    df = pd.read_excel(caminho)
                    modificado = datetime.fromtimestamp(os.path.getmtime(caminho))
                    print(f"✅ {arquivo}:")
                    print(f"   📋 {len(df)} registros")
                    print(f"   📅 Modificado: {modificado.strftime('%d/%m/%Y %H:%M:%S')}")
                    print(f"   📝 Colunas: {', '.join(df.columns.tolist()[:3])}{'...' if len(df.columns) > 3 else ''}")
                except Exception as e:
                    print(f"❌ {arquivo}: Erro ao ler ({e})")
            else:
                print(f"❌ {arquivo}: Não encontrado")
            print()

def main():
    """Função principal com argumentos de linha de comando"""
    parser = argparse.ArgumentParser(description='Gerenciador de Planilhas')
    subparsers = parser.add_subparsers(dest='comando', help='Comandos disponíveis')
    
    # Comando: adicionar funcionário
    func_parser = subparsers.add_parser('add-func', help='Adicionar funcionário')
    func_parser.add_argument('matricula', type=int, help='Matrícula do funcionário')
    func_parser.add_argument('nome', help='Nome completo')
    func_parser.add_argument('--email', default='', help='E-mail')
    func_parser.add_argument('--cargo', default='', help='Cargo')
    
    # Comando: buscar funcionário
    buscar_parser = subparsers.add_parser('buscar-func', help='Buscar funcionário')
    buscar_parser.add_argument('matricula', type=int, help='Matrícula do funcionário')
    
    # Comando: listar funcionários
    listar_parser = subparsers.add_parser('listar-func', help='Listar funcionários')
    listar_parser.add_argument('--limite', type=int, default=10, help='Número máximo de registros')
    
    # Comando: adicionar centro de custo
    centro_parser = subparsers.add_parser('add-centro', help='Adicionar centro de custo')
    centro_parser.add_argument('id_empresa', help='ID da empresa')
    centro_parser.add_argument('nome', help='Nome do centro')
    centro_parser.add_argument('id_cliente', help='ID do cliente')
    centro_parser.add_argument('--responsavel', default='', help='Responsável')
    
    # Comando: status
    subparsers.add_parser('status', help='Status das planilhas')
    
    # Parse argumentos
    args = parser.parse_args()
    
    if not args.comando:
        parser.print_help()
        return
    
    # Executar comando
    gerenciador = GerenciadorPlanilhas()
    
    if args.comando == 'add-func':
        gerenciador.adicionar_funcionario(args.matricula, args.nome, args.email, args.cargo)
    
    elif args.comando == 'buscar-func':
        gerenciador.buscar_funcionario(args.matricula)
    
    elif args.comando == 'listar-func':
        gerenciador.listar_funcionarios(args.limite)
    
    elif args.comando == 'add-centro':
        gerenciador.adicionar_centro_custo(args.id_empresa, args.nome, args.id_cliente, args.responsavel)
    
    elif args.comando == 'status':
        gerenciador.status_planilhas()

def menu_interativo():
    """Menu interativo quando executado sem argumentos"""
    gerenciador = GerenciadorPlanilhas()
    
    while True:
        print("\n🔧 Gerenciador de Planilhas")
        print("=" * 30)
        print("1. Adicionar funcionário")
        print("2. Buscar funcionário")
        print("3. Listar funcionários")
        print("4. Adicionar centro de custo")
        print("5. Status das planilhas")
        print("0. Sair")
        
        opcao = input("\nEscolha (0-5): ").strip()
        
        if opcao == "0":
            print("👋 Até logo!")
            break
        
        elif opcao == "1":
            print("\n👤 Adicionar Funcionário")
            try:
                matricula = int(input("Matrícula: "))
                nome = input("Nome completo: ").strip()
                email = input("E-mail (opcional): ").strip()
                cargo = input("Cargo (opcional): ").strip()
                
                if nome:
                    gerenciador.adicionar_funcionario(matricula, nome, email, cargo)
                else:
                    print("❌ Nome é obrigatório")
            except ValueError:
                print("❌ Matrícula deve ser um número")
            except KeyboardInterrupt:
                print("\n❌ Operação cancelada")
        
        elif opcao == "2":
            print("\n🔍 Buscar Funcionário")
            try:
                matricula = int(input("Matrícula: "))
                gerenciador.buscar_funcionario(matricula)
            except ValueError:
                print("❌ Matrícula deve ser um número")
            except KeyboardInterrupt:
                print("\n❌ Operação cancelada")
        
        elif opcao == "3":
            print("\n📋 Listar Funcionários")
            try:
                limite = input("Quantos mostrar (padrão 10): ").strip()
                limite = int(limite) if limite.isdigit() else 10
                gerenciador.listar_funcionarios(limite)
            except KeyboardInterrupt:
                print("\n❌ Operação cancelada")
        
        elif opcao == "4":
            print("\n🏢 Adicionar Centro de Custo")
            try:
                id_empresa = input("ID Empresa: ").strip()
                nome = input("Nome: ").strip()
                id_cliente = input("ID Cliente: ").strip()
                responsavel = input("Responsável (opcional): ").strip()
                
                if id_empresa and nome and id_cliente:
                    gerenciador.adicionar_centro_custo(id_empresa, nome, id_cliente, responsavel)
                else:
                    print("❌ ID Empresa, Nome e ID Cliente são obrigatórios")
            except KeyboardInterrupt:
                print("\n❌ Operação cancelada")
        
        elif opcao == "5":
            gerenciador.status_planilhas()
        
        else:
            print("❌ Opção inválida")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Executar com argumentos
        main()
    else:
        # Menu interativo
        menu_interativo()
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