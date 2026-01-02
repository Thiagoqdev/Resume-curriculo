"""
Factory para criação de análises
Seguindo padrão IT Valley
"""
from typing import Any
from uuid import uuid4
from datetime import datetime

from domain.helpers import _get, id_from, status_from
from domain.entities.domain import CompatibilityAnalysis, AnalysisStatus


class AnalysisFactory:
    """Factory para criação de análises"""
    
    @staticmethod
    def make_analysis(dto: Any, user_id: str) -> CompatibilityAnalysis:
        """
        Cria uma análise a partir de um DTO
        
        Args:
            dto: DTO com dados da análise
            user_id: ID do usuário
            
        Returns:
            Análise criada
            
        Raises:
            ValueError: Se dados inválidos
        """
        # Extrair dados usando helpers
        resume_id = _get(dto, "resume_id")
        job_id = _get(dto, "job_id")
        job_description = _get(dto, "job_description")
        analysis_type = _get(dto, "analysis_type", "job_match")
        
        # Validações específicas
        if not resume_id:
            raise ValueError("ID do currículo é obrigatório")
        
        if not user_id:
            raise ValueError("ID do usuário é obrigatório")
        
        if not job_id and not job_description:
            raise ValueError("ID da vaga ou descrição da vaga é obrigatório")
        
        # Criar análise
        return CompatibilityAnalysis(
            analysis_id=uuid4(),
            user_id=user_id,
            resume_id=resume_id,
            job_id=job_id,
            match_score=0.0,  # Será calculado pela IA
            status=AnalysisStatus.PENDING,
            analysis_type=analysis_type,
            created_at=datetime.utcnow()
        )
    
    @staticmethod
    def make_bulk_analysis(dto: Any, user_id: str) -> list:
        """
        Cria análises em lote
        
        Args:
            dto: DTO com dados das análises
            user_id: ID do usuário
            
        Returns:
            Lista de análises criadas
        """
        resume_ids = _get(dto, "resume_ids", [])
        job_id = _get(dto, "job_id")
        
        if not resume_ids:
            raise ValueError("IDs dos currículos são obrigatórios")
        
        if not job_id:
            raise ValueError("ID da vaga é obrigatório")
        
        analyses = []
        for resume_id in resume_ids:
            analysis_dto = {
                "resume_id": resume_id,
                "job_id": job_id,
                "analysis_type": "bulk_match"
            }
            analyses.append(AnalysisFactory.make_analysis(analysis_dto, user_id))
        
        return analyses
    
    @staticmethod
    def make_analysis_update(dto: Any, existing_analysis: CompatibilityAnalysis) -> CompatibilityAnalysis:
        """
        Cria atualização de análise
        
        Args:
            dto: DTO com dados de atualização
            existing_analysis: Análise existente
            
        Returns:
            Análise atualizada
        """
        # Aplicar atualizações usando método da entidade
        existing_analysis.aplicar_atualizacao_from_any(dto)
        existing_analysis.updated_at = datetime.utcnow()
        
        return existing_analysis
    
    @staticmethod
    def resume_id_from(dto: Any) -> str:
        """
        Helper para extrair resume_id do DTO
        
        Args:
            dto: DTO com resume_id
            
        Returns:
            Resume ID extraído
        """
        return id_from(dto)
    
    @staticmethod
    def job_id_from(dto: Any) -> str:
        """
        Helper para extrair job_id do DTO
        
        Args:
            dto: DTO com job_id
            
        Returns:
            Job ID extraído
        """
        return _get(dto, "job_id")
    
    @staticmethod
    def analysis_type_from(dto: Any) -> str:
        """
        Helper para extrair analysis_type do DTO
        
        Args:
            dto: DTO com analysis_type
            
        Returns:
            Analysis type extraído
        """
        return _get(dto, "analysis_type", "job_match")
    
    @staticmethod
    def status_from(dto: Any) -> str:
        """
        Helper para extrair status do DTO
        
        Args:
            dto: DTO com status
            
        Returns:
            Status extraído
        """
        return status_from(dto, AnalysisStatus.PENDING.value)
    
    @staticmethod
    def make_analysis_search(dto: Any) -> dict:
        """
        Cria parâmetros de busca de análises
        
        Args:
            dto: DTO de busca
            
        Returns:
            Parâmetros de busca
        """
        return {
            "search": _get(dto, "search"),
            "resume_id": _get(dto, "resume_id"),
            "job_id": _get(dto, "job_id"),
            "min_score": _get(dto, "min_score"),
            "max_score": _get(dto, "max_score"),
            "created_after": _get(dto, "created_after"),
            "created_before": _get(dto, "created_before"),
            "sort_by": _get(dto, "sort_by", "created_at"),
            "sort_order": _get(dto, "sort_order", "desc"),
            "page": _get(dto, "page", 1),
            "page_size": _get(dto, "page_size", 20)
        }
    
    @staticmethod
    def make_analysis_result(analysis: CompatibilityAnalysis, ai_result: dict) -> CompatibilityAnalysis:
        """
        Cria resultado de análise com dados da IA
        
        Args:
            analysis: Análise existente
            ai_result: Resultado da IA
            
        Returns:
            Análise com resultado
        """
        # Atualizar com resultado da IA
        analysis.match_score = ai_result.get("overall_score", 0.0)
        analysis.status = AnalysisStatus.COMPLETED
        analysis.completed_at = datetime.utcnow()
        analysis.processing_time_ms = ai_result.get("processing_time_ms")
        analysis.mongo_analysis_id = ai_result.get("mongo_analysis_id")
        
        return analysis
