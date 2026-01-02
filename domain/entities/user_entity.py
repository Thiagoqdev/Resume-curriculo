# domain/entities/user_entity.py
from uuid import UUID, uuid4
from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
from typing import Optional, Any

class User(BaseModel):
    """
    Entidade de domínio principal para o Usuário.
    Define a estrutura e as regras de negócio.
    """
    id: UUID = Field(default_factory=uuid4)
    name: str # CORRIGIDO: De 'full_name' para 'name'
    email: EmailStr
    password: str
    phone: Optional[str] = None
    avatar_url: Optional[str] = None
    active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        from_attributes = True

    def rename(self, new_name: str) -> None: # CORRIGIDO: De 'new_full_name' para 'new_name'
        """Regra de negócio para renomear o usuário."""
        if not new_name or len(new_name.strip()) < 2:
            raise ValueError("Invalid name") # CORRIGIDO: Mensagem de erro
        self.name = new_name.strip() # CORRIGIDO: Atualiza 'self.name'
        self.updated_at = datetime.utcnow()

    def deactivate(self) -> None:
        """Regra de negócio para desativar o usuário."""
        self.active = False
        self.updated_at = datetime.utcnow()

    def reactivate(self) -> None:
        """Regra de negócio para reativar o usuário."""
        self.active = True
        self.updated_at = datetime.utcnow()

    # Se você tiver o método apply_update_from_any, ele precisará ser ajustado para usar 'name'
    # def apply_update_from_any(self, data: Any) -> None:
    #     from domain.helpers import _get
    #     new_name_val = _get(data, "name") # CORRIGIDO: Buscar 'name'
    #     new_avatar = _get(data, "avatar_url")
        
    #     if new_name_val is not None:
    #         self.rename(new_name_val)
            
    #     if new_avatar is not None:
    #         self.avatar_url = new_avatar
    #         self.updated_at = datetime.utcnow()