"""
Modelos de domínio do SkillSync
Representam as entidades principais do negócio
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID
from enum import Enum
from dataclasses import dataclass, field


class SubscriptionType(str, Enum):
    """Tipos de assinatura"""
    FREE = "free"
    PRO = "pro"


class ResumeStatus(str, Enum):
    """Status do currículo"""
    DRAFT = "draft"
    ACTIVE = "active"
    ARCHIVED = "archived"


class AnalysisStatus(str, Enum):
    """Status da análise"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class JobType(str, Enum):
    """Tipos de trabalho"""
    CLT = "clt"
    PJ = "pj"
    REMOTE = "remote"
    HYBRID = "hybrid"
    FREELANCE = "freelance"


class ExperienceLevel(str, Enum):
    """Níveis de experiência"""
    JUNIOR = "junior"
    PLENO = "pleno"
    SENIOR = "senior"
    LEAD = "lead"
    MANAGER = "manager"


class NotificationType(str, Enum):
    """Tipos de notificação"""
    SUCCESS = "success"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


@dataclass
class User:
    """Entidade Usuário"""
    user_id: UUID
    email: str
    full_name: str
    password_hash: str
    phone: Optional[str] = None
    avatar_url: Optional[str] = None
    subscription_type: SubscriptionType = SubscriptionType.FREE
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    last_login_at: Optional[datetime] = None
    is_active: bool = True
    email_verified: bool = False
    two_factor_enabled: bool = False


@dataclass
class Resume:
    """Entidade Currículo"""
    resume_id: UUID
    user_id: UUID
    title: str
    version: str = "v1.0"
    status: ResumeStatus = ResumeStatus.DRAFT
    data_lake_file_id: Optional[UUID] = None
    original_filename: Optional[str] = None
    file_size: Optional[int] = None
    file_type: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    last_analyzed_at: Optional[datetime] = None
    analysis_count: int = 0
    average_match_score: float = 0.0


@dataclass
class Company:
    """Entidade Empresa"""
    company_id: UUID
    name: str
    industry: Optional[str] = None
    size: Optional[str] = None
    location: Optional[str] = None
    website: Optional[str] = None
    logo_url: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    is_active: bool = True


@dataclass
class JobDescription:
    """Entidade Descrição de Vaga"""
    job_id: UUID
    company_id: Optional[UUID]
    title: str
    location: Optional[str] = None
    job_type: Optional[JobType] = None
    salary_range: Optional[str] = None
    experience_level: Optional[ExperienceLevel] = None
    description: Optional[str] = None
    requirements: Optional[str] = None
    benefits: Optional[str] = None
    posted_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    is_active: bool = True
    view_count: int = 0
    application_count: int = 0


@dataclass
class CompatibilityAnalysis:
    """Entidade Análise de Compatibilidade"""
    analysis_id: UUID
    user_id: UUID
    resume_id: UUID
    job_id: Optional[UUID]
    match_score: float
    status: AnalysisStatus = AnalysisStatus.PENDING
    analysis_type: str = "job_match"
    processing_time_ms: Optional[int] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    mongo_analysis_id: Optional[str] = None


@dataclass
class CoverLetter:
    """Entidade Carta de Apresentação"""
    cover_letter_id: UUID
    user_id: UUID
    resume_id: UUID
    job_id: Optional[UUID]
    title: str
    status: str = "generated"
    data_lake_file_id: Optional[UUID] = None
    generated_at: datetime = field(default_factory=datetime.utcnow)
    last_edited_at: Optional[datetime] = None
    download_count: int = 0
    mongo_content_id: Optional[str] = None


@dataclass
class Skill:
    """Entidade Habilidade"""
    skill_id: UUID
    name: str
    category: Optional[str] = None
    description: Optional[str] = None
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class UserSkill:
    """Entidade Habilidade do Usuário"""
    user_skill_id: UUID
    user_id: UUID
    skill_id: UUID
    proficiency_level: int  # 1-100
    years_of_experience: Optional[float] = None
    last_updated: datetime = field(default_factory=datetime.utcnow)
    source: str = "manual"  # manual, resume_analysis, linkedin_import


