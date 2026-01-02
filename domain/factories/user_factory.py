# domain/factories/user_factory.py
from uuid import uuid4
from datetime import datetime
from typing import Any
from bcrypt import hashpw, gensalt, checkpw # Importa as funções diretamente
from datetime import datetime, UTC

from domain.entities.user_entity import User
from domain.helpers import _get
from schemas.requests.requests import UserRegisterRequest # Ou UserCreateRequest

class UserFactory:
    @staticmethod
    def hash_password(password: str) -> str:
        # CORRIGIDO: Chamar hashpw e gensalt diretamente
        return hashpw(password.encode('utf-8'), gensalt()).decode('utf-8')

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        # CORRIGIDO: Chamar checkpw diretamente
        return checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

    @staticmethod
    def make(dto: UserRegisterRequest) -> User:
        """
        Cria uma nova entidade User a partir de um DTO (ex: UserRegisterRequest).
        Inclui validação de entrada e hashing de senha.
        """
        name = _get(dto, "name") # Usar "name"
        email = _get(dto, "email")
        password = _get(dto, "password")
        phone = _get(dto, "phone")

        # --- Validações de Negócio ---
        if not name or len(name.strip()) < 2: # Validar 'name'
            raise ValueError("Invalid name") # Mensagem de erro
        if not email:
            raise ValueError("Email is required")
        if not password:
            raise ValueError("Password is required")

        hashed_password = UserFactory.hash_password(password)
        now = datetime.now(UTC)
        
        user = User(
            id=uuid4(),
            name=name, # Passar 'name'
            email=email,
            password=hashed_password,
            phone=phone,
            active=True,
            created_at=now,
            updated_at=now
        )
        return user

    @staticmethod
    def email_from(dto: Any) -> str | None:
        return _get(dto, "email")

    @staticmethod
    def id_from(dto: Any) -> str | None:
        return _get(dto, "id")

    # Se você tiver outros métodos como make_user_update, eles precisarão ser atualizados
    # para usar 'name'.
    # @staticmethod
    # def make_user_update(dto: Any) -> dict:
    #     update_data = {}
    #     if _get(dto, "name"):
    #         update_data["name"] = _get(dto, "name")
    #     if _get(dto, "email"):
    #         update_data["email"] = _get(dto, "email")
    #     if _get(dto, "phone"):
    #         update_data["phone"] = _get(dto, "phone")
    #     return update_data