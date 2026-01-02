"""
Mapper para currículos
Seguindo padrão IT Valley
"""
from typing import Optional
from datetime import datetime

from domain.entities.domain import Resume
from schemas.responses.resume_responses import ResumeResponse, ResumeListResponse


class ResumeMapper:
    """Mapper para conversão de currículos"""
    
    @staticmethod
    def to_public(resume: Resume) -> ResumeResponse:
        """
        Converte entidade Resume para resposta pública
        
        Args:
            resume: Entidade Resume
            
        Returns:
            Resposta pública do currículo
        """
        return ResumeResponse(
            resume_id=resume.resume_id,
            user_id=resume.user_id,
            title=resume.title,
            version=resume.version,
            status=resume.status,
            original_filename=resume.original_filename,
            file_size=resume.file_size,
            file_type=resume.file_type,
            created_at=resume.created_at,
            updated_at=resume.updated_at,
            last_analyzed_at=resume.last_analyzed_at,
            analysis_count=resume.analysis_count,
            average_match_score=resume.average_match_score,
            download_url=None  # Será gerado pelo service
        )
    
    @staticmethod
    def to_display(resume: Resume) -> dict:
        """
        Converte entidade Resume para exibição simples
        
        Args:
            resume: Entidade Resume
            
        Returns:
            Dados para exibição
        """
        return {
            "id": str(resume.resume_id),
            "title": resume.title,
            "version": resume.version,
            "status": resume.status.value,
            "analysis_count": resume.analysis_count,
            "average_score": resume.average_match_score,
            "created_at": resume.created_at,
            "last_analyzed": resume.last_analyzed_at
        }
    
    @staticmethod
    def to_list_item(resume: Resume) -> dict:
        """
        Converte entidade Resume para item de lista
        
        Args:
            resume: Entidade Resume
            
        Returns:
            Item de lista
        """
        return {
            "resume_id": str(resume.resume_id),
            "title": resume.title,
            "version": resume.version,
            "status": resume.status.value,
            "file_type": resume.file_type,
            "file_size": resume.file_size,
            "analysis_count": resume.analysis_count,
            "average_match_score": resume.average_match_score,
            "created_at": resume.created_at,
            "updated_at": resume.updated_at,
            "last_analyzed_at": resume.last_analyzed_at
        }
    
    @staticmethod
    def to_upload_response(resume: Resume, upload_url: str = None) -> dict:
        """
        Converte entidade Resume para resposta de upload
        
        Args:
            resume: Entidade Resume
            upload_url: URL de upload (opcional)
            
        Returns:
            Resposta de upload
        """
        return {
            "resume_id": str(resume.resume_id),
            "title": resume.title,
            "status": resume.status.value,
            "upload_url": upload_url,
            "processing_status": "uploaded" if resume.original_filename else "pending"
        }
    
    @staticmethod
    def to_analysis_input(resume: Resume) -> dict:
        """
        Converte entidade Resume para entrada de análise
        
        Args:
            resume: Entidade Resume
            
        Returns:
            Dados para análise
        """
        return {
            "resume_id": str(resume.resume_id),
            "title": resume.title,
            "version": resume.version,
            "file_type": resume.file_type,
            "analysis_count": resume.analysis_count,
            "average_score": resume.average_match_score
        }
    
    @staticmethod
    def to_statistics(resume: Resume, stats: dict) -> dict:
        """
        Converte entidade Resume com estatísticas
        
        Args:
            resume: Entidade Resume
            stats: Estatísticas do currículo
            
        Returns:
            Dados com estatísticas
        """
        return {
            "resume": ResumeMapper.to_public(resume),
            "statistics": {
                "total_analyses": stats.get("total_analyses", 0),
                "best_match_score": stats.get("best_match_score", 0.0),
                "worst_match_score": stats.get("worst_match_score", 0.0),
                "last_analysis_date": stats.get("last_analysis_date"),
                "improvement_suggestions": stats.get("improvement_suggestions", [])
            }
        }
    
    @staticmethod
    def to_export(resume: Resume) -> dict:
        """
        Converte entidade Resume para exportação
        
        Args:
            resume: Entidade Resume
            
        Returns:
            Dados para exportação
        """
        return {
            "id": str(resume.resume_id),
            "title": resume.title,
            "version": resume.version,
            "status": resume.status.value,
            "file_type": resume.file_type,
            "file_size": resume.file_size,
            "analysis_count": resume.analysis_count,
            "average_match_score": resume.average_match_score,
            "created_at": resume.created_at.isoformat() if resume.created_at else None,
            "updated_at": resume.updated_at.isoformat() if resume.updated_at else None,
            "last_analyzed_at": resume.last_analyzed_at.isoformat() if resume.last_analyzed_at else None
        }
    
    @staticmethod
    def to_minimal(resume: Resume) -> dict:
        """
        Converte entidade Resume para dados mínimos
        
        Args:
            resume: Entidade Resume
            
        Returns:
            Dados mínimos
        """
        return {
            "resume_id": str(resume.resume_id),
            "title": resume.title,
            "status": resume.status.value
        }
    
    @staticmethod
    def to_search_result(resume: Resume, score: float = None) -> dict:
        """
        Converte entidade Resume para resultado de busca
        
        Args:
            resume: Entidade Resume
            score: Score de relevância (opcional)
            
        Returns:
            Resultado de busca
        """
        return {
            "id": str(resume.resume_id),
            "type": "resume",
            "title": resume.title,
            "description": f"Currículo {resume.version}",
            "score": score or resume.average_match_score,
            "created_at": resume.created_at,
            "highlight": None  # Será preenchido pelo service de busca
        }
