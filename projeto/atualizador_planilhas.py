"""
Atualizador Automático de Planilhas
Sistema para sincronizar planilhas do Google Sheets ou OneDrive
"""

import pandas as pd
import requests
import os
from datetime import datetime
import time
import hashlib
from config_segura import ConfigSegura

class AtualizadorPlanilhas:
    """Classe para atualizar planilhas automaticamente"""
    
    def __init__(self):
        self.config = ConfigSegura()
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.urls_planilhas = {
            "FUNC.xlsx": None,  # URL do Google Sheets ou OneDrive
            "centros_de_custo.xlsx": None,
            "categorias_nibo.xlsx": None
        }
        self.hash_arquivos = {}
        self.carregar_urls()
    
    def carregar_urls(self):
        """Carrega URLs das planilhas online da configuração"""
        self.urls_planilhas["FUNC.xlsx"] = self.config.get("PLANILHAS.FUNC_URL")
        self.urls_planilhas["centros_de_custo.xlsx"] = self.config.get("PLANILHAS.CENTROS_URL")
        self.urls_planilhas["categorias_nibo.xlsx"] = self.config.get("PLANILHAS.CATEGORIAS_URL")
    
    def calcular_hash_arquivo(self, caminho_arquivo):
        """Calcula hash MD5 de um arquivo para detectar mudanças"""
        if not os.path.exists(caminho_arquivo):
            return None
        
        hash_md5 = hashlib.md5()
        with open(caminho_arquivo, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    def baixar_planilha_google_sheets(self, url_sheets):
        """
        Baixa planilha do Google Sheets
        URL deve estar no formato: https://docs.google.com/spreadsheets/d/ID/edit
        """
        if not url_sheets:
            return None
        
        try:
            # Converter URL para formato de export
            if "/edit" in url_sheets:
                file_id = url_sheets.split("/d/")[1].split("/")[0]
                export_url = f"https://docs.google.com/spreadsheets/d/{file_id}/export?format=xlsx"
            else:
                export_url = url_sheets
            
            response = requests.get(export_url, timeout=30)
            response.raise_for_status()
            return response.content
        
        except Exception as e:
            print(f"❌ Erro ao baixar planilha: {e}")
            return None
    
    def baixar_planilha_onedrive(self, url_onedrive):
        """
        Baixa planilha do OneDrive
        URL deve incluir o link de download direto
        """
        if not url_onedrive:
            return None
        
        try:
            # OneDrive precisa de URL de download direto
            if "1drv.ms" in url_onedrive or "onedrive.live.com" in url_onedrive:
                # Converter para URL de download
                if "?download=1" not in url_onedrive:
                    url_onedrive += "?download=1"
            
            response = requests.get(url_onedrive, timeout=30)
            response.raise_for_status()
            return response.content
        
        except Exception as e:
            print(f"❌ Erro ao baixar do OneDrive: {e}")
            return None
    
    def atualizar_planilha(self, nome_arquivo):
        """Atualiza uma planilha específica"""
        url = self.urls_planilhas.get(nome_arquivo)
        if not url:
            print(f"⚠️ URL não configurada para {nome_arquivo}")
            return False
        
        print(f"🔄 Verificando atualizações para {nome_arquivo}...")
        
        # Baixar conteúdo
        conteudo = None
        if "docs.google.com" in url:
            conteudo = self.baixar_planilha_google_sheets(url)
        elif "onedrive" in url or "1drv.ms" in url:
            conteudo = self.baixar_planilha_onedrive(url)
        else:
            # URL genérica
            try:
                response = requests.get(url, timeout=30)
                response.raise_for_status()
                conteudo = response.content
            except Exception as e:
                print(f"❌ Erro ao baixar {nome_arquivo}: {e}")
                return False
        
        if not conteudo:
            return False
        
        # Salvar arquivo temporário para comparação
        caminho_temp = os.path.join(self.base_dir, f"temp_{nome_arquivo}")
        with open(caminho_temp, "wb") as f:
            f.write(conteudo)
        
        # Verificar se houve mudança
        caminho_atual = os.path.join(self.base_dir, nome_arquivo)
        hash_novo = self.calcular_hash_arquivo(caminho_temp)
        hash_atual = self.calcular_hash_arquivo(caminho_atual)
        
        if hash_novo == hash_atual:
            os.remove(caminho_temp)
            print(f"✅ {nome_arquivo} já está atualizado")
            return False
        
        # Fazer backup do arquivo atual
        if os.path.exists(caminho_atual):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = os.path.join(self.base_dir, "backups", f"{nome_arquivo.replace('.xlsx', '')}_{timestamp}.xlsx")
            os.makedirs(os.path.dirname(backup_path), exist_ok=True)
            
            try:
                import shutil
                shutil.copy2(caminho_atual, backup_path)
                print(f"📦 Backup criado: {backup_path}")
            except:
                pass
        
        # Substituir arquivo
        if os.path.exists(caminho_atual):
            os.remove(caminho_atual)
        os.rename(caminho_temp, caminho_atual)
        
        # Validar novo arquivo
        try:
            df = pd.read_excel(caminho_atual)
            print(f"✅ {nome_arquivo} atualizado com sucesso! ({len(df)} registros)")
            
            # Mostrar mudanças
            if os.path.exists(caminho_atual.replace('.xlsx', f'_{datetime.now().strftime("%Y%m%d")}_old.xlsx')):
                try:
                    df_old = pd.read_excel(caminho_atual.replace('.xlsx', f'_{datetime.now().strftime("%Y%m%d")}_old.xlsx'))
                    if len(df) > len(df_old):
                        print(f"📈 +{len(df) - len(df_old)} novos registros adicionados")
                    elif len(df) < len(df_old):
                        print(f"📉 {len(df_old) - len(df)} registros removidos")
                except:
                    pass
            
            return True
            
        except Exception as e:
            print(f"❌ Erro ao validar {nome_arquivo}: {e}")
            return False
    
    def atualizar_todas_planilhas(self):
        """Atualiza todas as planilhas configuradas"""
        print("🔄 Iniciando atualização de todas as planilhas...")
        print("=" * 50)
        
        atualizacoes = 0
        for nome_arquivo in self.urls_planilhas.keys():
            if self.atualizar_planilha(nome_arquivo):
                atualizacoes += 1
            print("-" * 30)
        
        print("=" * 50)
        if atualizacoes > 0:
            print(f"✅ {atualizacoes} planilha(s) atualizada(s)")
        else:
            print("✅ Todas as planilhas já estão atualizadas")
        
        return atualizacoes
    
    def monitorar_continuamente(self, intervalo_minutos=5):
        """Monitora e atualiza planilhas continuamente"""
        print(f"👁️ Iniciando monitoramento contínuo (verificação a cada {intervalo_minutos} minutos)")
        
        while True:
            try:
                self.atualizar_todas_planilhas()
                print(f"⏰ Próxima verificação em {intervalo_minutos} minutos...")
                time.sleep(intervalo_minutos * 60)
            
            except KeyboardInterrupt:
                print("\n🛑 Monitoramento interrompido pelo usuário")
                break
            except Exception as e:
                print(f"❌ Erro no monitoramento: {e}")
                print(f"⏰ Tentando novamente em {intervalo_minutos} minutos...")
                time.sleep(intervalo_minutos * 60)

def configurar_urls_planilhas():
    """Função para configurar URLs das planilhas online"""
    config = ConfigSegura()
    
    print("🔧 Configuração de URLs das Planilhas Online")
    print("=" * 50)
    
    urls = {}
    
    print("\n📋 FUNC.xlsx - Funcionários")
    print("Cole a URL do Google Sheets ou OneDrive:")
    print("Google Sheets: https://docs.google.com/spreadsheets/d/ID/edit")
    print("OneDrive: https://1drv.ms/x/s!ID ou link direto")
    urls["FUNC_URL"] = input("URL: ").strip()
    
    print("\n🏢 centros_de_custo.xlsx - Centros de Custo")
    urls["CENTROS_URL"] = input("URL: ").strip()
    
    print("\n📂 categorias_nibo.xlsx - Categorias")
    urls["CATEGORIAS_URL"] = input("URL: ").strip()
    
    # Salvar configurações
    config_data = {}
    for key, url in urls.items():
        if url:
            config_data[f"PLANILHAS.{key}"] = url
    
    # Aqui você pode implementar salvamento na config_segura.py
    print("\n✅ URLs configuradas!")
    print("💡 Para que funcione automaticamente, adicione estas URLs no config_segura.py")
    for key, url in urls.items():
        if url:
            print(f'   "{key}": "{url}",')

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        comando = sys.argv[1]
        
        if comando == "config":
            configurar_urls_planilhas()
        elif comando == "monitorar":
            intervalo = int(sys.argv[2]) if len(sys.argv) > 2 else 5
            atualizador = AtualizadorPlanilhas()
            atualizador.monitorar_continuamente(intervalo)
        elif comando == "atualizar":
            atualizador = AtualizadorPlanilhas()
            atualizador.atualizar_todas_planilhas()
        else:
            print("Comandos disponíveis:")
            print("  python atualizador_planilhas.py config     - Configurar URLs")
            print("  python atualizador_planilhas.py atualizar  - Atualizar agora")
            print("  python atualizador_planilhas.py monitorar [minutos] - Monitorar continuamente")
    else:
        # Interface interativa
        atualizador = AtualizadorPlanilhas()
        print("🔄 Atualizador de Planilhas")
        print("1. Atualizar agora")
        print("2. Monitorar continuamente")
        print("3. Configurar URLs")
        
        opcao = input("Escolha (1-3): ").strip()
        
        if opcao == "1":
            atualizador.atualizar_todas_planilhas()
        elif opcao == "2":
            intervalo = input("Intervalo em minutos (padrão 5): ").strip()
            intervalo = int(intervalo) if intervalo.isdigit() else 5
            atualizador.monitorar_continuamente(intervalo)
        elif opcao == "3":
            configurar_urls_planilhas()