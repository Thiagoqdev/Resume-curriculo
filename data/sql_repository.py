"""
Repositório SQL Server
Camada de acesso a dados para SQL Server
"""
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime
from sqlalchemy import create_engine, text, and_, or_, desc, asc
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
import logging

from core.config import settings
from domain.entities.domain import (
    User, Resume, Company, JobDescription, CompatibilityAnalysis,
    CoverLetter, Skill, UserSkill, Notification, UserSession, DataLakeFile
)

logger = logging.getLogger(__name__)


class SQLRepository:
    """Repositório base para SQL Server"""
    
    def __init__(self):
        self.engine = create_engine(
            settings.sql_connection_string,
            pool_size=10,
            max_overflow=20,
            pool_timeout=30,
            pool_recycle=3600,
            echo=settings.DEBUG
        )
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
    
    def get_session(self) -> Session:
        """Obter sessão do banco"""
        return self.SessionLocal()
    
    def execute_query(self, query: str, params: Dict[str, Any] = None) -> List[Dict]:
        """Executar query SQL raw"""
        try:
            with self.get_session() as session:
                result = session.execute(text(query), params or {})
                return [dict(row._mapping) for row in result]
        except SQLAlchemyError as e:
            logger.error(f"SQL query error: {e}")
            raise
    
    def execute_scalar(self, query: str, params: Dict[str, Any] = None) -> Any:
        """Executar query que retorna valor único"""
        try:
            with self.get_session() as session:
                result = session.execute(text(query), params or {})
                return result.scalar()
        except SQLAlchemyError as e:
            logger.error(f"SQL scalar query error: {e}")
            raise


