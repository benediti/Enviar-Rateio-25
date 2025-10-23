"""
Configurações seguras do sistema
Este arquivo contém configurações sensíveis que não devem ser commitadas
"""

import os
import json
from typing import Dict, Any, List, Tuple, Optional

class ConfigSegura:
    """Classe para gerenciar configurações seguras"""
    
    def __init__(self):
        self.config_file = "config_api.json"
        self.config = {
            # Configurações de banco de dados
            "DATABASE": {
                "HOST": os.getenv("DB_HOST", "localhost"),
                "PORT": os.getenv("DB_PORT", "5432"),
                "NAME": os.getenv("DB_NAME", "rateio_db"),
                "USER": os.getenv("DB_USER", "usuario"),
                "PASSWORD": os.getenv("DB_PASSWORD", "senha123")
            },
            
            # Configurações de API
            "API": {
                "BASE_URL": os.getenv("API_BASE_URL", "https://api.exemplo.com"),
                "API_KEY": os.getenv("API_KEY", "sua_api_key_aqui"),
                "TIMEOUT": int(os.getenv("API_TIMEOUT", "30"))
            },
            
            # Configurações de email
            "EMAIL": {
                "SMTP_SERVER": os.getenv("SMTP_SERVER", "smtp.gmail.com"),
                "SMTP_PORT": int(os.getenv("SMTP_PORT", "587")),
                "EMAIL_USER": os.getenv("EMAIL_USER", "seu_email@example.com"),
                "EMAIL_PASSWORD": os.getenv("EMAIL_PASSWORD", "sua_senha"),
                "USE_TLS": os.getenv("EMAIL_USE_TLS", "True").lower() == "true"
            },
            
            # Configurações de arquivos
            "FILES": {
                "UPLOAD_DIR": os.getenv("UPLOAD_DIR", "./uploads"),
                "MAX_FILE_SIZE": int(os.getenv("MAX_FILE_SIZE", "10485760")),  # 10MB
                "ALLOWED_EXTENSIONS": ["xlsx", "xls", "csv"]
            },
            
            # Configurações do Nibo
            "NIBO": {
                "API_URL": os.getenv("NIBO_API_URL", "https://api.nibo.com.br"),
                "CLIENT_ID": os.getenv("NIBO_CLIENT_ID", "seu_client_id"),
                "CLIENT_SECRET": os.getenv("NIBO_CLIENT_SECRET", "seu_client_secret"),
                "REDIRECT_URI": os.getenv("NIBO_REDIRECT_URI", "http://localhost:8501/callback")
            }
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Obtém uma configuração usando notação de ponto
        Exemplo: config.get("DATABASE.HOST")
        """
        keys = key.split(".")
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def get_database_url(self) -> str:
        """Retorna a URL de conexão com o banco de dados"""
        db_config = self.config["DATABASE"]
        return f"postgresql://{db_config['USER']}:{db_config['PASSWORD']}@{db_config['HOST']}:{db_config['PORT']}/{db_config['NAME']}"
    
    def get_api_headers(self) -> Dict[str, str]:
        """Retorna os headers padrão para requisições da API"""
        return {
            "Authorization": f"Bearer {self.config['API']['API_KEY']}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
    
    def listar_perfis(self) -> List[str]:
        """Lista os perfis salvos de configuração da API"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                return list(data.keys())
        except Exception:
            pass
        return []
    
    def carregar_config(self, perfil: str = "default") -> Tuple[Optional[str], Optional[str]]:
        """Carrega configuração da API de um perfil específico"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                if perfil in data:
                    config = data[perfil]
                    return config.get('api_url'), config.get('api_token')
        except Exception:
            pass
        return None, None
    
    def salvar_config(self, api_url: str, api_token: str, perfil: str = "default") -> bool:
        """Salva configuração da API em um perfil"""
        try:
            data = {}
            if os.path.exists(self.config_file):
                try:
                    with open(self.config_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                except:
                    data = {}
            
            data[perfil] = {
                'api_url': api_url,
                'api_token': api_token
            }
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception:
            return False

# Instância global das configurações
config = ConfigSegura()

# Exemplo de uso:
if __name__ == "__main__":
    print("Configurações carregadas:")
    print(f"Database Host: {config.get('DATABASE.HOST')}")
    print(f"API URL: {config.get('API.BASE_URL')}")
    print(f"Upload Dir: {config.get('FILES.UPLOAD_DIR')}")