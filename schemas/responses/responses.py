"""
DTOs para respostas da API
Data Transfer Objects para saída de dados
"""
from datetime import datetime
from typing import Optional, List, Dict, Any, Generic, TypeVar
from uuid import UUID
from pydantic import BaseModel, Field, EmailStr
from domain.entities.domain import (
    SubscriptionType, ResumeStatus, AnalysisStatus,
    JobType, ExperienceLevel, NotificationType
)

T = TypeVar('T')


# ===== BASE RESPONSE DTOs =====

class BaseResponse(BaseModel):
    """Resposta base da API"""
    success: bool = True
    message: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ErrorResponse(BaseResponse):
    """Resposta de erro"""
    success: bool = False
    message: str
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat()) 
    error_code: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


class PaginatedResponse(BaseResponse, Generic[T]):
    """Resposta paginada"""
    data: List[T]
    pagination: Dict[str, Any]
    
    @classmethod
    def create(cls, data: List[T], page: int, page_size: int, total: int):
        total_pages = (total + page_size - 1) // page_size
        return cls(
            data=data,
            pagination={
                "page": page,
                "page_size": page_size,
                "total": total,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_prev": page > 1
            }
        )


# ===== AUTH DTOs =====

class TokenResponse(BaseResponse):
    """
    Resposta de token de autenticação (USR-005).
    (Mantido da versão antiga, compatível com BaseResponse)
    """
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # segundos


# --- INÍCIO DA EDIÇÃO CIRÚRGICA ---
# A classe UserProfileResponse foi modificada para alinhar com a
# nova UserEntity (Passo 2) e UserService (Passo 5.1).
# Os campos que não existem na nova entidade (phone, subscription_type)
# foram removidos para evitar erros de mapeamento no USR-001.

class UserProfileResponse(BaseModel):
    """
    Resposta do perfil do usuário (USR-001).
    Refatorado para alinhar com a nova UserEntity.
    """
    user_id: str | UUID # O serviço (Passo 5.1) envia o 'id' (str) da entidade
    email: EmailStr
    full_name: Optional[str] = None # O serviço (Passo 5.1) mapeia 'name' para 'full_name'
    avatar_url: Optional[str] = None
    created_at: datetime
    last_login_at: Optional[datetime] = None
    email_verified: bool = False # O serviço (Passo 5.1) não lida com isso ainda
    two_factor_enabled: bool = False # O serviço (Passo 5.1) não lida com isso ainda

    class Config:
        from_attributes = True # Permite mapear de entidades (orm_mode)

# --- FIM DA EDIÇÃO CIRÚRGICA ---


# ===== RESUME DTOs =====
# (Estes DTOs abaixo são mantidos intactos para os outros devs)

class ResumeResponse(BaseModel):
    """Resposta de currículo"""
    resume_id: UUID
    user_id: UUID
    title: str
    version: str
    status: ResumeStatus
    original_filename: Optional[str] = None
    file_size: Optional[int] = None
    file_type: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    last_analyzed_at: Optional[datetime] = None
    analysis_count: int
    average_match_score: float
    download_url: Optional[str] = None


class ResumeListResponse(BaseModel):
    """Resposta de lista de currículos"""
    resumes: List[ResumeResponse]
    total_count: int
    active_count: int
    draft_count: int
    archived_count: int


class ResumeUploadResponse(BaseResponse):
    """Resposta de upload de currículo"""
    resume_id: UUID
    upload_url: Optional[str] = None  # Para upload direto ao blob storage
    processing_status: str = "uploaded"


# ===== JOB DTOs =====

class CompanyResponse(BaseModel):
    """Resposta de empresa"""
    company_id: UUID
    name: str
    industry: Optional[str] = None
    size: Optional[str] = None
    location: Optional[str] = None
    website: Optional[str] = None
    logo_url: Optional[str] = None
    created_at: datetime
    is_active: bool


