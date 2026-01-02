"""
DTOs para requisições da API
Data Transfer Objects para entrada de dados
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field, validator
from domain.entities.domain import (
    SubscriptionType, ResumeStatus, JobType, 
    ExperienceLevel, NotificationType
)


# ===== AUTH DTOs =====

class UserRegisterRequest(BaseModel):
    """DTO para registro de usuário"""
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    full_name: str = Field(..., min_length=2, max_length=255)
    phone: Optional[str] = Field(None, max_length=50)
    
    @validator('password')
    def validate_password(cls, v):
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v


class UserLoginRequest(BaseModel):
    """DTO para login de usuário"""
    email: EmailStr
    password: str
    remember_me: bool = False


class PasswordChangeRequest(BaseModel):
    """DTO para alteração de senha"""
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=100)
    
    @validator('new_password')
    def validate_new_password(cls, v):
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v


class PasswordResetRequest(BaseModel):
    """DTO para solicitação de reset de senha"""
    email: EmailStr


class PasswordResetConfirmRequest(BaseModel):
    """DTO para confirmação de reset de senha"""
    token: str
    new_password: str = Field(..., min_length=8, max_length=100)


# ===== USER DTOs =====

class UserUpdateRequest(BaseModel):
    """DTO para atualização de usuário"""
    full_name: Optional[str] = Field(None, min_length=2, max_length=255)
    phone: Optional[str] = Field(None, max_length=50)
    avatar_url: Optional[str] = None


class UserPreferencesRequest(BaseModel):
    """DTO para preferências do usuário"""
    resume_preferences: Optional[Dict[str, Any]] = None
    analysis_preferences: Optional[Dict[str, Any]] = None
    notification_preferences: Optional[Dict[str, Any]] = None
    privacy_settings: Optional[Dict[str, Any]] = None


# ===== RESUME DTOs =====

class ResumeCreateRequest(BaseModel):
    """DTO para criação de currículo"""
    title: str = Field(..., min_length=1, max_length=255)
    version: str = Field(default="v1.0", max_length=20)


class ResumeUpdateRequest(BaseModel):
    """DTO para atualização de currículo"""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    version: Optional[str] = Field(None, max_length=20)
    status: Optional[ResumeStatus] = None


class ResumeUploadRequest(BaseModel):
    """DTO para upload de currículo"""
    title: str = Field(..., min_length=1, max_length=255)
    # O arquivo será enviado via multipart/form-data


# ===== JOB DTOs =====

class JobDescriptionCreateRequest(BaseModel):
    """DTO para criação de descrição de vaga"""
    company_id: Optional[UUID] = None
    title: str = Field(..., min_length=1, max_length=255)
    location: Optional[str] = Field(None, max_length=255)
    job_type: Optional[JobType] = None
    salary_range: Optional[str] = Field(None, max_length=100)
    experience_level: Optional[ExperienceLevel] = None
    description: Optional[str] = None
    requirements: Optional[str] = None
    benefits: Optional[str] = None
    expires_at: Optional[datetime] = None


class JobDescriptionUpdateRequest(BaseModel):
    """DTO para atualização de descrição de vaga"""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    location: Optional[str] = Field(None, max_length=255)
    job_type: Optional[JobType] = None
    salary_range: Optional[str] = Field(None, max_length=100)
    experience_level: Optional[ExperienceLevel] = None
    description: Optional[str] = None
    requirements: Optional[str] = None
    benefits: Optional[str] = None
    expires_at: Optional[datetime] = None
    is_active: Optional[bool] = None


# ===== ANALYSIS DTOs =====

class AnalysisCreateRequest(BaseModel):
    """DTO para criação de análise"""
    resume_id: UUID
    job_id: Optional[UUID] = None
    job_description: Optional[str] = None  # Para análise ad-hoc
    analysis_type: str = Field(default="job_match", max_length=50)
    
    @validator('job_id', 'job_description')
    def validate_job_input(cls, v, values):
        job_id = values.get('job_id')
        job_description = values.get('job_description')
        if not job_id and not job_description:
            raise ValueError('Either job_id or job_description must be provided')
        return v


class BulkAnalysisRequest(BaseModel):
    """DTO para análise em lote"""
    resume_ids: List[UUID] = Field(..., min_items=1, max_items=10)
    job_id: UUID


# ===== COVER LETTER DTOs =====

class CoverLetterCreateRequest(BaseModel):
    """DTO para criação de carta de apresentação"""
    resume_id: UUID
    job_id: Optional[UUID] = None
    title: str = Field(..., min_length=1, max_length=255)
    tone: str = Field(default="formal", pattern="^(formal|casual|enthusiastic)$")
    length: str = Field(default="medium", pattern="^(short|medium|long)$")
    focus_areas: List[str] = Field(default_factory=list, max_items=5)
    custom_instructions: Optional[str] = Field(None, max_length=1000)


class CoverLetterUpdateRequest(BaseModel):
    """DTO para atualização de carta de apresentação"""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    content: Optional[Dict[str, Any]] = None
    customizations: Optional[Dict[str, Any]] = None


# ===== COMPANY DTOs =====

class CompanyCreateRequest(BaseModel):
    """DTO para criação de empresa"""
    name: str = Field(..., min_length=1, max_length=255)
    industry: Optional[str] = Field(None, max_length=100)
    size: Optional[str] = Field(None, max_length=50)
    location: Optional[str] = Field(None, max_length=255)
    website: Optional[str] = Field(None, max_length=500)
    logo_url: Optional[str] = Field(None, max_length=500)


class CompanyUpdateRequest(BaseModel):
    """DTO para atualização de empresa"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    industry: Optional[str] = Field(None, max_length=100)
    size: Optional[str] = Field(None, max_length=50)
    location: Optional[str] = Field(None, max_length=255)
    website: Optional[str] = Field(None, max_length=500)
    logo_url: Optional[str] = Field(None, max_length=500)
    is_active: Optional[bool] = None


