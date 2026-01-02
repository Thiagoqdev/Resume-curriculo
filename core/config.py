"""
Configurações da aplicação SkillSync
"""
from typing import Optional, List
from pydantic import BaseModel, validator
from pydantic_settings import BaseSettings
from decouple import config
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    """Configurações principais da aplicação"""
    
    # Aplicação
    APP_NAME: str = "SkillSync API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = config("DEBUG", default=False, cast=bool)
    API_V1_STR: str = "/api/v1"
    
    # Servidor
    HOST: str = config("HOST", default="0.0.0.0")
    PORT: int = config("PORT", default=8000, cast=int)
    
    # Segurança
    SECRET_KEY: str = config("SECRET_KEY", default="your-secret-key-here")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "https://skillsync.app"
    ]
    
    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v):
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    # SQL Server - String de conexão completa (prioridade)
    AZURE_SQL_CONNECTION_STRING: Optional[str] = config("AZURE_SQL_CONNECTION_STRING", default=None)
    
    # SQL Server - Configuração antiga (fallback para compatibilidade)
    SQL_SERVER: str = config("SQL_SERVER", default="localhost")
    SQL_DATABASE: str = config("SQL_DATABASE", default="SkillSync")
    SQL_USERNAME: str = config("SQL_USERNAME", default="sa")
    SQL_PASSWORD: str = config("SQL_PASSWORD", default="")
    SQL_DRIVER: str = config("SQL_DRIVER", default="ODBC Driver 18 for SQL Server")
    
    @property
    def sql_connection_string(self) -> str:
        """
        Retorna a string de conexão SQL.
        Prioriza AZURE_SQL_CONNECTION_STRING se disponível,
        caso contrário, constrói a partir das variáveis individuais.
        """
        # Prioridade: usar string de conexão completa se disponível
        if self.AZURE_SQL_CONNECTION_STRING:
            # Garantir que use mssql+aioodbc para assíncrono
            conn_str = self.AZURE_SQL_CONNECTION_STRING
            if conn_str.startswith("mssql+pyodbc://"):
                conn_str = conn_str.replace("mssql+pyodbc://", "mssql+aioodbc://", 1)
            return conn_str
        
        # Fallback: construir a partir das variáveis individuais
        driver_str = self.SQL_DRIVER.replace(' ', '+')
        return (
            f"mssql+aioodbc://{self.SQL_USERNAME}:{self.SQL_PASSWORD}"
            f"@{self.SQL_SERVER}/{self.SQL_DATABASE}"
            f"?driver={driver_str}"
            f"&TrustServerCertificate=yes"
        )
    
    # MongoDB
    MONGO_URL: str = config("MONGO_URL", default="mongodb://localhost:27017")
    MONGO_DATABASE: str = config("MONGO_DATABASE", default="skillsync")
    
    # Azure Blob Storage - String de conexão completa (prioridade)
    AZURE_STORAGE_CONNECTION_STRING: Optional[str] = config("AZURE_STORAGE_CONNECTION_STRING", default=None)
    
    # Azure Blob Storage - Configuração antiga (fallback para compatibilidade)
    AZURE_STORAGE_ACCOUNT: str = config("AZURE_STORAGE_ACCOUNT", default="")
    AZURE_STORAGE_KEY: str = config("AZURE_STORAGE_KEY", default="")
    AZURE_CONTAINER_NAME: str = config("AZURE_CONTAINER_NAME", default="skillsync-files")
    
    @property
    def azure_connection_string(self) -> str:
        """
        Retorna a string de conexão do Azure Storage.
        Prioriza AZURE_STORAGE_CONNECTION_STRING se disponível,
        caso contrário, constrói a partir das variáveis individuais.
        """
        # Prioridade: usar string de conexão completa se disponível
        if self.AZURE_STORAGE_CONNECTION_STRING:
            return self.AZURE_STORAGE_CONNECTION_STRING
        
        # Fallback: construir a partir das variáveis individuais
        if self.AZURE_STORAGE_ACCOUNT and self.AZURE_STORAGE_KEY:
            return (
                f"DefaultEndpointsProtocol=https;"
                f"AccountName={self.AZURE_STORAGE_ACCOUNT};"
                f"AccountKey={self.AZURE_STORAGE_KEY};"
                f"EndpointSuffix=core.windows.net"
            )
        
        return ""
    
    # Redis Cache
    REDIS_URL: str = config("REDIS_URL", default="redis://localhost:6379")
    CACHE_EXPIRE_SECONDS: int = config("CACHE_EXPIRE_SECONDS", default=3600, cast=int)
    
    # OpenAI
    OPENAI_API_KEY: str = config("OPENAI_API_KEY", default="")
    OPENAI_MODEL: str = config("OPENAI_MODEL", default="gpt-4-turbo-preview")
    
    # Azure Cognitive Services
    AZURE_TEXT_ANALYTICS_ENDPOINT: str = config("AZURE_TEXT_ANALYTICS_ENDPOINT", default="")
    AZURE_TEXT_ANALYTICS_KEY: str = config("AZURE_TEXT_ANALYTICS_KEY", default="")
    
    # Email
    SMTP_HOST: str = config("SMTP_HOST", default="smtp.gmail.com")
    SMTP_PORT: int = config("SMTP_PORT", default=587, cast=int)
    SMTP_USERNAME: str = config("SMTP_USERNAME", default="")
    SMTP_PASSWORD: str = config("SMTP_PASSWORD", default="")
    
    # Logging
    LOG_LEVEL: str = config("LOG_LEVEL", default="INFO")
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # File Upload
    MAX_FILE_SIZE: int = config("MAX_FILE_SIZE", default=50 * 1024 * 1024, cast=int)  # 50MB
    ALLOWED_FILE_TYPES: List[str] = [".pdf", ".doc", ".docx", ".txt"]
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = config("RATE_LIMIT_REQUESTS", default=100, cast=int)
    RATE_LIMIT_WINDOW: int = config("RATE_LIMIT_WINDOW", default=3600, cast=int)  # 1 hora
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Instância global das configurações
settings = Settings()