class JobDescriptionResponse(BaseModel):
    """Resposta de descrição de vaga"""
    job_id: UUID
    company: Optional[CompanyResponse] = None
    title: str
    location: Optional[str] = None
    job_type: Optional[JobType] = None
    salary_range: Optional[str] = None
    experience_level: Optional[ExperienceLevel] = None
    description: Optional[str] = None
    requirements: Optional[str] = None
    benefits: Optional[str] = None
    posted_at: datetime
    expires_at: Optional[datetime] = None
    is_active: bool
    view_count: int
    application_count: int


# ===== ANALYSIS DTOs =====

class SkillMatchResponse(BaseModel):
    """Resposta de match de habilidade"""
    name: str
    confidence: float
    matched: bool
    category: str
    proficiency_level: Optional[int] = None


class ExperienceMatchResponse(BaseModel):
    """Resposta de match de experiência"""
    company: str
    position: str
    duration: str
    description: str
    relevance_score: float


class CompatibilityScoresResponse(BaseModel):
    """Resposta de scores de compatibilidade"""
    overall_score: float
    skills: float
    experience: float
    education: float
    cultural: float


class AnalysisResponse(BaseModel):
    """Resposta de análise"""
    analysis_id: UUID
    user_id: UUID
    resume_id: UUID
    job_id: Optional[UUID] = None
    match_score: float
    status: AnalysisStatus
    analysis_type: str
    processing_time_ms: Optional[int] = None
    created_at: datetime
    completed_at: Optional[datetime] = None


class DetailedAnalysisResponse(BaseModel):
    """Resposta de análise detalhada"""
    analysis_id: UUID
    match_score: float
    status: AnalysisStatus
    
    # Análise da vaga
    job_analysis: Dict[str, Any]
    
    # Análise do currículo
    extracted_skills: List[SkillMatchResponse]
    experience_matches: List[ExperienceMatchResponse]
    education: List[Dict[str, str]]
    languages: List[str]
    certifications: List[str]
    
    # Relatório de compatibilidade
    compatibility_scores: CompatibilityScoresResponse
    strengths: List[str]
    weaknesses: List[str]
    recommendations: List[str]
    improvement_areas: List[Dict[str, Any]]
    
    # Metadata
    processing_time_ms: int
    ai_model: str
    created_at: datetime


class AnalysisListResponse(BaseModel):
    """Resposta de lista de análises"""
    analyses: List[AnalysisResponse]
    total_count: int
    completed_count: int
    pending_count: int
    failed_count: int
    average_score: float


# ===== COVER LETTER DTOs =====

class CoverLetterResponse(BaseModel):
    """Resposta de carta de apresentação"""
    cover_letter_id: UUID
    user_id: UUID
    resume_id: UUID
    job_id: Optional[UUID] = None
    title: str
    status: str
    generated_at: datetime
    last_edited_at: Optional[datetime] = None
    download_count: int
    word_count: Optional[int] = None
    download_url: Optional[str] = None


class CoverLetterContentResponse(BaseModel):
    """Resposta do conteúdo da carta"""
    cover_letter_id: UUID
    content: Dict[str, Any]
    customizations: Dict[str, Any]
    edit_history: List[Dict[str, Any]]
    generated_by: str
    ai_model: str
    language: str
    word_count: int


class CoverLetterListResponse(BaseModel):
    """Resposta de lista de cartas"""
    cover_letters: List[CoverLetterResponse]
    total_count: int
    generated_count: int
    edited_count: int


# ===== SKILL DTOs =====

class SkillResponse(BaseModel):
    """Resposta de habilidade"""
    skill_id: UUID
    name: str
    category: Optional[str] = None
    description: Optional[str] = None
    is_active: bool
    created_at: datetime


class UserSkillResponse(BaseModel):
    """Resposta de habilidade do usuário"""
    user_skill_id: UUID
    skill: SkillResponse
    proficiency_level: int
    years_of_experience: Optional[float] = None
    last_updated: datetime
    source: str


class SkillsAnalysisResponse(BaseModel):
    """Resposta de análise de habilidades"""
    user_id: UUID
    total_skills: int
    skills_by_category: Dict[str, List[UserSkillResponse]]
    top_skills: List[UserSkillResponse]
    improvement_areas: List[str]
    skill_gaps: List[str]
    overall_score: float


# ===== NOTIFICATION DTOs =====

