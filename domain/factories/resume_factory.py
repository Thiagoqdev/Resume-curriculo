"""
Factory para criação de currículos
Seguindo padrão IT Valley
"""
from typing import Any
from uuid import uuid4
from datetime import datetime

from domain.helpers import _get, name_from, id_from, status_from
from domain.entities.domain import Resume, ResumeStatus


class ResumeFactory:
    """Factory para criação de currículos"""
    
    @staticmethod
    def make_resume(dto: Any, user_id: str) -> Resume:
        """
        Cria um currículo a partir de um DTO
        
        Args:
            dto: DTO com dados do currículo
            user_id: ID do usuário
            
        Returns:
            Currículo criado
            
        Raises:
            ValueError: Se dados inválidos
        """
        # Extrair dados usando helpers
        title = name_from(dto)
        version = _get(dto, "version", "v1.0")
        status = status_from(dto, ResumeStatus.DRAFT.value)
        
        # Validações específicas
        if len(title) < 1:
            raise ValueError("Título do currículo é obrigatório")
        
        if not user_id:
            raise ValueError("ID do usuário é obrigatório")
        
        # Criar currículo
        return Resume(
            resume_id=uuid4(),
            user_id=user_id,
            title=title.strip(),
            version=version,
            status=ResumeStatus(status),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            analysis_count=0,
            average_match_score=0.0
        )
    
    @staticmethod
    def make_resume_from_upload(dto: Any, user_id: str, file_info: dict) -> Resume:
        """
        Cria currículo a partir de upload
        
        Args:
            dto: DTO de upload
            user_id: ID do usuário
            file_info: Informações do arquivo
            
        Returns:
            Currículo criado
        """
        resume = ResumeFactory.make_resume(dto, user_id)
        
        # Adicionar informações do arquivo
        resume.data_lake_file_id = file_info.get("file_id")
        resume.original_filename = file_info.get("filename")
        resume.file_size = file_info.get("file_size")
        resume.file_type = file_info.get("file_type")
        
        return resume
    
    @staticmethod
    def make_resume_update(dto: Any, existing_resume: Resume) -> Resume:
        """
        Cria atualização de currículo
        
        Args:
            dto: DTO com dados de atualização
            existing_resume: Currículo existente
            
        Returns:
            Currículo atualizado
        """
        # Aplicar atualizações usando método da entidade
        existing_resume.aplicar_atualizacao_from_any(dto)
        existing_resume.updated_at = datetime.utcnow()
        
        return existing_resume
    
    @staticmethod
    def title_from(dto: Any) -> str:
        """
        Helper para extrair título do DTO
        
        Args:
            dto: DTO com título
            
        Returns:
            Título extraído
        """
        return name_from(dto)
    
    @staticmethod
    def version_from(dto: Any) -> str:
        """
        Helper para extrair versão do DTO
        
        Args:
            dto: DTO com versão
            
        Returns:
            Versão extraída
        """
        return _get(dto, "version", "v1.0")
    
    @staticmethod
    def status_from(dto: Any) -> str:
        """
        Helper para extrair status do DTO
        
        Args:
            dto: DTO com status
            
        Returns:
            Status extraído
        """
        return status_from(dto, ResumeStatus.DRAFT.value)
    
    @staticmethod
    def user_id_from(dto: Any) -> str:
        """
        Helper para extrair user_id do DTO
        
        Args:
            dto: DTO com user_id
            
        Returns:
            User ID extraído
        """
        return id_from(dto)
    
    @staticmethod
    def make_resume_search(dto: Any) -> dict:
        """
        Cria parâmetros de busca de currículos
        
        Args:
            dto: DTO de busca
            
        Returns:
            Parâmetros de busca
        """
        return {
            "search": _get(dto, "search"),
            "status": _get(dto, "status"),
            "created_after": _get(dto, "created_after"),
            "created_before": _get(dto, "created_before"),
            "sort_by": _get(dto, "sort_by", "created_at"),
            "sort_order": _get(dto, "sort_order", "desc"),
            "page": _get(dto, "page", 1),
            "page_size": _get(dto, "page_size", 20)
        }
