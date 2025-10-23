"""
Configurações seguras do sistema
Este arquivo contém configurações sensíveis que não devem ser commitadas
"""

import os
from typing import Dict, Any

class ConfigSegura:
    """Classe para gerenciar configurações seguras"""
    
    def __init__(self):
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

# Instância global das configurações
config = ConfigSegura()

# Exemplo de uso:
if __name__ == "__main__":
    print("Configurações carregadas:")
    print(f"Database Host: {config.get('DATABASE.HOST')}")
    print(f"API URL: {config.get('API.BASE_URL')}")
    print(f"Upload Dir: {config.get('FILES.UPLOAD_DIR')}")