"""
Helpers para validação de dados
Seguindo padrão IT Valley
"""
from typing import Any, List, Dict
import re


def validate_required_fields(data: Any, required_fields: List[str]) -> None:
    """
    Valida se campos obrigatórios estão presentes
    
    Args:
        data: Dados a serem validados
        required_fields: Lista de campos obrigatórios
        
    Raises:
        ValueError: Se algum campo obrigatório estiver faltando
    """
    missing_fields = []
    
    for field in required_fields:
        if not _get_field_value(data, field):
            missing_fields.append(field)
    
    if missing_fields:
        raise ValueError(f"Campos obrigatórios faltando: {', '.join(missing_fields)}")


def validate_email_format(email: str) -> bool:
    """
    Valida formato de email
    
    Args:
        email: Email a ser validado
        
    Returns:
        True se válido, False caso contrário
    """
    if not email or not isinstance(email, str):
        return False
    
    # Regex básico para email
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email.strip()))


def validate_password_strength(password: str) -> bool:
    """
    Valida força da senha
    
    Args:
        password: Senha a ser validada
        
    Returns:
        True se forte, False caso contrário
    """
    if not password or not isinstance(password, str):
        return False
    
    if len(password) < 8:
        return False
    
    # Deve ter pelo menos uma letra maiúscula
    if not re.search(r'[A-Z]', password):
        return False
    
    # Deve ter pelo menos uma letra minúscula
    if not re.search(r'[a-z]', password):
        return False
    
    # Deve ter pelo menos um número
    if not re.search(r'\d', password):
        return False
    
    return True


def validate_phone_format(phone: str) -> bool:
    """
    Valida formato de telefone brasileiro
    
    Args:
        phone: Telefone a ser validado
        
    Returns:
        True se válido, False caso contrário
    """
    if not phone or not isinstance(phone, str):
        return False
    
    # Remove caracteres não numéricos
    clean_phone = re.sub(r'\D', '', phone)
    
    # Telefone brasileiro: 10 ou 11 dígitos
    return len(clean_phone) in [10, 11]


def validate_name_format(name: str) -> bool:
    """
    Valida formato de nome
    
    Args:
        name: Nome a ser validado
        
    Returns:
        True se válido, False caso contrário
    """
    if not name or not isinstance(name, str):
        return False
    
    # Deve ter pelo menos 2 caracteres
    if len(name.strip()) < 2:
        return False
    
    # Deve conter apenas letras, espaços e alguns caracteres especiais
    if not re.match(r'^[a-zA-ZÀ-ÿ\s\'-]+$', name.strip()):
        return False
    
    return True


def validate_uuid_format(uuid_str: str) -> bool:
    """
    Valida formato de UUID
    
    Args:
        uuid_str: UUID a ser validado
        
    Returns:
        True se válido, False caso contrário
    """
    if not uuid_str or not isinstance(uuid_str, str):
        return False
    
    # Regex para UUID v4
    pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$'
    return bool(re.match(pattern, uuid_str.lower()))


def validate_file_type(filename: str, allowed_types: List[str]) -> bool:
    """
    Valida tipo de arquivo
    
    Args:
        filename: Nome do arquivo
        allowed_types: Lista de extensões permitidas
        
    Returns:
        True se válido, False caso contrário
    """
    if not filename or not isinstance(filename, str):
        return False
    
    # Extrai extensão do arquivo
    extension = filename.lower().split('.')[-1] if '.' in filename else ''
    
    return extension in [ext.lower().lstrip('.') for ext in allowed_types]


def validate_file_size(file_size: int, max_size_mb: int) -> bool:
    """
    Valida tamanho do arquivo
    
    Args:
        file_size: Tamanho do arquivo em bytes
        max_size_mb: Tamanho máximo em MB
        
    Returns:
        True se válido, False caso contrário
    """
    if not isinstance(file_size, int) or file_size < 0:
        return False
    
    max_size_bytes = max_size_mb * 1024 * 1024
    return file_size <= max_size_bytes


def _get_field_value(data: Any, field: str) -> Any:
    """
    Helper interno para extrair valor de campo
    
    Args:
        data: Dados de origem
        field: Campo a ser extraído
        
    Returns:
        Valor do campo ou None
    """
    if data is None:
        return None
    
    # Se for um objeto com atributos
    if hasattr(data, field):
        return getattr(data, field)
    
    # Se for um dicionário
    elif isinstance(data, dict):
        return data.get(field)
    
    return None