@dataclass
class Notification:
    """Entidade Notificação"""
    notification_id: UUID
    user_id: UUID
    type: NotificationType
    title: str
    message: str
    action_url: Optional[str] = None
    is_read: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)
    read_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None


@dataclass
class UserSession:
    """Entidade Sessão do Usuário"""
    session_id: UUID
    user_id: UUID
    session_token: str
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: datetime = field(default_factory=datetime.utcnow)
    last_activity_at: datetime = field(default_factory=datetime.utcnow)
    is_active: bool = True


@dataclass
class DataLakeFile:
    """Entidade Arquivo do Data Lake"""
    file_id: UUID
    user_id: UUID
    filename: str
    file_type: str
    file_size: int
    mime_type: Optional[str] = None
    storage_path: str = ""
    bucket_name: str = ""
    storage_provider: str = "azure_blob"
    uploaded_at: datetime = field(default_factory=datetime.utcnow)
    last_accessed_at: Optional[datetime] = None
    access_count: int = 0
    is_deleted: bool = False
    deleted_at: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None


# ===== MODELOS MONGODB (Documentos) =====

@dataclass
class SkillExtraction:
    """Habilidade extraída do currículo"""
    name: str
    confidence: float
    matched: bool
    category: str


@dataclass
class ExperienceItem:
    """Item de experiência profissional"""
    company: str
    position: str
    duration: str
    description: str
    relevance_score: float


@dataclass
class EducationItem:
    """Item de educação"""
    institution: str
    degree: str
    field: str
    year: str


@dataclass
class JobAnalysis:
    """Análise da vaga"""
    key_requirements: List[str]
    required_skills: List[str]
    experience_level: str
    education: str
    benefits: List[str]
    company_info: Dict[str, str]


@dataclass
class ResumeAnalysis:
    """Análise do currículo"""
    extracted_skills: List[SkillExtraction]
    experience: List[ExperienceItem]
    education: List[EducationItem]
    languages: List[str]
    certifications: List[str]


@dataclass
class CategoryScores:
    """Scores por categoria"""
    skills: float
    experience: float
    education: float
    cultural: float


@dataclass
class ImprovementArea:
    """Área de melhoria"""
    area: str
    priority: str
    suggestions: List[str]


@dataclass
class CompatibilityReport:
    """Relatório de compatibilidade"""
    overall_score: float
    category_scores: CategoryScores
    strengths: List[str]
    weaknesses: List[str]
    recommendations: List[str]
    improvement_areas: List[ImprovementArea]


@dataclass
class DetailedAnalysis:
    """Análise detalhada (MongoDB)"""
    analysis_id: str
    user_id: str
    resume_id: str
    job_id: Optional[str]
    match_score: float
    job_analysis: JobAnalysis
    resume_analysis: ResumeAnalysis
    compatibility_report: CompatibilityReport
    processing_time: int
    ai_model: str
    version: str
    created_at: datetime
    updated_at: datetime


@dataclass
class CoverLetterContent:
    """Conteúdo da carta de apresentação"""
    subject: str
    greeting: str
    introduction: str
    body: List[str]
    conclusion: str
    signature: str
    full_text: str


@dataclass
class CoverLetterCustomization:
    """Personalização da carta"""
    tone: str  # formal, casual, enthusiastic
    length: str  # short, medium, long
    focus_areas: List[str]
    company_research: Dict[str, Any]


@dataclass
class EditHistoryItem:
    """Item do histórico de edições"""
    version: int
    changes: str
    edited_by: str
    edited_at: datetime


@dataclass
class CoverLetterDocument:
    """Documento da carta (MongoDB)"""
    cover_letter_id: str
    user_id: str
    resume_id: str
    job_id: Optional[str]
    content: CoverLetterContent
    customizations: CoverLetterCustomization
    edit_history: List[EditHistoryItem]
    generated_by: str  # ai, manual
    ai_model: str
    language: str
    word_count: int
    created_at: datetime
    updated_at: datetime


@dataclass
class UserPreferences:
    """Preferências do usuário (MongoDB)"""
    user_id: str
    resume_preferences: Dict[str, Any]
    analysis_preferences: Dict[str, Any]
    notification_preferences: Dict[str, Any]
    privacy_settings: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
