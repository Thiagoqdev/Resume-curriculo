"""
Endpoints de Autenticação (Refatorados para Injeção de Dependência)

Este ficheiro funde as rotas antigas com o novo sistema de injeção
(Passo 5.1 e 5.2) para USR-001 e USR-005.
"""
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import logging

# Passo 1: DTOs de Request (Refatorados por si no Canvas)
from schemas.users.requests import (
    UserCreateRequest, 
    UserLoginRequest, 
    ChangePasswordRequest
)

# DTOs de Resposta (Refatorados por si no Canvas)
from schemas.responses.responses import (
    BaseResponse, 
    TokenResponse, 
    UserProfileResponse
)

# Passo 5.1: Serviço
from services.user_service import UserService

# Passo 5.2 (FUSÃO FINAL): Injeção de Dependência
from core.dependencies import get_current_user, get_user_service

logger = logging.getLogger(__name__)

# Corrigindo o prefixo para corresponder ao README.md
router = APIRouter(prefix="/auth", tags=["Autenticação"])

# NOTA: O 'security = HTTPBearer()' já não é necessário aqui,
# pois foi movido para 'core/dependencies.py' (FUSÃO FINAL).


@router.post(
    "/register", 
    response_model=UserProfileResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar Novo Usuário (USR-001)"
)
async def register_user(
    request: UserCreateRequest,
    # INJEÇÃO: Substitui user_service = UserService()
    user_service: UserService = Depends(get_user_service)
):
    """Registrar novo usuário"""
    try:
        # REMOVIDO: user_service = UserService()
        user_profile = await user_service.register_user(request)
        return user_profile
        
    except ValueError as e:
        logger.warning(f"Falha no registo (400): {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error in register_user: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.post(
    "/login", 
    response_model=TokenResponse,
    summary="Autenticar Usuário e Obter JWT (USR-005)"
)
async def login_user(
    request: UserLoginRequest,
    # INJEÇÃO: Substitui user_service = UserService()
    user_service: UserService = Depends(get_user_service)
):
    """Autenticar usuário"""
    try:
        # REMOVIDO: user_service = UserService()
        token_response = await user_service.authenticate_user(request)
        return token_response
        
    except ValueError as e:
        logger.warning(f"Falha no login (401) para {request.email}: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"}
        )
    except Exception as e:
        logger.error(f"Error in login_user: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
    # INJEÇÃO: Substitui user_service = UserService()
    user_service: UserService = Depends(get_user_service)
):
    """Renovar token de acesso"""
    try:
        # REMOVIDO: user_service = UserService()
        token_response = await user_service.refresh_token(credentials.credentials)
        
        if not token_response:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        return token_response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in refresh_token: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/profile", response_model=UserProfileResponse)
async def get_user_profile(
    # A dependência get_current_user (da FUSÃO FINAL) funciona agora
    current_user: Dict[str, Any] = Depends(get_current_user),
    # INJEÇÃO: Substitui user_service = UserService()
    user_service: UserService = Depends(get_user_service)
):
    """Obter perfil do usuário autenticado"""
    try:
        # REMOVIDO: user_service = UserService()
        
        # Usamos o ID do token para buscar o perfil
        user_id = current_user["user_id"]
        user_profile = await user_service.get_user_profile(user_id)
        
        if not user_profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return user_profile
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_user_profile: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.post("/change-password", response_model=BaseResponse)
async def change_password(
    request: ChangePasswordRequest, # Corrigido para o DTO do Passo 1
    current_user: Dict[str, Any] = Depends(get_current_user),
    # INJEÇÃO: Substitui user_service = UserService()
    user_service: UserService = Depends(get_user_service)
):
    """Alterar senha do usuário"""
    try:
        # REMOVIDO: user_service = UserService()
        success = await user_service.change_password(
            current_user["user_id"],
            request.current_password,
            request.new_password
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to change password"
            )
        
        return BaseResponse(
            success=True,
            message="Password changed successfully"
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error in change_password: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.post("/logout", response_model=BaseResponse)
async def logout_user(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Logout do usuário (invalidar token)"""
    try:
        # Em uma implementação real, você invalidaria o token no Redis/cache
        # Por enquanto, apenas retornamos sucesso
        
        return BaseResponse(
            success=True,
            message="Logged out successfully"
        )
        
    except Exception as e:
        logger.error(f"Error in logout_user: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/verify", response_model=BaseResponse)
async def verify_token(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Verificar se token é válido"""
    try:
        # Se get_current_user funcionou, o token é válido.
        return BaseResponse(
            success=True,
            message="Token is valid"
        )
        
    except Exception as e:
        logger.error(f"Error in verify_token: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

