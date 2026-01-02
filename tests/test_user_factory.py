# tests/test_user_factory.py
import pytest
from uuid import UUID
from datetime import datetime
from domain.entities.user_entity import User
from domain.factories.user_factory import UserFactory
from schemas.requests.requests import UserRegisterRequest # Usando o DTO canônico

@pytest.fixture
def user_register_request_data():
    """Fixture para dados de registro de usuário válidos."""
    return UserRegisterRequest(
        full_name="Test User",
        email="test@example.com",
        password="StrongPassword123$",
        phone="+5511987654321"
    )

def test_user_factory_make_creates_user_entity(user_register_request_data):
    """
    Verifica se a UserFactory cria uma instância de User com os dados corretos
    e se a senha é hashada.
    """
    user = UserFactory.make(user_register_request_data)

    assert isinstance(user, User)
    assert isinstance(user.id, UUID)
    assert user.full_name == user_register_request_data.full_name
    assert user.email == user_register_request_data.email
    assert user.phone == user_register_request_data.phone
    assert user.active == True # Valor padrão esperado
    assert isinstance(user.created_at, datetime)
    assert isinstance(user.updated_at, datetime)
    assert user.created_at == user.updated_at
    assert user.password != user_register_request_data.password # Senha deve ser hashada
    assert UserFactory.verify_password(user_register_request_data.password, user.password)

def test_user_factory_make_with_missing_phone(user_register_request_data):
    """
    Verifica se a UserFactory cria uma instância de User mesmo sem o telefone.
    """
    data_without_phone = user_register_request_data.copy(update={"phone": None})
    user = UserFactory.make(data_without_phone)

    assert isinstance(user, User)
    assert user.phone is None
    assert user.email == data_without_phone.email

def test_user_factory_verify_password_correctly():
    """
    Verifica se o método verify_password funciona corretamente.
    """
    password = "MySecretPassword123!"
    hashed_password = UserFactory.hash_password(password)
    assert UserFactory.verify_password(password, hashed_password)

def test_user_factory_verify_password_incorrectly():
    """
    Verifica se o método verify_password falha com senha incorreta.
    """
    password = "MySecretPassword123!"
    hashed_password = UserFactory.hash_password(password)
    assert not UserFactory.verify_password("WrongPassword", hashed_password)