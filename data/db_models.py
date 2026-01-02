# data/db_models.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func # Para default values como GETUTCDATE()
from datetime import datetime # Para default values Python-side

Base = declarative_base()

# --- Modelos para as tabelas de referência ---

class TBStatusTypes(Base):
    __tablename__ = 'tb_status_types'
    __table_args__ = {'schema': 'users'}
    status_type_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False, unique=True)
    description = Column(String(255))
    users = relationship("TBUsers", back_populates="status_type")

class TBCredentialProviders(Base):
    __tablename__ = 'tb_credential_providers'
    __table_args__ = {'schema': 'users'}
    provider_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False, unique=True)
    description = Column(String(255))
    credentials = relationship("TBUserCredentials", back_populates="provider")

class TBContactTypes(Base):
    __tablename__ = 'tb_contact_types'
    __table_args__ = {'schema': 'users'}
    contact_type_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False, unique=True)
    description = Column(String(255))
    contacts = relationship("TBContacts", back_populates="contact_type")

# --- Modelos para as tabelas principais ---

class TBUsers(Base):
    __tablename__ = 'tb_users'
    __table_args__ = {'schema': 'users'}
    user_id = Column(Integer, primary_key=True, autoincrement=True)
    user_uuid = Column(String(36), unique=True, nullable=False) # UUID público
    display_name = Column("user_display_name", String(255), nullable=False)
    user_name = Column("user_name", String(255), nullable=True) # Exemplo, se necessário
    avatar_url = Column(String(255), nullable=True)
    status_type_id = Column(Integer, ForeignKey('users.tb_status_types.status_type_id'), nullable=False)
    created_at = Column(DateTime, server_default=func.getutcdate(), nullable=False)
    updated_at = Column(DateTime, server_default=func.getutcdate(), onupdate=func.getutcdate(), nullable=False)

    status_type = relationship("TBStatusTypes", back_populates="users")
    contacts = relationship("TBContacts", back_populates="user", cascade="all, delete-orphan")
    credentials = relationship("TBUserCredentials", back_populates="user", cascade="all, delete-orphan")
    settings = relationship("TBSettings", uselist=False, back_populates="user", cascade="all, delete-orphan")

class TBUserCredentials(Base):
    __tablename__ = 'tb_credentials'
    __table_args__ = {'schema': 'users'}
    credential_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.tb_users.user_id'), nullable=False)
    provider_id = Column(Integer, ForeignKey('users.tb_credential_providers.provider_id'), nullable=False)
    identifier = Column(String(255), nullable=False) # Ex: email para login
    password_hashed = Column(String(255), nullable=False) # Hash da senha
    #is_primary = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, server_default=func.getutcdate(), nullable=False)
    #updated_at = Column(DateTime, server_default=func.getutcdate(), onupdate=func.getutcdate(), nullable=False)

    user = relationship("TBUsers", back_populates="credentials")
    provider = relationship("TBCredentialProviders", back_populates="credentials")

class TBContacts(Base):
    __tablename__ = 'tb_contacts'
    __table_args__ = {'schema': 'users'}
    contact_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.tb_users.user_id'), nullable=False)
    contact_type_id = Column(Integer, ForeignKey('users.tb_contact_types.contact_type_id'), nullable=False)
    contact_value = Column(String(255), nullable=False)
    is_primary = Column(Boolean, default=False, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, server_default=func.getutcdate(), nullable=False)
    updated_at = Column(DateTime, server_default=func.getutcdate(), onupdate=func.getutcdate(), nullable=False)

    user = relationship("TBUsers", back_populates="contacts")
    contact_type = relationship("TBContactTypes", back_populates="contacts")

class TBSettings(Base):
    __tablename__ = 'tb_settings' # Confirme que este é o nome exato da tabela
    __table_args__ = {'schema': 'users'} # Mantenha esta linha
    setting_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.tb_users.user_id'), unique=True, nullable=False)
    language_id = Column(Integer, ForeignKey('refs.tb_languages.language_id'), nullable=False) # Assumindo que 'refs' é o schema para tabelas de referência
    timezone_id = Column(Integer, ForeignKey('refs.tb_timezones.timezone_id'), nullable=False) # Assumindo que 'refs' é o schema para tabelas de referência
    # <--- NOVAS COLUNAS CONFORME BANCO DE DADOS --->
    email_notifications_enabled = Column(Boolean, default=True, nullable=False) # Assumindo que é um booleano
    dark_mode_enabled = Column(Boolean, default=False, nullable=False) # Assumindo que é um booleano
    advanced_settings = Column(JSON, default={}, nullable=False) # Assumindo que é um tipo JSON no DB

    created_at = Column(DateTime, server_default=func.getutcdate(), nullable=False)
    updated_at = Column(DateTime, server_default=func.getutcdate(), onupdate=func.getutcdate(), nullable=False)

    user = relationship("TBUsers", back_populates="settings")
    language = relationship("TBLanguages") # Se você tiver modelos para refs.tb_languages
    timezone = relationship("TBTimezones") # Se você tiver modelos para refs.tb_timezones

# Se você tiver modelos para o schema 'refs', eles também devem estar aqui
# class TBLanguages(Base):
#     __tablename__ = 'tb_languages'
#     __table_args__ = {'schema': 'refs'}
#     language_id = Column(Integer, primary_key=True)
#     name = Column(String(50))
#     code = Column(String(10))
class TBLanguages(Base):
    __tablename__ = 'tb_languages'
    __table_args__ = {'schema': 'refs'} # Schema 'refs'
    language_id = Column(Integer, primary_key=True, autoincrement=True)
    language_code = Column(String(10), nullable=False, unique=True)
    language_name = Column(String(50), nullable=False)
    created_at = Column(DateTime, server_default=func.getutcdate(), nullable=False)

# class TBTimezones(Base):
#     __tablename__ = 'tb_timezones'
#     __table_args__ = {'schema': 'refs'}
#     timezone_id = Column(Integer, primary_key=True)
#     name = Column(String(100))
#     offset = Column(String(10))
class TBTimezones(Base):
    __tablename__ = 'tb_timezones'
    __table_args__ = {'schema': 'refs'} # Schema 'refs'
    timezone_id = Column(Integer, primary_key=True, autoincrement=True)
    timezone_name = Column(String(100), nullable=False, unique=True) # Ex: 'America/Sao_Paulo'
    offset = Column(String(10), nullable=False) # Ex: '-03:00'
    created_at = Column(DateTime, server_default=func.getutcdate(), nullable=False)