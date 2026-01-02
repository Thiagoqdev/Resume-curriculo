"""
Respostas específicas para usuários
Seguindo padrão IT Valley
"""
from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel

from domain.entities.domain import SubscriptionType


class UserProfileResponse(BaseModel):
    """Resposta do perfil do usuário"""
    user_id: UUID
    email: str
    full_name: Optional[str] = None # Deve ser este campo
    phone: Optional[str] = None
    avatar_url: Optional[str] = None
    subscription_type: SubscriptionType
    created_at: datetime
    last_login_at: Optional[datetime] = None
    email_verified: bool
    two_factor_enabled: bool


class UserResponse(BaseModel):
    """Resposta básica do usuário"""
    user_id: UUID
    email: str
    full_name: str
    subscription_type: SubscriptionType
    is_active: bool
