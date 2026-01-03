"""
Injeção de Dependências (FUSÃO FINAL)

CORREÇÃO FINAL: Injeta o UserMapper no SQLUserRepository.
"""
from typing import Dict, Any, Optional, Generator, AsyncGenerator
from uuid import UUID
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
import logging

# Passo 4.3: A Conexão
from data.database import SessionLocal, engine
# Passo 4.4: O Repositório (Arquivista)
from data.users.sql_user_repository import SQLUserRepository
# Passo 4.2: O Tradutor
from data.users.user_mapper import UserMapper
# Passo 5.1: O Serviço (Gerente)
from services.user_service import UserService
# Stubs (para que as importações funcionem)
from data.mongo_repository import (
    UserPreferencesMongoRepository, 
    ActivityLogMongoRepository
)

logger = logging.getLogger(__name__)
security = HTTPBearer()

# --- PARTE 1: Novo "Encanamento" da Aplicação (Passos 4 e 5) ---

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Obtém uma sessão do banco de dados (SQLAlchemy Session) 
    para uma única requisição.
    """
    async with SessionLocal() as db:
        try:
            yield db
        except Exception:
            await db.rollback()
            raise


def get_user_mapper() -> UserMapper:
    """Cria e injeta o Tradutor (Mapper)."""
    return UserMapper()

def get_sql_user_repository(
    db: AsyncSession = Depends(get_db),
    # CORREÇÃO CRÍTICA AQUI:
    # O "Arquivista" (SQLUserRepository) agora recebe o "Tradutor" (UserMapper).
    mapper: UserMapper = Depends(get_user_mapper)
) -> SQLUserRepository:
    """Cria e injeta o Repositório de Usuário (SQL)."""
    return SQLUserRepository(db=db, mapper=mapper)

# Stubs para os repositórios Mongo (para que o UserService possa ser inicializado)
def get_user_preferences_repository() -> UserPreferencesMongoRepository:
    return UserPreferencesMongoRepository()

def get_activity_log_repository() -> ActivityLogMongoRepository:
    return ActivityLogMongoRepository()

def get_user_service(
    user_repo: SQLUserRepository = Depends(get_sql_user_repository),
    prefs_repo: UserPreferencesMongoRepository = Depends(get_user_preferences_repository),
    activity_repo: ActivityLogMongoRepository = Depends(get_activity_log_repository)
) -> UserService:
    """Cria e injeta o Serviço de Usuário com todas as suas dependências."""
    return UserService(
        user_repo=user_repo,
        prefs_repo=prefs_repo,
        activity_repo=activity_repo
    )


# --- PARTE 2: Dependências de Autenticação Antigas (Refatoradas) ---

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    user_service: UserService = Depends(get_user_service) 
) -> Dict[str, Any]:
    """Obter usuário atual a partir do token JWT"""
    try:
        token_data = await user_service.verify_token(credentials.credentials)
        
        if not token_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        token_data["user_id"] = UUID(token_data["user_id"])
        return token_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting current user: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[Dict[str, Any]]:
    """Obter usuário atual (opcional) - para endpoints públicos"""
    if not credentials:
        return None
    
    try:
        return await get_current_user(credentials)
    except HTTPException:
        return None


def require_subscription(subscription_types: list = ["pro"]):
    """Decorator para exigir tipos específicos de assinatura"""
    async def subscription_dependency(
        current_user: Dict[str, Any] = Depends(get_current_user)
    ) -> Dict[str, Any]:
        
        user_subscription = current_user["user"].subscription_type.value
        
        if user_subscription not in subscription_types:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"This feature requires {' or '.join(subscription_types)} subscription"
            )
        
        return current_user
    
    return subscription_dependency


def require_admin():
    """Decorator para exigir permissões de administrador"""
    async def admin_dependency(
        current_user: Dict[str, Any] = Depends(get_current_user)
    ) -> Dict[str, Any]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    return admin_dependency