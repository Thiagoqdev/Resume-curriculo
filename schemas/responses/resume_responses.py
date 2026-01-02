"""
Respostas específicas para currículos
Seguindo padrão IT Valley
"""
from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel

from domain.entities.domain import ResumeStatus


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
    resumes: list
    total_count: int
    active_count: int
    draft_count: int
    archived_count: int
