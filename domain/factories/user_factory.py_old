"""
Factory para criação de usuários
Seguindo padrão IT Valley
"""
from typing import Any
from uuid import uuid4
from datetime import datetime

from domain.helpers import _get, email_from, name_from, phone_from, status_from
from domain.entities.domain import User, SubscriptionType


class UserFactory:
    """Factory para criação de usuários"""
    
    @staticmethod
    def make_user(dto: Any) -> User:
        """
        Cria um usuário a partir de um DTO
        
        Args:
            dto: DTO com dados do usuário
            
        Returns:
            Usuário criado
            
        Raises:
            ValueError: Se dados inválidos
        """
        # Extrair dados usando helpers
        email = email_from(dto)
        full_name = name_from(dto)
        phone = phone_from(dto)
        status = status_from(dto, "ativo")
        
        # Validações específicas
        if len(full_name) < 2:
            raise ValueError("Nome deve ter pelo menos 2 caracteres")
        
        if not email or "@" not in email:
            raise ValueError("Email deve ter formato válido")
        
        # Criar usuário
        return User(
            user_id=uuid4(),
            email=email.strip().lower(),
            full_name=full_name.strip(),
            phone=phone,
            password_hash="",  # Será definido pelo service
            subscription_type=SubscriptionType.FREE,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            is_active=True,
            email_verified=False,
            two_factor_enabled=False
        )
    
    @staticmethod
    def email_from(dto: Any) -> str:
        """
        Helper para extrair email do DTO
        
        Args:
            dto: DTO com email
            
        Returns:
            Email extraído
        """
        return email_from(dto)
    
    @staticmethod
    def name_from(dto: Any) -> str:
        """
        Helper para extrair nome do DTO
        
        Args:
            dto: DTO com nome
            
        Returns:
            Nome extraído
        """
        return name_from(dto)
    
    @staticmethod
    def phone_from(dto: Any) -> str:
        """
        Helper para extrair telefone do DTO
        
        Args:
            dto: DTO com telefone
            
        Returns:
            Telefone extraído
        """
        return phone_from(dto)
    
    @staticmethod
    def id_from(dto: Any) -> str:
        """
        Helper para extrair ID do DTO
        
        Args:
            dto: DTO com ID
            
        Returns:
            ID extraído
        """
        return _get(dto, "user_id") or _get(dto, "id")
    
    @staticmethod
    def make_user_update(dto: Any, existing_user: User) -> User:
        """
        Cria atualização de usuário
        
        Args:
            dto: DTO com dados de atualização
            existing_user: Usuário existente
            
        Returns:
            Usuário atualizado
        """
        # Aplicar atualizações usando método da entidade
        existing_user.aplicar_atualizacao_from_any(dto)
        existing_user.updated_at = datetime.utcnow()
        
        return existing_user
    
    @staticmethod
    def make_user_from_register(dto: Any) -> User:
        """
        Cria usuário a partir de registro
        
        Args:
            dto: DTO de registro
            
        Returns:
            Usuário criado
        """
        # Validações específicas de registro
        if not _get(dto, "password"):
            raise ValueError("Senha é obrigatória")
        
        if not _get(dto, "email"):
            raise ValueError("Email é obrigatório")
        
        if not _get(dto, "full_name"):
            raise ValueError("Nome completo é obrigatório")
        
        return UserFactory.make_user(dto)
    
    @staticmethod
    def make_user_from_login(dto: Any) -> dict:
        """
        Cria dados de login a partir de DTO
        
        Args:
            dto: DTO de login
            
        Returns:
            Dados de login
        """
        email = email_from(dto)
        password = _get(dto, "password")
        remember_me = _get(dto, "remember_me", False)
        
        if not password:
            raise ValueError("Senha é obrigatória")
        
        return {
            "email": email,
            "password": password,
            "remember_me": remember_me
        }
    
    @staticmethod
    def make_password_change(dto: Any) -> dict:
        """
        Cria dados de mudança de senha
        
        Args:
            dto: DTO de mudança de senha
            
        Returns:
            Dados de mudança de senha
        """
        current_password = _get(dto, "current_password")
        new_password = _get(dto, "new_password")
        
        if not current_password:
            raise ValueError("Senha atual é obrigatória")
        
        if not new_password:
            raise ValueError("Nova senha é obrigatória")
        
        if len(new_password) < 8:
            raise ValueError("Nova senha deve ter pelo menos 8 caracteres")
        
        return {
            "current_password": current_password,
            "new_password": new_password
        }
