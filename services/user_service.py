"""
Serviço de Usuários (Refatorado para Injeção de Dependência)
"""
from typing import Optional, Dict, Any
from uuid import UUID, uuid4
from datetime import datetime, timedelta, UTC
import bcrypt # Importar bcrypt diretamente
from jose import JWTError, jwt
import logging

from core.config import settings
from domain.entities.user_entity import User
from domain.factories.user_factory import UserFactory
from schemas.users.requests import (
    UserCreateRequest, 
    UserLoginRequest,
    UserUpdateRequest,
    ChangePasswordRequest
)
from schemas.responses.responses import (
    UserProfileResponse, 
    TokenResponse,
    BaseResponse
)
from data.users.sql_user_repository import SQLUserRepository
from data.mongo_repository import (
    UserPreferencesMongoRepository, 
    ActivityLogMongoRepository
)

logger = logging.getLogger(__name__)


class UserService:
    def __init__(
        self,
        user_repo: SQLUserRepository,
        prefs_repo: UserPreferencesMongoRepository,
        activity_repo: ActivityLogMongoRepository
    ):
        self.user_repo = user_repo
        self.preferences_repo = prefs_repo
        self.activity_repo = activity_repo
        self.factory = UserFactory() # Instanciar a factory

    def _create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(UTC) + expires_delta
        else:
            expire = datetime.now(UTC) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt
    
    def _create_refresh_token(self, data: Dict[str, Any]) -> str:
        to_encode = data.copy()
        expire = datetime.now(UTC) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode.update({"exp": expire, "type": "refresh"})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt

    async def register_user(self, request: UserCreateRequest) -> UserProfileResponse:
        try:
            existing_user = await self.user_repo.get_user_by_email(request.email)
            if existing_user:
                raise ValueError("Email already registered")
            
            new_user_entity = self.factory.make(request)
            created_user = await self.user_repo.create_user(new_user_entity)
            
            try:
                default_prefs = {"userId": str(created_user.id), "defaultLanguage": "en"}
                await self.preferences_repo.create_user_preferences(default_prefs)
                logger.info("Stub: Criação de preferências ignorada.")
            except Exception as e:
                logger.error(f"Erro ao criar preferências (stub): {e}")
                pass
            
            try:
                log_entry = {"userId": str(created_user.id), "action": "user_registered"}
                await self.activity_repo.log_activity(log_entry)
            except Exception as e:
                logger.error(f"Erro ao logar atividade (stub): {e}")
                pass

            return UserProfileResponse(
                user_id=created_user.id,
                full_name=created_user.name, # CORRIGIDO: Mapeia created_user.name para full_name
                email=created_user.email,
                avatar_url=created_user.avatar_url,
                created_at=created_user.created_at,
                subscription_type="free", 
                last_login_at=None,
                email_verified=False,
                two_factor_enabled=False,
                phone=created_user.phone
            )
            
        except ValueError as e:
            logger.warning(f"Falha no registo (Value Error): {e}")
            raise e
        except Exception as e:
            logger.error(f"Erro ao registrar usuário: {e}", exc_info=True)
            raise ValueError(f"Internal error during registration: {e}")
    
    async def authenticate_user(self, request: UserLoginRequest) -> TokenResponse:
        try:
            user = await self.user_repo.get_user_by_email(request.email)
            if not user:
                raise ValueError("Invalid credentials")
            
            # CORRIGIDO: Usar bcrypt.checkpw diretamente
            if not bcrypt.checkpw(request.password.encode('utf-8'), user.password.encode('utf-8')):
                raise ValueError("Invalid credentials")
            
            if not user.active:
                raise ValueError("User account is disabled")
            
            access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = self._create_access_token(
                data={"sub": str(user.id), "email": user.email},
                expires_delta=access_token_expires
            )
            
            refresh_token = self._create_refresh_token(
                data={"sub": str(user.id), "email": user.email}
            )
            
            try:
                log_entry = {"userId": str(user.id), "action": "user_login"}
                await self.activity_repo.log_activity(log_entry)
            except Exception as e:
                logger.error(f"Erro ao logar atividade (stub): {e}")
                pass
            
            return TokenResponse(
                access_token=access_token,
                refresh_token=refresh_token,
                token_type="bearer",
                expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
            )
            
        except ValueError as e:
            logger.warning(f"Falha na autenticação para {request.email}: {e}")
            raise e
        except Exception as e:
            logger.error(f"Error authenticating user: {e}", exc_info=True)
            raise ValueError(f"Internal error during authentication: {e}")
    
    async def get_user_profile(self, user_id: UUID) -> Optional[UserProfileResponse]:
        try:
            user = await self.user_repo.get_user_by_id(user_id)
            if not user:
                return None
            
            return UserProfileResponse(
                user_id=user.id,
                full_name=user.name, # CORRIGIDO: Mapeia user.name para full_name
                email=user.email,
                avatar_url=user.avatar_url,
                created_at=user.created_at,
                subscription_type="free", 
                last_login_at=None,
                email_verified=False,
                two_factor_enabled=False,
                phone=user.phone
            )
            
        except Exception as e:
            logger.error(f"Error getting user profile: {e}", exc_info=True)
            return None
    
    async def update_user_profile(self, user_id: UUID, request: UserUpdateRequest) -> bool:
        try:
            user_entity = await self.user_repo.get_user_by_id(user_id)
            if not user_entity:
                return False
                
            update_data = {}
            if request.name:
                user_entity.rename(request.name)
            if request.avatar_url:
                user_entity.avatar_url = request.avatar_url
                user_entity.updated_at = datetime.now(UTC)
            if request.phone:
                user_entity.phone = request.phone
                user_entity.updated_at = datetime.now(UTC)
            
            success = await self.user_repo.update_user(user_id, user_entity)
            
            if success:
                try:
                    log_entry = {"userId": str(user_id), "action": "profile_updated"}
                    await self.activity_repo.log_activity(log_entry)
                except Exception as e:
                    logger.error(f"Erro ao logar atividade (stub): {e}")
                    pass
            
            return success
            
        except Exception as e:
            logger.error(f"Error updating user profile: {e}", exc_info=True)
            return False
    
    async def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            user_id: str = payload.get("sub")
            
            if user_id is None:
                return None
            
            user = await self.user_repo.get_user_by_id(UUID(user_id))
            if not user or not user.active:
                return None
            
            return {
                "user_id": user_id,
                "email": payload.get("email"),
                "user": user
            }
            
        except JWTError:
            logger.warning("Falha ao verificar JWT (JWTError)")
            return None
        except Exception as e:
            logger.error(f"Error verifying token: {e}", exc_info=True)
            return None
    
    async def refresh_token(self, refresh_token: str) -> Optional[TokenResponse]:
        try:
            payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            
            if payload.get("type") != "refresh":
                logger.warning("Falha no refresh: não é um refresh token")
                return None
            
            user_id: str = payload.get("sub")
            email: str = payload.get("email")
            
            if user_id is None or email is None:
                logger.warning("Falha no refresh: payload inválido")
                return None
            
            user = await self.user_repo.get_user_by_id(UUID(user_id))
            if not user or not user.active:
                logger.warning(f"Falha no refresh: utilizador {user_id} inativo ou não encontrado")
                return None
            
            access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = self._create_access_token(
                data={"sub": user_id, "email": email},
                expires_delta=access_token_expires
            )
            
            new_refresh_token = self._create_refresh_token(
                data={"sub": user_id, "email": email}
            )
            
            return TokenResponse(
                access_token=access_token,
                refresh_token=new_refresh_token,
                token_type="bearer",
                expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
            )
            
        except JWTError as e:
            logger.warning(f"Falha no refresh (JWTError): {e}")
            return None
        except Exception as e:
            logger.error(f"Error refreshing token: {e}", exc_info=True)
            return None
    
    async def change_password(self, user_id: UUID, current_password: str, new_password: str) -> bool:
        try:
            user = await self.user_repo.get_user_by_id(user_id)
            if not user:
                return False
            
            # CORRIGIDO: Usar bcrypt.checkpw diretamente
            if not bcrypt.checkpw(current_password.encode('utf-8'), user.password.encode('utf-8')):
                raise ValueError("Current password is incorrect")
            
            new_hash = UserFactory.hash_password(new_password)
            
            success = await self.user_repo.update_password_hash(user_id, new_hash) 
            
            if success:
                try:
                    log_entry = {"userId": str(user_id), "action": "password_changed"}
                    await self.activity_repo.log_activity(log_entry)
                except Exception as e:
                    logger.error(f"Erro ao logar atividade (stub): {e}")
                    pass
            
            return success
            
        except ValueError as e:
            logger.warning(f"password change failure: {e}")
            raise e
        except Exception as e:
            logger.error(f"Error changing password: {e}", exc_info=True)
            return False