# data/database.py
import logging
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from core.config import settings, db_settings

# IMPORTANTE: Importar o módulo db_models para que todas as classes de modelo sejam registradas
import data.db_models # <--- ADICIONE ESTA LINHA

logger = logging.getLogger(__name__)

# 1. CONSTRUIR A URL DE CONEXÃO
try:
    DATABASE_URL = settings.sql_connection_string
except AttributeError:
    logger.critical("A 'sql_connection_string' não está definida no 'core/config.py'!")
    raise

# 2. CRIAR O "MOTOR" (ENGINE) ASSÍNCRONO
try:
    engine = create_async_engine(
        DATABASE_URL,
        pool_size=db_settings.SQL_POOL_SIZE,
        max_overflow=db_settings.SQL_MAX_OVERFLOW,
        pool_timeout=db_settings.SQL_POOL_TIMEOUT,
        pool_recycle=db_settings.SQL_POOL_RECYCLE,
        echo=settings.DEBUG
    )

    # 3. CRIAR O "CRIADOR DE SESSÕES"
    SessionLocal = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
        autocommit=False
    )

except Exception as e:
    logger.critical(f"Erro ao criar o engine do SQLAlchemy: {e}")
    raise