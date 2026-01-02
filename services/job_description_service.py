"""Serviço para gerenciamento de vaga"""
from typing import List, Optional
from uuid import UUID, uuid4
from datetime import datetime
import logging
from data.sql_repository import JobRepository
from schemas.requests.requests import JobDescriptionCreateRequest, JobDescriptionUpdateRequest
from domain.entities.domain import JobDescription
from schemas.responses.responses import JobDescriptionResponse
from utils.haddlers import resolve_id_from_uuid

logger = logging.getLogger(__name__)


class JobDescriptionService:
    def __init__(self, repo: JobRepository):
        self.repo = repo

    async def add_job_description(self, request: JobDescriptionCreateRequest, created_by_user_uuid: Optional[str] = None) -> JobDescriptionResponse:
        job_id = uuid4()
        job = JobDescription(
            job_id=job_id,
            company_id=request.company_id,
            title=request.title,
            location=request.location,
            job_type=request.job_type,
            salary_range=request.salary_range,
            experience_level=request.experience_level,
            description=request.description,
            requirements=request.requirements,
            benefits=request.benefits,
            posted_at=datetime.utcnow(),
            expires_at=request.expires_at,
            is_active=True
        )

        try:
            created = await self.repo.add(job, created_by_user_uuid=created_by_user_uuid)
            logger.info(f"Job description created: {created.job_id}")
            return JobDescriptionResponse(
                job_id=created.job_id,
                company=None,
                title=created.title,
                location=created.location,
                job_type=created.job_type,
                salary_range=created.salary_range,
                experience_level=created.experience_level,
                description=created.description,
                requirements=created.requirements,
                benefits=created.benefits,
                posted_at=created.posted_at,
                expires_at=created.expires_at,
                is_active=created.is_active,
                view_count=0,
                application_count=0
            )
        except Exception as e:
            logger.error(f"Failed to create job description: {e}", exc_info=True)
            raise


    async def get_job_description(self, job_id: UUID) -> Optional[JobDescriptionResponse]:
        """Recupera uma descrição de vaga pelo ID."""
        job = await self.repo.get_by_id(job_id)
        if not job:
            logger.warning(f"Job description not found: {job_id}")
            return None

        logger.info(f"Job description retrieved: {job.job_id}")
        return JobDescriptionResponse(
            job_id=job.job_id,
            company=None,
            title=job.title,
            location=job.location,
            job_type=job.job_type,
            salary_range=job.salary_range,
            experience_level=job.experience_level,
            description=job.description,
            requirements=job.requirements,
            benefits=job.benefits,
            posted_at=job.posted_at,
            expires_at=job.expires_at,
            is_active=job.is_active,
            view_count=getattr(job, 'view_count', 0),
            application_count=getattr(job, 'application_count', 0)
        )
    
    async def update_job_description(self, job_id: UUID, request: JobDescriptionUpdateRequest, current_user_uuid: Optional[UUID] = None) -> JobDescriptionResponse:
        """Atualiza uma descrição de vaga existente com os dados fornecidos.

        Apenas o usuário que criou a vaga (`created_by_user_id`) pode atualizá-la.
        """
        if not current_user_uuid:
            raise ValueError("Authentication required")
        existing = await self.repo.get_by_id(job_id)
        if not existing:
            raise ValueError("Job description not found")
        resolved = None
        try:
            resolved= await resolve_id_from_uuid(
                self.repo,
                current_user_uuid,
                "users.tb_users",
                "user_uuid",
                "user_id"
            )
            if resolved is None:
                raise ValueError("Authenticated user not found")

        except Exception:
            raise ValueError("Authenticated user not found")

        if int(existing.created_by_user_id) != int(resolved):
            raise ValueError("User not authorized to update this job")

        update_data = request.dict(exclude_unset=True)
        job = await self.repo.update(job_id, update_data)
        if not job:
            raise ValueError("Job description not found after update")

        return JobDescriptionResponse(
            job_id=job.job_id,
            company=None,
            title=job.title,
            location=job.location,
            job_type=job.job_type,
            salary_range=job.salary_range,
            experience_level=job.experience_level,
            description=job.description,
            requirements=job.requirements,
            benefits=job.benefits,
            posted_at=job.posted_at,
            expires_at=job.expires_at,
            is_active=job.is_active,
            view_count=getattr(job, 'view_count', 0),
            application_count=getattr(job, 'application_count', 0)
        )

    async def delete_job_description(self, job_id: UUID, current_user_uuid: Optional[UUID] = None) -> bool:
        """Deleta uma descrição de vaga apenas se o usuário autenticado for o criador."""
        if not current_user_uuid:
            raise ValueError("Authentication required")

        existing = await self.repo.get_by_id(job_id)
        if not existing:
            raise ValueError("Job description not found")

        resolved = None
        try:
            resolved= await resolve_id_from_uuid(
                self.repo,
                current_user_uuid,
                "users.tb_users",
                "user_uuid",
                "user_id"
            )
            if resolved is None:
                raise ValueError("Authenticated user not found")
        
        except Exception:
            raise ValueError("Authenticated user not found")

        if existing.created_by_user_id is None or int(existing.created_by_user_id) != int(resolved):
            raise ValueError("User not authorized to delete this job")

        deleted = await self.repo.delete(job_id)
        if not deleted:
            raise ValueError("Job description not found or could not be deleted")

        logger.info(f"Job description deleted: {job_id}")
        return True

    async def list_jobs_by_creator(self, current_user_uuid: UUID) -> List[JobDescriptionResponse]:
        resolved = await resolve_id_from_uuid(
            self.repo,
            current_user_uuid,
            "users.tb_users",
            "user_uuid",
            "user_id"
        )
        if resolved is None:
            raise ValueError("Authenticated user not found")

        jobs = await self.repo.list_by_creator_id(resolved)
        responses = []
        for job in jobs:
            responses.append(JobDescriptionResponse(
                job_id=job.job_id,
                company=None,
                title=job.title,
                location=job.location,
                job_type=job.job_type,
                salary_range=job.salary_range,
                experience_level=job.experience_level,
                description=job.description,
                requirements=job.requirements,
                benefits=job.benefits,
                posted_at=job.posted_at,
                expires_at=job.expires_at,
                is_active=job.is_active,
                view_count=getattr(job, 'view_count', 0),
                application_count=getattr(job, 'application_count', 0)
            ))
        return responses
