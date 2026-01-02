"""
Respostas específicas para análises
Seguindo padrão IT Valley
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID
from pydantic import BaseModel

from domain.entities.domain import AnalysisStatus


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
    extracted_skills: List[Dict[str, Any]]
    experience_matches: List[Dict[str, Any]]
    education: List[Dict[str, str]]
    languages: List[str]
    certifications: List[str]
    
    # Relatório de compatibilidade
    compatibility_scores: Dict[str, float]
    strengths: List[str]
    weaknesses: List[str]
    recommendations: List[str]
    improvement_areas: List[Dict[str, Any]]
    
    # Metadata
    processing_time_ms: int
    ai_model: str
    created_at: datetime
