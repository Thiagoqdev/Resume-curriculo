import logging
from typing import Any, Dict, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from core.dependencies import get_current_user, get_resume_service
from schemas.requests.requests import ResumeCreateRequest, ResumeUpdateRequest
from schemas.responses.responses import BaseResponse
from schemas.responses.resume_responses import ResumeListResponse, ResumePublicResponse
from services.resume_service import ResumeService

logger = logging.getLogger(__name__)

"""Endpoints de Currículos"""

router = APIRouter(prefix="/resumes", tags=["Currículos"])


@router.post(
    "",
    response_model=ResumePublicResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar Novo Currículo (RES-001)",
)
async def criar_curriculo(
    request: ResumeCreateRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    resume_service: ResumeService = Depends(get_resume_service),
) -> ResumePublicResponse:
    """Criar novo currículo"""
    try:
        return await resume_service.criar_curriculo(current_user["user_id"], request)
    except ValueError as exc:
        logger.warning(f"Erro ao criar currículo: {exc}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    except Exception as exc:
        logger.error("Erro interno ao criar currículo", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.get(
    "/{resume_id}",
    response_model=ResumePublicResponse,
    summary="Buscar Currículo por ID (RES-002)",
)
async def buscar_curriculo(
    resume_id: UUID,
    current_user: Dict[str, Any] = Depends(get_current_user),
    resume_service: ResumeService = Depends(get_resume_service),
) -> ResumePublicResponse:
    """Buscar currículo por ID"""
    try:
        return await resume_service.buscar_curriculo(current_user["user_id"], resume_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))
    except Exception:
        logger.error("Erro interno ao buscar currículo", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.put(
    "/{resume_id}",
    response_model=ResumePublicResponse,
    summary="Atualizar Conteúdo do Currículo (RES-003)",
)
async def atualizar_curriculo(
    resume_id: UUID,
    request: ResumeUpdateRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    resume_service: ResumeService = Depends(get_resume_service),
) -> ResumePublicResponse:
    """Atualizar currículo criando uma nova versão"""
    try:
        return await resume_service.atualizar_curriculo(current_user["user_id"], resume_id, request)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))
    except Exception:
        logger.error("Erro interno ao atualizar currículo", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.delete(
    "/{resume_id}",
    response_model=BaseResponse,
    summary="Excluir Currículo (RES-004)",
)
async def excluir_curriculo(
    resume_id: UUID,
    current_user: Dict[str, Any] = Depends(get_current_user),
    resume_service: ResumeService = Depends(get_resume_service),
) -> BaseResponse:
    """Excluir currículo"""
    try:
        deleted = await resume_service.excluir_curriculo(current_user["user_id"], resume_id)
        if not deleted:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found")
        return BaseResponse(success=True, message="Resume deleted successfully")
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))
    except HTTPException:
        raise
    except Exception:
        logger.error("Erro interno ao excluir currículo", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.get(
    "",
    response_model=ResumeListResponse,
    summary="Listar Currículos do Usuário (RES-005)",
)
async def listar_curriculos(
    status_filter: Optional[str] = Query(default=None, alias="status"),
    current_user: Dict[str, Any] = Depends(get_current_user),
    resume_service: ResumeService = Depends(get_resume_service),
) -> ResumeListResponse:
    """Listar currículos do usuário"""
    try:
        return await resume_service.listar_curriculos(current_user["user_id"], status_filter)
    except Exception:
        logger.error("Erro interno ao listar currículos", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")