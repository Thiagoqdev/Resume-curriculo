# data/users/user_mapper.py
from typing import Optional, Tuple
from uuid import UUID, uuid4
from datetime import datetime

# A Entidade do Domínio (o que o Serviço usa)
from domain.entities.user_entity import User

# O "Mapa" (as 7 tabelas)
from data.db_models import (
    TBUsers, 
    TBContacts, 
    TBContactTypes, 
    TBUserCredentials, 
    TBCredentialProviders, 
    TBStatusTypes,
    TBSettings
)

# IDs de Referência (confirmados pelo DBA)
CONTACT_TYPE_ID_EMAIL = 1
PROVIDER_ID_EMAIL = 1
STATUS_TYPE_ID_ACTIVE = 1
STATUS_TYPE_ID_INACTIVE = 2 # Assumindo que 2 é para inativo

class UserMapper:
    """
    Traduz entre a Entidade de Domínio 'User' e os 
    Modelos de BD 'TBUsers', 'TBContacts', 'TBCredentials', e 'TBSettings'.
    """

    def to_domain(self, db_user: TBUsers) -> User:
        """
        Converte um modelo TBUsers (com relações carregadas) para a Entidade User.
        """
        email = None
        phone = None
        if db_user.contacts:
            for contact in db_user.contacts:
                if contact.contact_type_id == CONTACT_TYPE_ID_EMAIL:
                    email = contact.contact_value
                # Adicione lógica para extrair telefone se houver um contact_type_id para ele
                # elif contact.contact_type_id == CONTACT_TYPE_ID_PHONE:
                #     phone = contact.contact_value
        
        password_hash = None
        if db_user.credentials:
            for cred in db_user.credentials:
                if cred.provider_id == PROVIDER_ID_EMAIL:
                    password_hash = cred.password_hashed
                    break

        return User(
            id=UUID(db_user.user_uuid),
            name=db_user.display_name, # Mapeia db_user.display_name para entity.name
            email=email or "",
            password=password_hash or "",
            phone=phone,
            avatar_url=db_user.avatar_url,
            created_at=db_user.created_at,
            updated_at=db_user.updated_at,
            active=(db_user.status_type_id == STATUS_TYPE_ID_ACTIVE)
        )

    def to_persistence(
        self, 
        user: User,
        status_type_id: int,
        contact_type_id: int,
        provider_id: int
    ) -> Tuple[TBUsers, TBContacts, TBUserCredentials, TBSettings]:
        """
        Converte a Entidade (User) para os modelos de BD necessários para um novo registo.
        """
        # 1. Cria o Modelo TBUsers
        db_user = TBUsers(
            user_uuid=str(user.id),
            display_name=user.name,
            user_name=user.name,
            avatar_url=user.avatar_url,
            status_type_id=status_type_id,
            # created_at e updated_at são gerados pelo BD (server_default)
            # Não devem ser passados explicitamente aqui.
        )
        
        # 2. Cria o Modelo TBContacts (para o email)
        db_contact = TBContacts(
            contact_type_id=contact_type_id,
            contact_value=user.email.lower(),
            is_primary=True,
            is_verified=False,
            # created_at e updated_at são gerados pelo BD (server_default)
            # Não devem ser passados explicitamente aqui.
        )
        
        # 3. Cria o Modelo TBUserCredentials (para a senha)
        db_credential = TBUserCredentials(
            provider_id=provider_id,
            identifier=user.email.lower(),
            password_hashed=user.password,
            # 'is_active' NÃO É UMA COLUNA em TBUserCredentials, REMOVIDO.
            # 'created_at' é gerado pelo BD (server_default), REMOVIDO.
            # 'updated_at' NÃO É UMA COLUNA em TBUserCredentials, REMOVIDO.
        )
        
        # 4. Cria o Modelo TBSettings (com as preferências padrão)
        db_settings = TBSettings(
            language_id=1,
            timezone_id=1,
            email_notifications_enabled=True,
            dark_mode_enabled=False,
            advanced_settings={},
            # created_at e updated_at são gerados pelo BD (server_default)
            # Não devem ser passados explicitamente aqui.
        )
        
        return db_user, db_contact, db_credential, db_settings

    @staticmethod
    def to_public(user: User) -> dict:
        """
        Converte entidade User para resposta pública (ajustado para a nova entidade).
        """
        return {
            "user_id": str(user.id),
            "email": user.email,
            "name": user.name,
            "phone": user.phone,
            "avatar_url": user.avatar_url,
            "created_at": user.created_at,
            # Remova ou adicione os campos abaixo se existirem na sua entidade User
            # "subscription_type": user.subscription_type,
            # "last_login_at": user.last_login_at,
            # "email_verified": user.email_verified,
            # "two_factor_enabled": user.two_factor_enabled
        }