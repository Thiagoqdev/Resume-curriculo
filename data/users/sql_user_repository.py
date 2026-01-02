"""
Repositório SQL de Usuário (Corrigido para 7 Tabelas e IDs Hardcoded)

Usa o "Mapa" (db_models.py) e o "Tradutor" (user_mapper.py) 
para interagir com as 7 tabelas do BD Azure.
"""
import logging
from typing import Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

# O "Mapa" (as 7 tabelas)
from data.db_models import (
    TBUsers, 
    TBContacts, 
    TBContactTypes, 
    TBUserCredentials,
    TBSettings
)
# O "Tradutor"
from data.users.user_mapper import UserMapper
# A Entidade do Domínio (o que o Serviço usa)
from domain.entities.user_entity import User

logger = logging.getLogger(__name__)

# IDs de Referência (confirmados pelo DBA)
# Usamos isto para que o BD não precise de ser "seedado"
CONTACT_TYPE_ID_EMAIL = 1
PROVIDER_ID_EMAIL = 1
STATUS_TYPE_ID_ACTIVE = 1
STATUS_TYPE_ID_INACTIVE = 2 # ADICIONADO: Assumindo que 2 é o ID para status inativo

class SQLUserRepository:
    """
    Implementação do Repositório de Usuário para SQL Server.
    """
    
    def __init__(self, db: AsyncSession, mapper: UserMapper):
        self.db = db
        self.mapper = mapper

    async def _get_contact_by_email(self, email: str) -> Optional[TBContacts]:
        """
        Verifica se um email (contact_value) já existe na tabela de contatos.
        """
        try:
            stmt = (
                select(TBContacts)
                .where(
                    TBContacts.contact_type_id == CONTACT_TYPE_ID_EMAIL, # ID=1 (Email)
                    TBContacts.contact_value == email.lower() # Coluna correta
                )
            )
            result = await self.db.execute(stmt)
            return result.scalar_one_or_none()
        
        except Exception as e:
            logger.error(f"Erro ao buscar contato por email: {e}")
            raise ValueError(f"Internal error during database query: {e}")

    async def _get_credential_by_email(self, email: str) -> Optional[TBUserCredentials]:
        """
        Verifica se um email (identifier) já existe na tabela de credenciais.
        """
        try:
            stmt = (
                select(TBUserCredentials)
                .where(
                    TBUserCredentials.provider_id == PROVIDER_ID_EMAIL, # ID=1 (Email/Senha)
                    TBUserCredentials.identifier == email.lower() # Coluna correta
                )
            )
            result = await self.db.execute(stmt)
            return result.scalar_one_or_none()
        
        except Exception as e:
            logger.error(f"Erro ao buscar credencial por email: {e}")
            raise ValueError(f"Internal error during database query: {e}")

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Busca um usuário completo pelo email (usado no Login).
        Otimizado para buscar o usuário e suas credenciais/contatos em uma única query.
        """
        logger.info(f"Buscando usuário por email para login: {email}")
        try:
            # Busca o usuário através do contato de email e carrega as relações necessárias
            stmt = (
                select(TBUsers)
                .join(TBContacts, TBUsers.user_id == TBContacts.user_id)
                .options(
                    selectinload(TBUsers.contacts),
                    selectinload(TBUsers.credentials)
                )
                .where(
                    TBContacts.contact_type_id == CONTACT_TYPE_ID_EMAIL,
                    TBContacts.contact_value == email.lower()
                )
            )
            result = await self.db.execute(stmt)
            db_user = result.scalar_one_or_none()

            if not db_user:
                logger.warning(f"email not found: {email}")
                return None

            # Traduz o Modelo de BD (TBUsers) para a Entidade de Domínio (User)
            return self.mapper.to_domain(db_user)

        except Exception as e:
            logger.error(f"Erro ao buscar usuário por email para login: {e}")
            raise ValueError(f"Internal error during database query: {e}")
    
    async def get_user_by_id(self, user_id: UUID) -> Optional[User]:
        """
        Busca um usuário completo pelo ID (PK).
        """
        try:
            stmt = (
                select(TBUsers)
                .options(
                    selectinload(TBUsers.contacts),
                    selectinload(TBUsers.credentials),
                    selectinload(TBUsers.settings) 
                )
                 .where(TBUsers.user_uuid == str(user_id)) # <--- Busque por user_uuid
            )
            result = await self.db.execute(stmt)
            db_user = result.scalar_one_or_none()

            if not db_user:
                return None
            
            # 3. Traduz o Modelo de BD (TBUsers) para a Entidade de Domínio (User)
            return self.mapper.to_domain(db_user)

        except Exception as e:
            logger.error(f"Erro ao buscar usuário por ID: {e}")
            raise ValueError(f"Internal error during database query: {e}")

    async def create_user(self, user: User) -> User:
        """
        Cria um novo usuário (USR-001).
        Recebe a Entidade de Domínio (User) e a divide nas 7 tabelas.
        """
        logger.info(f"Iniciando criação do usuário: {user.email}")
        try:
            # 1. Verifica se o email (contato) já existe
            existing_contact = await self._get_contact_by_email(user.email)
            if existing_contact:
                raise ValueError("Email already exists (contact)")

            # 2. Verifica se o email (credencial) já existe
            existing_credential = await self._get_credential_by_email(user.email)
            if existing_credential:
                raise ValueError("Email already exists (credential)")

            # 3. Traduz a Entidade (User) para os Modelos de BD (TBUsers, etc.)
            # (Usando os IDs de referência hardcoded)
            db_user, db_contact, db_credential, db_settings = self.mapper.to_persistence(
                user=user,
                status_type_id=STATUS_TYPE_ID_ACTIVE if user.active else STATUS_TYPE_ID_INACTIVE, # CORRIGIDO: Passa o ID correto baseado em user.active
                contact_type_id=CONTACT_TYPE_ID_EMAIL,
                provider_id=PROVIDER_ID_EMAIL
            )

            # 4. Adiciona tudo à sessão (transação)
            self.db.add(db_user)
            # O 'flush' é necessário para que o 'db_user.user_id' (autoincrement)
            # seja gerado pelo BD e possa ser usado nas tabelas filhas.
            await self.db.flush()

            # 5. Atribui o novo ID às tabelas filhas
            db_contact.user_id = db_user.user_id
            db_credential.user_id = db_user.user_id
            db_settings.user_id = db_user.user_id
            
            self.db.add(db_contact)
            self.db.add(db_credential)
            self.db.add(db_settings)
            
            # 6. Salva (Commit) a transação
            await self.db.commit()
            
            # 7. Retorna a entidade atualizada (agora com o ID do BD)
            stmt = (
                select(TBUsers)
                .options(
                    selectinload(TBUsers.contacts),
                    selectinload(TBUsers.credentials),
                    selectinload(TBUsers.settings)
                )
                .where(TBUsers.user_id == db_user.user_id)
            )
            result = await self.db.execute(stmt)
            fully_loaded_db_user = result.scalar_one() 
            
            logger.info(f"Usuário criado com sucesso, ID interno: {db_user.user_id}, UUID: {db_user.user_uuid}")
            return self.mapper.to_domain(fully_loaded_db_user)

        except Exception as e:
            logger.error(f"Erro ao criar usuário: {e}")
            await self.db.rollback()
            raise ValueError(f"Internal error during user creation: {e}")

    async def update_user(self, user_id: UUID, user: User) -> Optional[User]: 
        # (Lógica de atualização - pode ser implementada depois)
        pass