"""
DTOs (Data Transfer Objects) para requisições (input) do domínio User.

Define as regras de validação para dados que chegam na API.
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional

# (Mantido do Passo 1)
class UserCreateRequest(BaseModel):
    """
    DTO para a requisição de criação de um novo usuário (Cadastro).
    """
    name: str = Field(min_length=2, max_length=255, description="Nome completo do usuário")
    email: EmailStr = Field(description="Email válido do usuário")
    password: str = Field(min_length=8, description="Senha com mínimo de 8 caracteres")

# --- ADICIONADO AGORA ---
class UserLoginRequest(BaseModel):
    """
    DTO para a requisição de login de um usuário (USR-005).
    Usado no endpoint de 'Login'.
    """
    email: EmailStr = Field(description="Email de login do usuário")
    password: str = Field(description="Senha do usuário")
    remember_me: bool = False # Campo do DTO antigo, mantido por consistência

# (Mantido do Passo 1)
class UserUpdateRequest(BaseModel):
    """
    DTO para a requisição de atualização de perfil.
    """
    name: Optional[str] = Field(default=None, min_length=2, max_length=255)
    avatar_url: Optional[str] = Field(default=None, max_length=1024)

# (Mantido do Passo 1)
class ChangePasswordRequest(BaseModel):
    """
    DTO para a requisição de mudança de senha.
    """
    current_password: str = Field(min_length=8)
    new_password: str = Field(min_length=8)

# (Mantido do Passo 1)
class UserSearchRequest(BaseModel):
    """
    DTO para parâmetros de busca de usuários (ex: admin).
    """
    query: Optional[str] = Field(default=None)
    page: int = 1
    page_size: int = 20