class DatabaseSettings:
    """Configurações específicas do banco de dados"""
    
    # SQL Server
    SQL_POOL_SIZE: int = 10
    SQL_MAX_OVERFLOW: int = 20
    SQL_POOL_TIMEOUT: int = 30
    SQL_POOL_RECYCLE: int = 3600
    
    # MongoDB
    MONGO_MIN_POOL_SIZE: int = 5
    MONGO_MAX_POOL_SIZE: int = 50
    MONGO_MAX_IDLE_TIME: int = 30000
    
    # Connection retry
    MAX_RETRIES: int = 3
    RETRY_DELAY: int = 1


db_settings = DatabaseSettings()


class AISettings:
    """Configurações para serviços de IA"""
    
    # OpenAI
    MAX_TOKENS: int = 4000
    TEMPERATURE: float = 0.7
    TOP_P: float = 1.0
    
    # Análise de currículo
    RESUME_ANALYSIS_PROMPT: str = """
    Analise o seguinte currículo e extraia as seguintes informações:
    1. Habilidades técnicas
    2. Experiência profissional
    3. Educação
    4. Certificações
    5. Idiomas
    
    Retorne em formato JSON estruturado.
    """
    
    # Análise de compatibilidade
    COMPATIBILITY_ANALYSIS_PROMPT: str = """
    Compare o currículo com a descrição da vaga e forneça:
    1. Score de compatibilidade (0-100)
    2. Pontos fortes
    3. Pontos fracos
    4. Recomendações de melhoria
    
    Seja específico e construtivo.
    """
    
    # Geração de cover letter
    COVER_LETTER_PROMPT: str = """
    Gere uma carta de apresentação profissional baseada no currículo e vaga.
    Inclua:
    1. Introdução personalizada
    2. Destaque das qualificações relevantes
    3. Demonstração de interesse na empresa
    4. Conclusão com call-to-action
    
    Tom: {tone}
    Tamanho: {length}
    """


ai_settings = AISettings()