# ===== SKILL DTOs =====

class SkillCreateRequest(BaseModel):
    """DTO para criação de habilidade"""
    name: str = Field(..., min_length=1, max_length=100)
    category: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = Field(None, max_length=500)


class UserSkillUpdateRequest(BaseModel):
    """DTO para atualização de habilidade do usuário"""
    skill_id: UUID
    proficiency_level: int = Field(..., ge=1, le=100)
    years_of_experience: Optional[float] = Field(None, ge=0, le=50)


class BulkUserSkillsUpdateRequest(BaseModel):
    """DTO para atualização em lote de habilidades"""
    skills: List[UserSkillUpdateRequest] = Field(..., min_items=1, max_items=50)


# ===== NOTIFICATION DTOs =====

class NotificationCreateRequest(BaseModel):
    """DTO para criação de notificação"""
    user_id: UUID
    type: NotificationType
    title: str = Field(..., min_length=1, max_length=255)
    message: str = Field(..., min_length=1, max_length=1000)
    action_url: Optional[str] = Field(None, max_length=500)
    expires_at: Optional[datetime] = None


class NotificationUpdateRequest(BaseModel):
    """DTO para atualização de notificação"""
    is_read: Optional[bool] = None


class BulkNotificationUpdateRequest(BaseModel):
    """DTO para atualização em lote de notificações"""
    notification_ids: List[UUID] = Field(..., min_items=1, max_items=100)
    is_read: bool = True


# ===== SEARCH & FILTER DTOs =====

class ResumeSearchRequest(BaseModel):
    """DTO para busca de currículos"""
    search: Optional[str] = Field(None, max_length=255)
    status: Optional[ResumeStatus] = None
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
    sort_by: str = Field(default="created_at", pattern="^(created_at|updated_at|title|match_score)$")
    sort_order: str = Field(default="desc", pattern="^(asc|desc)$")
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


class AnalysisSearchRequest(BaseModel):
    """DTO para busca de análises"""
    search: Optional[str] = Field(None, max_length=255)
    resume_id: Optional[UUID] = None
    job_id: Optional[UUID] = None
    min_score: Optional[float] = Field(None, ge=0, le=100)
    max_score: Optional[float] = Field(None, ge=0, le=100)
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
    sort_by: str = Field(default="created_at", pattern="^(created_at|match_score|processing_time)$")
    sort_order: str = Field(default="desc", pattern="^(asc|desc)$")
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


class JobSearchRequest(BaseModel):
    """DTO para busca de vagas"""
    search: Optional[str] = Field(None, max_length=255)
    location: Optional[str] = Field(None, max_length=255)
    job_type: Optional[JobType] = None
    experience_level: Optional[ExperienceLevel] = None
    company_id: Optional[UUID] = None
    posted_after: Optional[datetime] = None
    is_active: bool = True
    sort_by: str = Field(default="posted_at", pattern="^(posted_at|title|view_count)$")
    sort_order: str = Field(default="desc", pattern="^(asc|desc)$")
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


# ===== DASHBOARD DTOs =====

class DashboardStatsRequest(BaseModel):
    """DTO para estatísticas do dashboard"""
    period: str = Field(default="30d", pattern="^(7d|30d|90d|1y|all)$")
    include_details: bool = False


# ===== EXPORT DTOs =====

class DataExportRequest(BaseModel):
    """DTO para exportação de dados"""
    export_type: str = Field(..., pattern="^(resumes|analyses|cover_letters|all)$")
    format: str = Field(default="json", pattern="^(json|csv|pdf)$")
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    include_files: bool = False


# ===== FEEDBACK DTOs =====

class FeedbackCreateRequest(BaseModel):
    """DTO para criação de feedback"""
    type: str = Field(..., pattern="^(analysis_feedback|feature_request|bug_report|general)$")
    title: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=10, max_length=2000)
    rating: Optional[int] = Field(None, ge=1, le=5)
    category: Optional[str] = Field(None, max_length=100)
    context: Optional[Dict[str, Any]] = None
