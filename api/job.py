import logging
from fastapi import APIRouter, Depends, status
from schemas.requests.requests import JobDescriptionCreateRequest, JobDescriptionUpdateRequest
from services.job_description_service import JobDescriptionService
from core.dependencies import get_job_service, get_current_user
from utils.haddlers import handle_exceptions, ensure_exists
from uuid import UUID
from schemas.responses.responses import JobDescriptionResponse
from typing import List
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/jobs", tags=["jobs"])

@router.post("/", response_model=JobDescriptionResponse)
async def create_job(
    request: JobDescriptionCreateRequest,
    service: JobDescriptionService = Depends(get_job_service),
    current_user: dict = Depends(get_current_user)
):
    try:
        user_uuid = current_user.get('user_id', None)
        return await service.add_job_description(request, created_by_user_uuid=user_uuid)
    except Exception as e: 
        handle_exceptions(e, "create_job")

@router.get("/all", response_model=List[JobDescriptionResponse])
async def list_my_jobs(
    service: JobDescriptionService = Depends(get_job_service),
    current_user: dict = Depends(get_current_user)
):
    try:
        user_uuid = current_user.get('user_id', None)
        jobs = await service.list_jobs_by_creator(user_uuid)
        return jobs
    except Exception as e:
        handle_exceptions(e, "list_my_jobs")


@router.get("/{job_id}", response_model=JobDescriptionResponse)
async def get_job(
    job_id: UUID,
    service: JobDescriptionService = Depends(get_job_service)
):
    try:
        job = await service.get_job_description(job_id) 
        return ensure_exists(job, "Job description")
    except Exception as e:
        handle_exceptions(e, "get_job")

@router.put("/{job_id}", response_model=JobDescriptionResponse)
async def update_job(
    job_id: UUID,
    request: JobDescriptionUpdateRequest,
    current_user: dict = Depends(get_current_user),
    service: JobDescriptionService = Depends(get_job_service)
):
    try:
        user_uuid = current_user.get("user_id") 
        return await service.update_job_description(job_id, request, user_uuid)
    except Exception as e:
        handle_exceptions(e, "update_job")

@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_job(
    job_id: UUID,
    service: JobDescriptionService = Depends(get_job_service),
    current_user: dict = Depends(get_current_user)
):
    try:
        user_uuid = current_user.get('user_id', None)
        await service.delete_job_description(job_id, current_user_uuid=user_uuid)
        return None
    except Exception as e:
        handle_exceptions(e, "delete_job")


