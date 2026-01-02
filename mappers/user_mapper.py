"""
Mapper para usuários
Seguindo padrão IT Valley
"""
from typing import Optional
from datetime import datetime

from domain.entities.domain import User
from schemas.responses.user_responses import UserProfileResponse, UserResponse


class UserMapper:
    """Mapper para conversão de usuários"""
    
    @staticmethod
    def to_public(user: User) -> UserProfileResponse:
        """
        Converte entidade User para resposta pública
        
        Args:
            user: Entidade User
            
        Returns:
            Resposta pública do usuário
        """
        return UserProfileResponse(
            user_id=user.user_id,
            email=user.email,
            full_name=user.full_name,
            phone=user.phone,
            avatar_url=user.avatar_url,
            subscription_type=user.subscription_type,
            created_at=user.created_at,
            last_login_at=user.last_login_at,
            email_verified=user.email_verified,
            two_factor_enabled=user.two_factor_enabled
        )
    
    @staticmethod
    def to_display(user: User) -> dict:
        """
        Converte entidade User para exibição simples
        
        Args:
            user: Entidade User
            
        Returns:
            Dados para exibição
        """
        return {
            "id": str(user.user_id),
            "name": user.full_name,
            "email": user.email,
            "subscription": user.subscription_type.value,
            "is_active": user.is_active
        }
    
    @staticmethod
    def to_list_item(user: User) -> dict:
        """
        Converte entidade User para item de lista
        
        Args:
            user: Entidade User
            
        Returns:
            Item de lista
        """
        return {
            "user_id": str(user.user_id),
            "full_name": user.full_name,
            "email": user.email,
            "subscription_type": user.subscription_type.value,
            "is_active": user.is_active,
            "created_at": user.created_at,
            "last_login_at": user.last_login_at
        }
    
    @staticmethod
    def to_admin_view(user: User) -> dict:
        """
        Converte entidade User para visão administrativa
        
        Args:
            user: Entidade User
            
        Returns:
            Dados administrativos
        """
        return {
            "user_id": str(user.user_id),
            "email": user.email,
            "full_name": user.full_name,
            "phone": user.phone,
            "subscription_type": user.subscription_type.value,
            "is_active": user.is_active,
            "email_verified": user.email_verified,
            "two_factor_enabled": user.two_factor_enabled,
            "created_at": user.created_at,
            "updated_at": user.updated_at,
            "last_login_at": user.last_login_at
        }
    
    @staticmethod
    def to_export(user: User) -> dict:
        """
        Converte entidade User para exportação
        
        Args:
            user: Entidade User
            
        Returns:
            Dados para exportação
        """
        return {
            "id": str(user.user_id),
            "email": user.email,
            "full_name": user.full_name,
            "phone": user.phone,
            "subscription_type": user.subscription_type.value,
            "is_active": user.is_active,
            "email_verified": user.email_verified,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "last_login_at": user.last_login_at.isoformat() if user.last_login_at else None
        }
    
    @staticmethod
    def to_statistics(user: User, stats: dict) -> dict:
        """
        Converte entidade User com estatísticas
        
        Args:
            user: Entidade User
            stats: Estatísticas do usuário
            
        Returns:
            Dados com estatísticas
        """
        return {
            "user": UserMapper.to_public(user),
            "statistics": {
                "total_resumes": stats.get("total_resumes", 0),
                "total_analyses": stats.get("total_analyses", 0),
                "average_match_score": stats.get("average_match_score", 0.0),
                "last_activity": stats.get("last_activity"),
                "subscription_usage": stats.get("subscription_usage", {})
            }
        }
    
    @staticmethod
    def to_minimal(user: User) -> dict:
        """
        Converte entidade User para dados mínimos
        
        Args:
            user: Entidade User
            
        Returns:
            Dados mínimos
        """
        return {
            "user_id": str(user.user_id),
            "full_name": user.full_name,
            "email": user.email
        }
    
    @staticmethod
    def to_activity_log(user: User, action: str, details: dict = None) -> dict:
        """
        Converte entidade User para log de atividade
        
        Args:
            user: Entidade User
            action: Ação realizada
            details: Detalhes da ação
            
        Returns:
            Log de atividade
        """
        return {
            "user_id": str(user.user_id),
            "user_name": user.full_name,
            "user_email": user.email,
            "action": action,
            "timestamp": datetime.utcnow(),
            "details": details or {}
        }
