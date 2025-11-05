"""
Integração com Google Forms
Monitora respostas do Google Forms e adiciona automaticamente nas planilhas
"""

import pandas as pd
import requests
import os
from datetime import datetime
import time
import json
import uuid

class IntegradorGoogleForms:
    """Classe para integrar com Google Forms"""
    
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.config_file = "forms_config.json"
        self.ultimo_processamento = "ultimo_forms.json"
        
    def configurar_forms(self):
        """Configura integração com Google Forms"""
        print("🔧 Configuração do Google Forms")
        print("=" * 50)
        
        print("\n📝 Passo 1: Configurar Google Forms")
        print("1. Acesse: https://forms.google.com")
        print("2. Crie um formulário com os campos:")
        print("   - Matrícula (Resposta curta, obrigatório)")
        print("   - Nome Completo (Resposta curta, obrigatório)")
        print("   - E-mail (E-mail, opcional)")
        print("   - Cargo (Resposta curta, opcional)")
        
        print("\n📊 Passo 2: Configurar Google Sheets")
        print("1. No Google Forms, clique em 'Respostas'")
        print("2. Clique no ícone do Google Sheets")
        print("3. Crie uma nova planilha")
        print("4. Copie a URL da planilha criada")
        
        forms_url = input("\nCole a URL da planilha de respostas: ").strip()
        
        # Converter URL para formato de exportação
        if "/edit" in forms_url:
            file_id = forms_url.split("/d/")[1].split("/")[0]
            export_url = f"https://docs.google.com/spreadsheets/d/{file_id}/export?format=csv"
        else:
            export_url = forms_url
        
        config = {
            "forms_url": forms_url,
            "export_url": export_url,
            "configurado_em": datetime.now().isoformat(),
            "ultima_verificacao": None,
            "mapeamento_colunas": {
                "timestamp": "Carimbo de data/hora",
                "matricula": "Matrícula",
                "nome": "Nome Completo",
                "email": "E-mail",
                "cargo": "Cargo"
            }
        }
        
        # Salvar configuração
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        print("✅ Configuração salva!")
        print(f"📄 Arquivo: {self.config_file}")
        
        return config
    
    def carregar_config(self):
        """Carrega configuração salva"""
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None
    
    def carregar_ultimo_processamento(self):
        """Carrega informações do último processamento"""
        if os.path.exists(self.ultimo_processamento):
            with open(self.ultimo_processamento, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"ultimo_timestamp": None, "processados": []}
    
    def salvar_ultimo_processamento(self, dados):
        """Salva informações do último processamento"""
        with open(self.ultimo_processamento, 'w', encoding='utf-8') as f:
            json.dump(dados, f, indent=2, ensure_ascii=False)
    
    def baixar_respostas_forms(self, export_url):
        """Baixa respostas do Google Forms via CSV"""
        try:
            response = requests.get(export_url, timeout=30)
            response.raise_for_status()
            
            # Salvar CSV temporário
            csv_temp = "temp_forms.csv"
            with open(csv_temp, 'wb') as f:
                f.write(response.content)
            
            # Ler como DataFrame
            df = pd.read_csv(csv_temp, encoding='utf-8')
            os.remove(csv_temp)
            
            return df
            
        except Exception as e:
            print(f"❌ Erro ao baixar respostas: {e}")
            return None
    
    def processar_novas_respostas(self):
        """Processa novas respostas do formulário"""
        config = self.carregar_config()
        if not config:
            print("❌ Configuração não encontrada. Execute: configurar_forms()")
            return 0
        
        print("🔄 Verificando novas respostas do Google Forms...")
        
        # Baixar respostas
        df_respostas = self.baixar_respostas_forms(config["export_url"])
        if df_respostas is None or df_respostas.empty:
            print("📭 Nenhuma resposta encontrada")
            return 0
        
        # Carregar último processamento
        ultimo_proc = self.carregar_ultimo_processamento()
        ultimo_timestamp = ultimo_proc.get("ultimo_timestamp")
        processados = set(ultimo_proc.get("processados", []))
        
        # Mapear colunas
        mapeamento = config["mapeamento_colunas"]
        
        # Filtrar apenas novas respostas
        novas_respostas = []
        novo_timestamp = ultimo_timestamp
        
        for _, row in df_respostas.iterrows():
            # Usar timestamp ou índice como identificador único
            timestamp_resposta = str(row.get(mapeamento["timestamp"], ""))
            identificador = f"{row.get(mapeamento['matricula'], '')}_{timestamp_resposta}"
            
            # Verificar se já foi processada
            if identificador not in processados:
                if not ultimo_timestamp or timestamp_resposta > ultimo_timestamp:
                    novas_respostas.append({
                        "identificador": identificador,
                        "timestamp": timestamp_resposta,
                        "matricula": self._limpar_matricula(row.get(mapeamento["matricula"], "")),
                        "nome": str(row.get(mapeamento["nome"], "")).strip(),
                        "email": str(row.get(mapeamento["email"], "")).strip(),
                        "cargo": str(row.get(mapeamento["cargo"], "")).strip()
                    })
                    
                    # Atualizar último timestamp
                    if not novo_timestamp or timestamp_resposta > novo_timestamp:
                        novo_timestamp = timestamp_resposta
        
        if not novas_respostas:
            print("✅ Nenhuma resposta nova para processar")
            return 0
        
        print(f"📥 {len(novas_respostas)} nova(s) resposta(s) encontrada(s)")
        
        # Carregar planilha FUNC.xlsx
        func_file = os.path.join(self.base_dir, "FUNC.xlsx")
        if os.path.exists(func_file):
            df_func = pd.read_excel(func_file)
        else:
            df_func = pd.DataFrame(columns=['matricula', 'nome', 'Coluna2'])
        
        # Processar cada resposta
        adicionados = 0
        for resposta in novas_respostas:
            try:
                matricula = resposta["matricula"]
                nome = resposta["nome"]
                
                # Validações
                if not matricula or not nome:
                    print(f"⚠️ Resposta incompleta ignorada: {resposta}")
                    continue
                
                # Verificar se matrícula já existe
                if 'matricula' in df_func.columns and matricula in df_func['matricula'].values:
                    print(f"⚠️ Matrícula {matricula} já existe, ignorando")
                    processados.add(resposta["identificador"])
                    continue
                
                # Criar novo registro
                novo_funcionario = {
                    'matricula': matricula,
                    'nome': nome,
                    'Coluna2': str(uuid.uuid4()),  # Stakeholder ID
                    'email': resposta["email"] if resposta["email"] else "",
                    'cargo': resposta["cargo"] if resposta["cargo"] else "",
                    'origem': 'Google Forms',
                    'adicionado_em': datetime.now().isoformat()
                }
                
                # Adicionar colunas que existem no DataFrame original
                for col in df_func.columns:
                    if col not in novo_funcionario:
                        novo_funcionario[col] = ""
                
                # Adicionar ao DataFrame
                df_func = pd.concat([df_func, pd.DataFrame([novo_funcionario])], ignore_index=True)
                
                print(f"✅ Funcionário adicionado: {nome} (Matrícula: {matricula})")
                adicionados += 1
                processados.add(resposta["identificador"])
                
            except Exception as e:
                print(f"❌ Erro ao processar resposta: {e}")
                continue
        
        # Salvar planilha atualizada
        if adicionados > 0:
            try:
                df_func.to_excel(func_file, index=False)
                print(f"💾 Planilha FUNC.xlsx atualizada com {adicionados} novo(s) funcionário(s)")
            except Exception as e:
                print(f"❌ Erro ao salvar planilha: {e}")
                return 0
        
        # Salvar último processamento
        self.salvar_ultimo_processamento({
            "ultimo_timestamp": novo_timestamp,
            "processados": list(processados),
            "ultima_verificacao": datetime.now().isoformat(),
            "total_processados": len(processados)
        })
        
        # Atualizar config com última verificação
        config["ultima_verificacao"] = datetime.now().isoformat()
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        return adicionados
    
    def _limpar_matricula(self, matricula):
        """Limpa e converte matrícula para formato padrão"""
        if pd.isna(matricula):
            return None
        
        try:
            # Remover pontuação e espaços
            matricula_limpa = str(matricula).replace('.', '').replace(',', '').replace(' ', '').strip()
            
            # Converter para inteiro se possível
            if matricula_limpa.isdigit():
                return int(matricula_limpa)
            else:
                return matricula_limpa
        except:
            return str(matricula).strip()
    
    def monitorar_forms(self, intervalo_minutos=5):
        """Monitora Google Forms continuamente"""
        print(f"👁️ Iniciando monitoramento do Google Forms (verificação a cada {intervalo_minutos} minutos)")
        
        while True:
            try:
                adicionados = self.processar_novas_respostas()
                
                if adicionados > 0:
                    print(f"🎉 {adicionados} funcionário(s) adicionado(s)!")
                else:
                    print("✅ Verificação concluída, nenhuma novidade")
                
                print(f"⏰ Próxima verificação em {intervalo_minutos} minutos...")
                time.sleep(intervalo_minutos * 60)
                
            except KeyboardInterrupt:
                print("\n🛑 Monitoramento interrompido pelo usuário")
                break
            except Exception as e:
                print(f"❌ Erro no monitoramento: {e}")
                print(f"⏰ Tentando novamente em {intervalo_minutos} minutos...")
                time.sleep(intervalo_minutos * 60)

