"""
DTOs para requisições da API
Seguindo padrão IT Valley
"""
from .requests import (
    UserRegisterRequest,
    UserLoginRequest,
    PasswordChangeRequest,
    ResumeCreateRequest,
    AnalysisCreateRequest
)

__all__ = [
    "UserRegisterRequest",
    "UserLoginRequest", 
    "PasswordChangeRequest",
    "ResumeCreateRequest",
    "AnalysisCreateRequest"
]
