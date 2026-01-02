"""
Helpers para extração segura de dados
Seguindo padrão IT Valley
"""
from typing import Any, Optional


def _get(data: Any, key: str, default: Any = None) -> Any:
    """
    Helper para extrair dados de forma segura de qualquer fonte
    
    Args:
        data: Dados de origem (DTO, dict, objeto)
        key: Chave/campo a ser extraído
        default: Valor padrão se não encontrar
        
    Returns:
        Valor extraído ou default
    """
    if data is None:
        return default
    
    # Se for um objeto com atributos
    if hasattr(data, key):
        value = getattr(data, key)
        return value if value is not None else default
    
    # Se for um dicionário
    elif isinstance(data, dict):
        return data.get(key, default)
    
    # Se for uma lista/tupla com índice
    elif isinstance(data, (list, tuple)) and isinstance(key, int):
        try:
            return data[key] if 0 <= key < len(data) else default
        except (IndexError, TypeError):
            return default
    
    return default


def email_from(dto: Any) -> str:
    """
    Extrai email de forma segura de qualquer DTO
    
    Args:
        dto: DTO ou objeto com email
        
    Returns:
        Email extraído
        
    Raises:
        ValueError: Se email não for encontrado ou for inválido
    """
    email = _get(dto, "email")
    
    if not email:
        raise ValueError("Email é obrigatório")
    
    if not isinstance(email, str) or "@" not in email:
        raise ValueError("Email deve ter formato válido")
    
    return email.strip().lower()


def id_from(dto: Any) -> Optional[str]:
    """
    Extrai ID de forma segura de qualquer DTO
    
    Args:
        dto: DTO ou objeto com ID
        
    Returns:
        ID extraído ou None
    """
    return _get(dto, "id") or _get(dto, "user_id") or _get(dto, "resume_id")


def name_from(dto: Any) -> str:
    """
    Extrai nome de forma segura de qualquer DTO
    
    Args:
        dto: DTO ou objeto com nome
        
    Returns:
        Nome extraído
        
    Raises:
        ValueError: Se nome não for encontrado ou for inválido
    """
    name = _get(dto, "name") or _get(dto, "full_name") or _get(dto, "title")
    
    if not name:
        raise ValueError("Nome é obrigatório")
    
    if not isinstance(name, str) or len(name.strip()) < 2:
        raise ValueError("Nome deve ter pelo menos 2 caracteres")
    
    return name.strip()


def phone_from(dto: Any) -> Optional[str]:
    """
    Extrai telefone de forma segura de qualquer DTO
    
    Args:
        dto: DTO ou objeto com telefone
        
    Returns:
        Telefone extraído ou None
    """
    phone = _get(dto, "phone") or _get(dto, "telefone")
    
    if phone and isinstance(phone, str):
        # Remove caracteres não numéricos
        clean_phone = ''.join(filter(str.isdigit, phone))
        return clean_phone if clean_phone else None
    
    return None


def status_from(dto: Any, default: str = "ativo") -> str:
    """
    Extrai status de forma segura de qualquer DTO
    
    Args:
        dto: DTO ou objeto com status
        default: Status padrão se não encontrar
        
    Returns:
        Status extraído ou default
    """
    status = _get(dto, "status")
    
    if status and isinstance(status, str):
        return status.strip().lower()
    
    return default


def created_at_from(dto: Any) -> Optional[str]:
    """
    Extrai data de criação de forma segura de qualquer DTO
    
    Args:
        dto: DTO ou objeto com created_at
        
    Returns:
        Data de criação ou None
    """
    return _get(dto, "created_at") or _get(dto, "createdAt")


def updated_at_from(dto: Any) -> Optional[str]:
    """
    Extrai data de atualização de forma segura de qualquer DTO
    
    Args:
        dto: DTO ou objeto com updated_at
        
    Returns:
        Data de atualização ou None
    """
    return _get(dto, "updated_at") or _get(dto, "updatedAt")