def main():
    """Função principal"""
    integrador = IntegradorGoogleForms()
    
    print("📝 Integração com Google Forms")
    print("=" * 50)
    print("1. Configurar Google Forms")
    print("2. Processar respostas agora")
    print("3. Monitorar continuamente")
    print("4. Ver configuração atual")
    
    opcao = input("\nEscolha uma opção (1-4): ").strip()
    
    if opcao == "1":
        integrador.configurar_forms()
        
    elif opcao == "2":
        adicionados = integrador.processar_novas_respostas()
        print(f"\n🎉 Processamento concluído! {adicionados} funcionário(s) adicionado(s)")
        
    elif opcao == "3":
        intervalo = input("Intervalo em minutos (padrão 5): ").strip()
        intervalo = int(intervalo) if intervalo.isdigit() else 5
        integrador.monitorar_forms(intervalo)
        
    elif opcao == "4":
        config = integrador.carregar_config()
        if config:
            print("\n📋 Configuração atual:")
            print(f"URL do Forms: {config.get('forms_url', 'N/A')}")
            print(f"Configurado em: {config.get('configurado_em', 'N/A')}")
            print(f"Última verificação: {config.get('ultima_verificacao', 'Nunca')}")
            
            ultimo_proc = integrador.carregar_ultimo_processamento()
            print(f"Total processados: {len(ultimo_proc.get('processados', []))}")
        else:
            print("❌ Nenhuma configuração encontrada")
    
    else:
        print("❌ Opção inválida")

if __name__ == "__main__":
    main()