import logging
from typing import Optional
from uuid import UUID
from fastapi import HTTPException, status

logger = logging.getLogger(__name__)

def handle_exceptions(e: Exception, context: str, bad_request_status: int = status.HTTP_400_BAD_REQUEST):
    """Manipula exceções comuns e levanta HTTPException apropriada."""
    if isinstance(e, ValueError):
        logger.warning(f"Falha no {context} ({bad_request_status}): {e}")
        raise HTTPException(
            status_code=bad_request_status,
            detail=str(e)
        )
    elif isinstance(e, HTTPException):
        raise e
    else:
        logger.error(f"Error in {context}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

def ensure_exists(obj, entity_name: str):
    """Verifica se o objeto existe, senão levanta 404."""
    if not obj:
        logger.warning(f"{entity_name} not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{entity_name} not found"
        )
    return obj

async def resolve_id_from_uuid(
    repo,
    value,
    table: str,
    uuid_column: str,
    id_column: str
) -> Optional[int]:
    """
    Resolve um valor que pode ser UUID ou int para o id correspondente no banco.
    - Se for UUID, busca na tabela e retorna o id.
    - Se já for int, retorna direto.
    - Se não encontrar, retorna None.
    """
    if isinstance(value, UUID):
        try:
            rows = repo.execute_query(
                f"SELECT {id_column} FROM {table} WHERE {uuid_column} = :uuid",
                {"uuid": str(value)}
            )
            if rows:
                return rows[0].get(id_column)
            # If UUID provided but not found in table, do not convert UUID to int — return None
            return None
        except Exception:
            return None

    # If value is not a UUID instance, try to interpret it as an int id
    try:
        return int(value)
    except Exception:
        return None
