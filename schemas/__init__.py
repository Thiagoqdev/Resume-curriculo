"""
Schemas para a arquitetura IT Valley
"""
from .requests import *
from .responses import *

__all__ = [
    # Requests
    "UserRegisterRequest",
    "UserLoginRequest", 
    "PasswordChangeRequest",
    "ResumeCreateRequest",
    "AnalysisCreateRequest",
    # Responses
    "UserProfileResponse",
    "TokenResponse",
    "ResumeResponse",
    "AnalysisResponse"
]