class UserRepository(SQLRepository):
    """Repositório de usuários"""
    
    async def create_user(self, user: User) -> User:
        """Criar novo usuário"""
        query = """
        EXEC sp_CreateUser 
            @Email = :email,
            @PasswordHash = :password_hash,
            @FullName = :full_name,
            @Phone = :phone
        """
        params = {
            "email": user.email,
            "password_hash": user.password_hash,
            "full_name": user.full_name,
            "phone": user.phone
        }
        
        result = self.execute_scalar(query, params)
        user.user_id = result
        return user
    
    async def get_user_by_id(self, user_id: UUID) -> Optional[User]:
        """Buscar usuário por ID"""
        query = """
        SELECT UserId, Email, PasswordHash, FullName, Phone, AvatarUrl,
               SubscriptionType, CreatedAt, UpdatedAt, LastLoginAt,
               IsActive, EmailVerified, TwoFactorEnabled
        FROM Users 
        WHERE UserId = :user_id AND IsActive = 1
        """
        
        result = self.execute_query(query, {"user_id": str(user_id)})
        if not result:
            return None
        
        row = result[0]
        return User(
            user_id=UUID(row["UserId"]),
            email=row["Email"],
            password_hash=row["PasswordHash"],
            full_name=row["FullName"],
            phone=row["Phone"],
            avatar_url=row["AvatarUrl"],
            subscription_type=row["SubscriptionType"],
            created_at=row["CreatedAt"],
            updated_at=row["UpdatedAt"],
            last_login_at=row["LastLoginAt"],
            is_active=row["IsActive"],
            email_verified=row["EmailVerified"],
            two_factor_enabled=row["TwoFactorEnabled"]
        )
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Buscar usuário por email"""
        query = """
        SELECT UserId, Email, PasswordHash, FullName, Phone, AvatarUrl,
               SubscriptionType, CreatedAt, UpdatedAt, LastLoginAt,
               IsActive, EmailVerified, TwoFactorEnabled
        FROM Users 
        WHERE Email = :email AND IsActive = 1
        """
        
        result = self.execute_query(query, {"email": email})
        if not result:
            return None
        
        row = result[0]
        return User(
            user_id=UUID(row["UserId"]),
            email=row["Email"],
            password_hash=row["PasswordHash"],
            full_name=row["FullName"],
            phone=row["Phone"],
            avatar_url=row["AvatarUrl"],
            subscription_type=row["SubscriptionType"],
            created_at=row["CreatedAt"],
            updated_at=row["UpdatedAt"],
            last_login_at=row["LastLoginAt"],
            is_active=row["IsActive"],
            email_verified=row["EmailVerified"],
            two_factor_enabled=row["TwoFactorEnabled"]
        )
    
    async def update_user(self, user_id: UUID, updates: Dict[str, Any]) -> bool:
        """Atualizar usuário"""
        set_clauses = []
        params = {"user_id": str(user_id)}
        
        for key, value in updates.items():
            if key in ["full_name", "phone", "avatar_url", "subscription_type"]:
                set_clauses.append(f"{key.title().replace('_', '')} = :{key}")
                params[key] = value
        
        if not set_clauses:
            return False
        
        set_clauses.append("UpdatedAt = GETUTCDATE()")
        
        query = f"""
        UPDATE Users 
        SET {', '.join(set_clauses)}
        WHERE UserId = :user_id
        """
        
        try:
            with self.get_session() as session:
                result = session.execute(text(query), params)
                session.commit()
                return result.rowcount > 0
        except SQLAlchemyError as e:
            logger.error(f"Error updating user: {e}")
            return False
    
    async def update_last_login(self, user_id: UUID) -> bool:
        """Atualizar último login"""
        query = """
        UPDATE Users 
        SET LastLoginAt = GETUTCDATE()
        WHERE UserId = :user_id
        """
        
        try:
            with self.get_session() as session:
                result = session.execute(text(query), {"user_id": str(user_id)})
                session.commit()
                return result.rowcount > 0
        except SQLAlchemyError as e:
            logger.error(f"Error updating last login: {e}")
            return False


class ResumeRepository(SQLRepository):
    """Repositório de currículos"""
    
    async def create_resume(self, resume: Resume) -> Resume:
        """Criar novo currículo"""
        query = """
        INSERT INTO Resumes (ResumeId, UserId, Title, Version, Status, 
                           DataLakeFileId, OriginalFileName, FileSize, FileType)
        VALUES (NEWSEQUENTIALID(), :user_id, :title, :version, :status,
                :data_lake_file_id, :original_filename, :file_size, :file_type)
        """
        
        params = {
            "user_id": str(resume.user_id),
            "title": resume.title,
            "version": resume.version,
            "status": resume.status.value,
            "data_lake_file_id": str(resume.data_lake_file_id) if resume.data_lake_file_id else None,
            "original_filename": resume.original_filename,
            "file_size": resume.file_size,
            "file_type": resume.file_type
        }
        
        try:
            with self.get_session() as session:
                session.execute(text(query), params)
                session.commit()
                return resume
        except SQLAlchemyError as e:
            logger.error(f"Error creating resume: {e}")
            raise
    
    async def get_user_resumes(self, user_id: UUID, status: Optional[str] = None) -> List[Resume]:
        """Buscar currículos do usuário"""
        query = """
        SELECT ResumeId, UserId, Title, Version, Status, DataLakeFileId,
               OriginalFileName, FileSize, FileType, CreatedAt, UpdatedAt,
               LastAnalyzedAt, AnalysisCount, AverageMatchScore
        FROM Resumes 
        WHERE UserId = :user_id
        """
        
        params = {"user_id": str(user_id)}
        
        if status:
            query += " AND Status = :status"
            params["status"] = status
        
        query += " ORDER BY UpdatedAt DESC"
        
        result = self.execute_query(query, params)
        
        resumes = []
        for row in result:
            resumes.append(Resume(
                resume_id=UUID(row["ResumeId"]),
                user_id=UUID(row["UserId"]),
                title=row["Title"],
                version=row["Version"],
                status=row["Status"],
                data_lake_file_id=UUID(row["DataLakeFileId"]) if row["DataLakeFileId"] else None,
                original_filename=row["OriginalFileName"],
                file_size=row["FileSize"],
                file_type=row["FileType"],
                created_at=row["CreatedAt"],
                updated_at=row["UpdatedAt"],
                last_analyzed_at=row["LastAnalyzedAt"],
                analysis_count=row["AnalysisCount"],
                average_match_score=row["AverageMatchScore"]
            ))
        
        return resumes
    
    async def get_resume_by_id(self, resume_id: UUID) -> Optional[Resume]:
        """Buscar currículo por ID"""
        query = """
        SELECT ResumeId, UserId, Title, Version, Status, DataLakeFileId,
               OriginalFileName, FileSize, FileType, CreatedAt, UpdatedAt,
               LastAnalyzedAt, AnalysisCount, AverageMatchScore
        FROM Resumes 
        WHERE ResumeId = :resume_id
        """
        
        result = self.execute_query(query, {"resume_id": str(resume_id)})
        if not result:
            return None
        
        row = result[0]
        return Resume(
            resume_id=UUID(row["ResumeId"]),
            user_id=UUID(row["UserId"]),
            title=row["Title"],
            version=row["Version"],
            status=row["Status"],
            data_lake_file_id=UUID(row["DataLakeFileId"]) if row["DataLakeFileId"] else None,
            original_filename=row["OriginalFileName"],
            file_size=row["FileSize"],
            file_type=row["FileType"],
            created_at=row["CreatedAt"],
            updated_at=row["UpdatedAt"],
            last_analyzed_at=row["LastAnalyzedAt"],
            analysis_count=row["AnalysisCount"],
            average_match_score=row["AverageMatchScore"]
        )
    
    async def update_resume_analysis_stats(self, resume_id: UUID, match_score: float) -> bool:
        """Atualizar estatísticas de análise do currículo"""
        query = """
        UPDATE Resumes 
        SET AnalysisCount = AnalysisCount + 1,
            AverageMatchScore = (AverageMatchScore * AnalysisCount + :match_score) / (AnalysisCount + 1),
            LastAnalyzedAt = GETUTCDATE(),
            UpdatedAt = GETUTCDATE()
        WHERE ResumeId = :resume_id
        """
        
        try:
            with self.get_session() as session:
                result = session.execute(text(query), {
                    "resume_id": str(resume_id),
                    "match_score": match_score
                })
                session.commit()
                return result.rowcount > 0
        except SQLAlchemyError as e:
            logger.error(f"Error updating resume stats: {e}")
            return False


class AnalysisRepository(SQLRepository):
    """Repositório de análises"""
    
    async def create_analysis(self, analysis: CompatibilityAnalysis) -> CompatibilityAnalysis:
        """Criar nova análise"""
        query = """
        INSERT INTO CompatibilityAnalyses (AnalysisId, UserId, ResumeId, JobId,
                                         MatchScore, Status, AnalysisType, MongoAnalysisId)
        VALUES (NEWSEQUENTIALID(), :user_id, :resume_id, :job_id,
                :match_score, :status, :analysis_type, :mongo_analysis_id)
        """
        
        params = {
            "user_id": str(analysis.user_id),
            "resume_id": str(analysis.resume_id),
            "job_id": str(analysis.job_id) if analysis.job_id else None,
            "match_score": analysis.match_score,
            "status": analysis.status.value,
            "analysis_type": analysis.analysis_type,
            "mongo_analysis_id": analysis.mongo_analysis_id
        }
        
        try:
            with self.get_session() as session:
                session.execute(text(query), params)
                session.commit()
                return analysis
        except SQLAlchemyError as e:
            logger.error(f"Error creating analysis: {e}")
            raise
    
    async def get_user_analyses(self, user_id: UUID, limit: int = 50) -> List[CompatibilityAnalysis]:
        """Buscar análises do usuário"""
        query = """
        SELECT TOP (:limit) AnalysisId, UserId, ResumeId, JobId, MatchScore,
               Status, AnalysisType, ProcessingTimeMs, CreatedAt, CompletedAt,
               MongoAnalysisId
        FROM CompatibilityAnalyses 
        WHERE UserId = :user_id
        ORDER BY CreatedAt DESC
        """
        
        result = self.execute_query(query, {"user_id": str(user_id), "limit": limit})
        
        analyses = []
        for row in result:
            analyses.append(CompatibilityAnalysis(
                analysis_id=UUID(row["AnalysisId"]),
                user_id=UUID(row["UserId"]),
                resume_id=UUID(row["ResumeId"]),
                job_id=UUID(row["JobId"]) if row["JobId"] else None,
                match_score=row["MatchScore"],
                status=row["Status"],
                analysis_type=row["AnalysisType"],
                processing_time_ms=row["ProcessingTimeMs"],
                created_at=row["CreatedAt"],
                completed_at=row["CompletedAt"],
                mongo_analysis_id=row["MongoAnalysisId"]
            ))
        
        return analyses
    
    async def update_analysis_status(self, analysis_id: UUID, status: str, 
                                   processing_time_ms: Optional[int] = None) -> bool:
        """Atualizar status da análise"""
        query = """
        UPDATE CompatibilityAnalyses 
        SET Status = :status,
            ProcessingTimeMs = COALESCE(:processing_time_ms, ProcessingTimeMs),
            CompletedAt = CASE WHEN :status = 'completed' THEN GETUTCDATE() ELSE CompletedAt END
        WHERE AnalysisId = :analysis_id
        """
        
        try:
            with self.get_session() as session:
                result = session.execute(text(query), {
                    "analysis_id": str(analysis_id),
                    "status": status,
                    "processing_time_ms": processing_time_ms
                })
                session.commit()
                return result.rowcount > 0
        except SQLAlchemyError as e:
            logger.error(f"Error updating analysis status: {e}")
            return False


class DashboardRepository(SQLRepository):
    """Repositório para dados do dashboard"""
    
    async def get_dashboard_stats(self, user_id: UUID) -> Dict[str, Any]:
        """Obter estatísticas do dashboard"""
        query = """
        EXEC sp_GetDashboardStats @UserId = :user_id
        """
        
        result = self.execute_query(query, {"user_id": str(user_id)})
        if not result:
            return {}
        
        return result[0]
    
    async def get_recent_analyses(self, user_id: UUID, limit: int = 5) -> List[Dict[str, Any]]:
        """Obter análises recentes"""
        query = """
        SELECT TOP (:limit) ca.AnalysisId, ca.MatchScore, ca.CreatedAt,
               r.Title as ResumeTitle, jd.Title as JobTitle, c.Name as CompanyName
        FROM CompatibilityAnalyses ca
        LEFT JOIN Resumes r ON ca.ResumeId = r.ResumeId
        LEFT JOIN JobDescriptions jd ON ca.JobId = jd.JobId
        LEFT JOIN Companies c ON jd.CompanyId = c.CompanyId
        WHERE ca.UserId = :user_id AND ca.Status = 'completed'
        ORDER BY ca.CreatedAt DESC
        """
        
        return self.execute_query(query, {"user_id": str(user_id), "limit": limit})


class DataLakeRepository(SQLRepository):
    """Repositório para arquivos do Data Lake"""
    
    async def create_file_reference(self, file_ref: DataLakeFile) -> DataLakeFile:
        """Criar referência de arquivo no Data Lake"""
        query = """
        INSERT INTO DataLakeFiles (FileId, UserId, FileName, FileType, FileSize,
                                 MimeType, StoragePath, BucketName, StorageProvider, Metadata)
        VALUES (NEWSEQUENTIALID(), :user_id, :filename, :file_type, :file_size,
                :mime_type, :storage_path, :bucket_name, :storage_provider, :metadata)
        """
        
        params = {
            "user_id": str(file_ref.user_id),
            "filename": file_ref.filename,
            "file_type": file_ref.file_type,
            "file_size": file_ref.file_size,
            "mime_type": file_ref.mime_type,
            "storage_path": file_ref.storage_path,
            "bucket_name": file_ref.bucket_name,
            "storage_provider": file_ref.storage_provider,
            "metadata": str(file_ref.metadata) if file_ref.metadata else None
        }
        
        try:
            with self.get_session() as session:
                session.execute(text(query), params)
                session.commit()
                return file_ref
        except SQLAlchemyError as e:
            logger.error(f"Error creating file reference: {e}")
            raise
    
    async def record_file_access(self, file_id: UUID) -> bool:
        """Registrar acesso ao arquivo"""
        query = """
        EXEC sp_RecordDataLakeAccess @FileId = :file_id
        """
        
        try:
            with self.get_session() as session:
                session.execute(text(query), {"file_id": str(file_id)})
                session.commit()
                return True
        except SQLAlchemyError as e:
            logger.error(f"Error recording file access: {e}")
            return False
