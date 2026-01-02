# tests/test_user_service.py
import pytest
from unittest.mock import MagicMock
from uuid import uuid4
from datetime import datetime, UTC
import asyncio # Adicionado para asyncio.run

from domain.entities.user_entity import User
from domain.factories.user_factory import UserFactory
from data.users.sql_user_repository import SQLUserRepository
from data.mongo_repository import UserPreferencesMongoRepository, ActivityLogMongoRepository
from services.user_service import UserService
from schemas.requests.requests import UserRegisterRequest, UserLoginRequest
from schemas.responses.responses import UserProfileResponse, TokenResponse # Adicionado para UserProfileResponse

# Fixture para um usuário de exemplo
@pytest.fixture
def sample_user():
    return User(
        id=uuid4(),
        full_name="Existing User",
        email="existing@example.com",
        password=UserFactory.hash_password("ExistingPassword123$"), # Senha hashada
        phone="+5511999998888",
        active=True, # CORRIGIDO: Adicionado o campo 'active'
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC)
    )

# Fixture para o mock do UserRepository
@pytest.fixture
def mock_user_repository():
    repo = MagicMock(spec=SQLUserRepository)
    return repo

@pytest.fixture
def mock_prefs_repository():
    repo = MagicMock(spec=UserPreferencesMongoRepository)
    return repo

@pytest.fixture
def mock_activity_repository():
    repo = MagicMock(spec=ActivityLogMongoRepository)
    return repo

# Fixture para o UserService com os mocks dos repositórios
@pytest.fixture
def user_service(mock_user_repository, mock_prefs_repository, mock_activity_repository):
    return UserService(
        user_repo=mock_user_repository,
        prefs_repo=mock_prefs_repository,
        activity_repo=mock_activity_repository
    )

# --- Testes para register_user ---
def test_register_user_success(user_service, mock_user_repository):
    """
    Verifica se o registro de usuário funciona com sucesso.
    """
    request_data = UserRegisterRequest(
        full_name="New User",
        email="new@example.com",
        password="NewStrongPassword123$",
        phone="+5511777776666"
    )
    
    # Simula que o usuário não existe
    mock_user_repository.get_user_by_email.return_value = None
    # Simula que o usuário é salvo com sucesso.
    # O UserService.register_user cria uma User entity e a passa para create_user.
    # Precisamos que o mock retorne uma User entity para que o UserService possa usá-la.
    mock_user_repository.create_user.side_effect = lambda user_entity: user_entity

    registered_user_profile_response = asyncio.run(user_service.register_user(request_data))

    # CORRIGIDO: O UserService.register_user retorna UserProfileResponse, não User
    assert isinstance(registered_user_profile_response, UserProfileResponse)
    assert registered_user_profile_response.email == request_data.email
    assert registered_user_profile_response.full_name == request_data.full_name
    # Não podemos verificar a senha hashada diretamente no UserProfileResponse
    mock_user_repository.get_user_by_email.assert_called_once_with(request_data.email)
    mock_user_repository.create_user.assert_called_once()


def test_register_user_email_already_exists(user_service, mock_user_repository, sample_user):
    """
    Verifica se o registro falha se o e-mail já existe.
    """
    request_data = UserRegisterRequest(
        full_name="Another User",
        email=sample_user.email, # E-mail já existente
        password="AnotherStrongPassword123$"
    )

    # Simula que o usuário já existe
    mock_user_repository.get_user_by_email.return_value = sample_user

    with pytest.raises(ValueError, match="Email already registered"):
        asyncio.run(user_service.register_user(request_data))

    mock_user_repository.get_user_by_email.assert_called_once_with(request_data.email)
    mock_user_repository.create_user.assert_not_called()

# --- Testes para authenticate_user ---
def test_authenticate_user_success(user_service, mock_user_repository, sample_user):
    """
    Verifica se a autenticação funciona com credenciais corretas.
    """
    login_request = UserLoginRequest(
        email=sample_user.email,
        password="ExistingPassword123$"
    )

    # Simula que o usuário é encontrado
    mock_user_repository.get_user_by_email.return_value = sample_user

    authenticated_token_response = asyncio.run(user_service.authenticate_user(login_request))

    assert isinstance(authenticated_token_response, TokenResponse) # CORRIGIDO: Retorna TokenResponse
    assert authenticated_token_response.token_type == "bearer"
    mock_user_repository.get_user_by_email.assert_called_once_with(login_request.email)

def test_authenticate_user_invalid_email(user_service, mock_user_repository):
    """
    Verifica se a autenticação falha com e-mail não registrado.
    """
    login_request = UserLoginRequest(
        email="nonexistent@example.com",
        password="AnyPassword123$"
    )

    # Simula que o usuário não é encontrado
    mock_user_repository.get_user_by_email.return_value = None

    with pytest.raises(ValueError, match="Invalid credentials"):
        asyncio.run(user_service.authenticate_user(login_request))

    mock_user_repository.get_user_by_email.assert_called_once_with(login_request.email)

def test_authenticate_user_invalid_password(user_service, mock_user_repository, sample_user):
    """
    Verifica se a autenticação falha com senha incorreta.
    """
    login_request = UserLoginRequest(
        email=sample_user.email,
        password="WrongPassword123$"
    )

    # Simula que o usuário é encontrado, mas com senha diferente
    mock_user_repository.get_user_by_email.return_value = sample_user

    with pytest.raises(ValueError, match="Invalid credentials"):
        asyncio.run(user_service.authenticate_user(login_request))

    mock_user_repository.get_user_by_email.assert_called_once_with(login_request.email)