"""
Serviço de Currículos
"""
from typing import Optional
from uuid import UUID, uuid4

from data.sql_repository import ResumeRepository
from domain.entities.domain import Resume, ResumeStatus
from datetime import datetime
from schemas.requests.requests import ResumeCreateRequest, ResumeUpdateRequest
from schemas.responses.resume_responses import ResumeListResponse, ResumePublicResponse

class ResumeService:
    """Regras de negócio para currículos"""

    def __init__(self, resume_repository: ResumeRepository) -> None:
        self.resume_repository = resume_repository


    def _to_public_response(self, resume: Resume) -> ResumePublicResponse:
        """Converter entidade em DTO público"""
        return ResumePublicResponse(
            resume_id=resume.resume_id,
            resume_group_id=resume.resume_group_id,
            user_id=resume.user_id,
            title=resume.title,
            version_number=resume.version_number,
            version=resume.version,
            is_current=resume.is_current,
            status=resume.status,
            original_filename=resume.original_filename,
            file_size=resume.file_size,
            file_type=resume.file_type,
            created_at=resume.created_at,
            updated_at=resume.updated_at,
            last_analyzed_at=resume.last_analyzed_at,
            analysis_count=resume.analysis_count,
            average_match_score=resume.average_match_score,
        )
        
    async def criar_curriculo(self, user_id: UUID, dto: ResumeCreateRequest) -> ResumePublicResponse:
        """Criar novo currículo"""
        resume = Resume(
            resume_id=uuid4(),
            resume_group_id=uuid4(),
            user_id=user_id,
            title=dto.title.strip(),
            version_number=1,
            version=dto.version,
            is_current=True,
            status=ResumeStatus.DRAFT,
            original_filename=dto.original_filename,
            file_size=dto.file_size,
            file_type=dto.file_type,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        created = await self.resume_repository.add(resume)
        return self._to_public_response(created)
    async def buscar_curriculo(self, user_id: UUID, resume_id: UUID) -> ResumePublicResponse:
        """Buscar currículo por ID"""
        resume = await self.resume_repository.get_by_id(resume_id)
        if not resume:
            raise ValueError("Resume not found")

        if resume.user_id != user_id:
            raise PermissionError("Access denied to this resume")

        return self._to_public_response(resume)

    async def atualizar_curriculo(
        self,
        user_id: UUID,
        resume_id: UUID,
        dto: ResumeUpdateRequest,
    ) -> ResumePublicResponse:
        """Atualizar currículo criando uma nova versão"""
        existing = await self.resume_repository.get_by_id(resume_id)
        if not existing:
            raise ValueError("Resume not found")

        if existing.user_id != user_id:
            raise PermissionError("Access denied to this resume")

        new_version_number = existing.version_number + 1
        new_version = dto.version or f"v{new_version_number}.0"

        if existing.is_current:
            existing.is_current = False
            existing.updated_at = datetime.utcnow()
            await self.resume_repository.update(existing)

        new_resume = Resume(
            resume_id=uuid4(),
            resume_group_id=existing.resume_group_id,
            user_id=existing.user_id,
            title=dto.title or existing.title,
            version_number=new_version_number,
            version=new_version,
            is_current=True,
            status=dto.status or existing.status,
            data_lake_file_id=existing.data_lake_file_id,
            original_filename=dto.original_filename or existing.original_filename,
            file_size=dto.file_size if dto.file_size is not None else existing.file_size,
            file_type=dto.file_type or existing.file_type,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            last_analyzed_at=existing.last_analyzed_at,
            analysis_count=existing.analysis_count,
            average_match_score=existing.average_match_score,
        )

        created = await self.resume_repository.add(new_resume)
        return self._to_public_response(created)

    async def excluir_curriculo(self, user_id: UUID, resume_id: UUID) -> bool:
        """Excluir currículo"""
        resume = await self.resume_repository.get_by_id(resume_id)
        if not resume:
            raise ValueError("Resume not found")

        if resume.user_id != user_id:
            raise PermissionError("Access denied to this resume")

        return await self.resume_repository.delete(resume_id)

    async def listar_curriculos(
        self,
        user_id: UUID,
        status: Optional[str] = None,
    ) -> ResumeListResponse:
        """Listar currículos do usuário"""
        resumes = await self.resume_repository.list_by_user(user_id, status)
        responses = [self._to_public_response(resume) for resume in resumes]

        active_count = sum(1 for resume in resumes if resume.status == ResumeStatus.ACTIVE)
        draft_count = sum(1 for resume in resumes if resume.status == ResumeStatus.DRAFT)
        archived_count = sum(1 for resume in resumes if resume.status == ResumeStatus.ARCHIVED)

        return ResumeListResponse(
            resumes=responses,
            total_count=len(responses),
            active_count=active_count,
            draft_count=draft_count,
            archived_count=archived_count,
        )





"""
def create_new_resume(self, user_id: uuid4, dto: ResumeCreateRequest) -> Resume:
    resume_group_id = uuid4()

    resume = Resume(
        resume_id=uuid4(),
        resume_group_id=resume_group_id,
        user_id=user_id,
        title=dto.title,
        version_number=1,
        version="v1.0",
        is_current=True,
        status=ResumeStatus.DRAFT,
        original_filename=dto.original_filename,
        file_size=dto.file_size,
        file_type=dto.file_type,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

    return self.resume_repository.add(resume)

def search_resume(self, user_id: UIDD, resume_id: UUID) -> Resume:
   resume =  self.resume_repository.get_by__id(resume_id)

   if not resume:
       raise ValueError("Resume not found")
   
   if resume.user_id != user_id:
       raise PermissionError("Access denied to this resume")
   
   return resume

"""