class NotificationResponse(BaseModel):
    """Resposta de notificação"""
    notification_id: UUID
    type: NotificationType
    title: str
    message: str
    action_url: Optional[str] = None
    is_read: bool
    created_at: datetime
    read_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None


class NotificationListResponse(BaseModel):
    """Resposta de lista de notificações"""
    notifications: List[NotificationResponse]
    total_count: int
    unread_count: int


# ===== DASHBOARD DTOs =====

class DashboardStatsResponse(BaseModel):
    """Resposta de estatísticas do dashboard"""
    saved_resumes: int
    average_match: float
    best_match: Optional[str] = None
    best_match_percentage: float
    total_analyses: int
    this_month: int
    completed_analyses: int
    pending_analyses: int
    cover_letters_generated: int
    profile_views: int
    
    # Gráficos e tendências
    analysis_trend: List[Dict[str, Any]] = Field(default_factory=list)
    skill_distribution: List[Dict[str, Any]] = Field(default_factory=list)
    match_score_distribution: List[Dict[str, Any]] = Field(default_factory=list)


class RecentActivityResponse(BaseModel):
    """Resposta de atividade recente"""
    activity_type: str
    title: str
    description: str
    timestamp: datetime
    resource_id: Optional[UUID] = None
    resource_type: Optional[str] = None


class DashboardResponse(BaseModel):
    """Resposta completa do dashboard"""
    stats: DashboardStatsResponse
    recent_activities: List[RecentActivityResponse]
    recent_analyses: List[AnalysisResponse]
    notifications: List[NotificationResponse]


# ===== SEARCH DTOs =====

class SearchResultResponse(BaseModel):
    """Resposta de resultado de busca"""
    id: UUID
    type: str  # resume, job, analysis, etc.
    title: str
    description: Optional[str] = None
    score: float
    highlight: Optional[str] = None
    created_at: datetime


class SearchResponse(BaseModel):
    """Resposta de busca"""
    query: str
    results: List[SearchResultResponse]
    total_count: int
    search_time_ms: int
    suggestions: List[str] = Field(default_factory=list)


# ===== FILE DTOs =====

class FileUploadResponse(BaseResponse):
    """Resposta de upload de arquivo"""
    file_id: UUID
    filename: str
    file_size: int
    file_type: str
    upload_url: Optional[str] = None
    processing_status: str = "uploaded"


class FileDownloadResponse(BaseModel):
    """Resposta de download de arquivo"""
    file_id: UUID
    filename: str
    download_url: str
    expires_at: datetime
    file_size: int
    mime_type: str


# ===== EXPORT DTOs =====

class ExportResponse(BaseResponse):
    """Resposta de exportação"""
    export_id: UUID
    export_type: str
    format: str
    status: str = "processing"
    download_url: Optional[str] = None
    expires_at: Optional[datetime] = None
    file_size: Optional[int] = None


# ===== HEALTH & STATUS DTOs =====

class HealthCheckResponse(BaseModel):
    """Resposta de health check"""
    status: str = "healthy"
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    version: str
    uptime_seconds: int
    
    # Status dos serviços
    database: Dict[str, str]
    mongodb: Dict[str, str]
    blob_storage: Dict[str, str]
    redis: Dict[str, str]
    ai_services: Dict[str, str]


class SystemStatsResponse(BaseModel):
    """Resposta de estatísticas do sistema"""
    total_users: int
    total_resumes: int
    total_analyses: int
    total_cover_letters: int
    
    # Estatísticas de uso
    daily_active_users: int
    monthly_active_users: int
    analyses_today: int
    analyses_this_month: int
    
    # Performance
    average_analysis_time_ms: float
    average_response_time_ms: float
    error_rate_percentage: float
    
    # Storage
    total_storage_gb: float
    storage_usage_percentage: float


# ===== PREFERENCES DTOs =====

class UserPreferencesResponse(BaseModel):
    """Resposta de preferências do usuário"""
    user_id: UUID
    resume_preferences: Dict[str, Any]
    analysis_preferences: Dict[str, Any]
    notification_preferences: Dict[str, Any]
    privacy_settings: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
