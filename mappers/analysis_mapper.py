"""
Mapper para análises
Seguindo padrão IT Valley
"""
from typing import Optional, List, Dict, Any
from datetime import datetime

from domain.entities.domain import CompatibilityAnalysis
from schemas.responses.analysis_responses import AnalysisResponse, DetailedAnalysisResponse


class AnalysisMapper:
    """Mapper para conversão de análises"""
    
    @staticmethod
    def to_public(analysis: CompatibilityAnalysis) -> AnalysisResponse:
        """
        Converte entidade CompatibilityAnalysis para resposta pública
        
        Args:
            analysis: Entidade CompatibilityAnalysis
            
        Returns:
            Resposta pública da análise
        """
        return AnalysisResponse(
            analysis_id=analysis.analysis_id,
            user_id=analysis.user_id,
            resume_id=analysis.resume_id,
            job_id=analysis.job_id,
            match_score=analysis.match_score,
            status=analysis.status,
            analysis_type=analysis.analysis_type,
            processing_time_ms=analysis.processing_time_ms,
            created_at=analysis.created_at,
            completed_at=analysis.completed_at
        )
    
    @staticmethod
    def to_detailed(analysis: CompatibilityAnalysis, detailed_data: dict) -> DetailedAnalysisResponse:
        """
        Converte entidade CompatibilityAnalysis para resposta detalhada
        
        Args:
            analysis: Entidade CompatibilityAnalysis
            detailed_data: Dados detalhados da análise
            
        Returns:
            Resposta detalhada da análise
        """
        return DetailedAnalysisResponse(
            analysis_id=analysis.analysis_id,
            match_score=analysis.match_score,
            status=analysis.status,
            job_analysis=detailed_data.get("job_analysis", {}),
            extracted_skills=detailed_data.get("extracted_skills", []),
            experience_matches=detailed_data.get("experience_matches", []),
            education=detailed_data.get("education", []),
            languages=detailed_data.get("languages", []),
            certifications=detailed_data.get("certifications", []),
            compatibility_scores=detailed_data.get("compatibility_scores", {}),
            strengths=detailed_data.get("strengths", []),
            weaknesses=detailed_data.get("weaknesses", []),
            recommendations=detailed_data.get("recommendations", []),
            improvement_areas=detailed_data.get("improvement_areas", []),
            processing_time_ms=analysis.processing_time_ms or 0,
            ai_model=detailed_data.get("ai_model", "gpt-4"),
            created_at=analysis.created_at
        )
    
    @staticmethod
    def to_display(analysis: CompatibilityAnalysis) -> dict:
        """
        Converte entidade CompatibilityAnalysis para exibição simples
        
        Args:
            analysis: Entidade CompatibilityAnalysis
            
        Returns:
            Dados para exibição
        """
        return {
            "id": str(analysis.analysis_id),
            "match_score": analysis.match_score,
            "status": analysis.status.value,
            "analysis_type": analysis.analysis_type,
            "created_at": analysis.created_at,
            "completed_at": analysis.completed_at
        }
    
    @staticmethod
    def to_list_item(analysis: CompatibilityAnalysis) -> dict:
        """
        Converte entidade CompatibilityAnalysis para item de lista
        
        Args:
            analysis: Entidade CompatibilityAnalysis
            
        Returns:
            Item de lista
        """
        return {
            "analysis_id": str(analysis.analysis_id),
            "user_id": str(analysis.user_id),
            "resume_id": str(analysis.resume_id),
            "job_id": str(analysis.job_id) if analysis.job_id else None,
            "match_score": analysis.match_score,
            "status": analysis.status.value,
            "analysis_type": analysis.analysis_type,
            "processing_time_ms": analysis.processing_time_ms,
            "created_at": analysis.created_at,
            "completed_at": analysis.completed_at
        }
    
    @staticmethod
    def to_dashboard_item(analysis: CompatibilityAnalysis, job_title: str = None) -> dict:
        """
        Converte entidade CompatibilityAnalysis para item do dashboard
        
        Args:
            analysis: Entidade CompatibilityAnalysis
            job_title: Título da vaga (opcional)
            
        Returns:
            Item do dashboard
        """
        return {
            "analysis_id": str(analysis.analysis_id),
            "match_score": analysis.match_score,
            "status": analysis.status.value,
            "job_title": job_title or "Análise Ad-hoc",
            "created_at": analysis.created_at,
            "completed_at": analysis.completed_at,
            "processing_time": analysis.processing_time_ms
        }
    
    @staticmethod
    def to_statistics(analysis: CompatibilityAnalysis, stats: dict) -> dict:
        """
        Converte entidade CompatibilityAnalysis com estatísticas
        
        Args:
            analysis: Entidade CompatibilityAnalysis
            stats: Estatísticas da análise
            
        Returns:
            Dados com estatísticas
        """
        return {
            "analysis": AnalysisMapper.to_public(analysis),
            "statistics": {
                "category_scores": stats.get("category_scores", {}),
                "skill_matches": stats.get("skill_matches", 0),
                "experience_matches": stats.get("experience_matches", 0),
                "education_matches": stats.get("education_matches", 0),
                "overall_rating": stats.get("overall_rating", "good")
            }
        }
    
    @staticmethod
    def to_export(analysis: CompatibilityAnalysis) -> dict:
        """
        Converte entidade CompatibilityAnalysis para exportação
        
        Args:
            analysis: Entidade CompatibilityAnalysis
            
        Returns:
            Dados para exportação
        """
        return {
            "id": str(analysis.analysis_id),
            "user_id": str(analysis.user_id),
            "resume_id": str(analysis.resume_id),
            "job_id": str(analysis.job_id) if analysis.job_id else None,
            "match_score": analysis.match_score,
            "status": analysis.status.value,
            "analysis_type": analysis.analysis_type,
            "processing_time_ms": analysis.processing_time_ms,
            "created_at": analysis.created_at.isoformat() if analysis.created_at else None,
            "completed_at": analysis.completed_at.isoformat() if analysis.completed_at else None
        }
    
    @staticmethod
    def to_minimal(analysis: CompatibilityAnalysis) -> dict:
        """
        Converte entidade CompatibilityAnalysis para dados mínimos
        
        Args:
            analysis: Entidade CompatibilityAnalysis
            
        Returns:
            Dados mínimos
        """
        return {
            "analysis_id": str(analysis.analysis_id),
            "match_score": analysis.match_score,
            "status": analysis.status.value
        }
    
    @staticmethod
    def to_search_result(analysis: CompatibilityAnalysis, job_title: str = None) -> dict:
        """
        Converte entidade CompatibilityAnalysis para resultado de busca
        
        Args:
            analysis: Entidade CompatibilityAnalysis
            job_title: Título da vaga (opcional)
            
        Returns:
            Resultado de busca
        """
        return {
            "id": str(analysis.analysis_id),
            "type": "analysis",
            "title": f"Análise {analysis.analysis_type}",
            "description": f"Score: {analysis.match_score}%",
            "score": analysis.match_score,
            "created_at": analysis.created_at,
            "highlight": f"Compatibilidade: {analysis.match_score}%"
        }
    
    @staticmethod
    def to_bulk_result(analyses: List[CompatibilityAnalysis]) -> dict:
        """
        Converte lista de análises para resultado em lote
        
        Args:
            analyses: Lista de análises
            
        Returns:
            Resultado em lote
        """
        return {
            "total_analyses": len(analyses),
            "completed_analyses": len([a for a in analyses if a.status.value == "completed"]),
            "pending_analyses": len([a for a in analyses if a.status.value == "pending"]),
            "failed_analyses": len([a for a in analyses if a.status.value == "failed"]),
            "average_score": sum(a.match_score for a in analyses) / len(analyses) if analyses else 0.0,
            "analyses": [AnalysisMapper.to_list_item(a) for a in analyses]
        }
