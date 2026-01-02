"""
Repositório MongoDB
Camada de acesso a dados para MongoDB
"""
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase, AsyncIOMotorCollection
from pymongo.errors import PyMongoError
import logging

from core.config import settings
from domain.entities.domain import (
    DetailedAnalysis, CoverLetterDocument, UserPreferences
)

logger = logging.getLogger(__name__)


class MongoRepository:
    """Repositório base para MongoDB"""
    
    def __init__(self):
        self.client: AsyncIOMotorClient = None
        self.database: AsyncIOMotorDatabase = None
    
    async def connect(self):
        """Conectar ao MongoDB"""
        try:
            self.client = AsyncIOMotorClient(settings.MONGO_URL)
            self.database = self.client[settings.MONGO_DATABASE]
            
            # Testar conexão
            await self.client.admin.command('ping')
            logger.info("Connected to MongoDB successfully")
            
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
    
    async def disconnect(self):
        """Desconectar do MongoDB"""
        if self.client:
            self.client.close()
            logger.info("Disconnected from MongoDB")
    
    def get_collection(self, collection_name: str) -> AsyncIOMotorCollection:
        """Obter coleção do MongoDB"""
        return self.database[collection_name]


class AnalysisMongoRepository(MongoRepository):
    """Repositório MongoDB para análises detalhadas"""
    
    def __init__(self):
        super().__init__()
        self.collection_name = "compatibility_analyses"
    
    async def create_detailed_analysis(self, analysis: Dict[str, Any]) -> str:
        """Criar análise detalhada"""
        try:
            collection = self.get_collection(self.collection_name)
            
            # Adicionar timestamps
            analysis["createdAt"] = datetime.utcnow()
            analysis["updatedAt"] = datetime.utcnow()
            
            result = await collection.insert_one(analysis)
            return str(result.inserted_id)
            
        except PyMongoError as e:
            logger.error(f"Error creating detailed analysis: {e}")
            raise
    
    async def get_detailed_analysis(self, analysis_id: str) -> Optional[Dict[str, Any]]:
        """Buscar análise detalhada por ID"""
        try:
            collection = self.get_collection(self.collection_name)
            
            result = await collection.find_one({"analysisId": analysis_id})
            return result
            
        except PyMongoError as e:
            logger.error(f"Error getting detailed analysis: {e}")
            return None
    
    async def get_user_analyses(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Buscar análises do usuário"""
        try:
            collection = self.get_collection(self.collection_name)
            
            cursor = collection.find(
                {"userId": user_id}
            ).sort("createdAt", -1).limit(limit)
            
            return await cursor.to_list(length=limit)
            
        except PyMongoError as e:
            logger.error(f"Error getting user analyses: {e}")
            return []
    
    async def update_analysis(self, analysis_id: str, updates: Dict[str, Any]) -> bool:
        """Atualizar análise"""
        try:
            collection = self.get_collection(self.collection_name)
            
            updates["updatedAt"] = datetime.utcnow()
            
            result = await collection.update_one(
                {"analysisId": analysis_id},
                {"$set": updates}
            )
            
            return result.modified_count > 0
            
        except PyMongoError as e:
            logger.error(f"Error updating analysis: {e}")
            return False
    
    async def delete_analysis(self, analysis_id: str) -> bool:
        """Deletar análise"""
        try:
            collection = self.get_collection(self.collection_name)
            
            result = await collection.delete_one({"analysisId": analysis_id})
            return result.deleted_count > 0
            
        except PyMongoError as e:
            logger.error(f"Error deleting analysis: {e}")
            return False
    
    async def get_analysis_statistics(self, user_id: str) -> Dict[str, Any]:
        """Obter estatísticas de análises"""
        try:
            collection = self.get_collection(self.collection_name)
            
            pipeline = [
                {"$match": {"userId": user_id}},
                {"$group": {
                    "_id": None,
                    "totalAnalyses": {"$sum": 1},
                    "averageScore": {"$avg": "$matchScore"},
                    "maxScore": {"$max": "$matchScore"},
                    "minScore": {"$min": "$matchScore"},
                    "scoreDistribution": {
                        "$push": {
                            "score": "$matchScore",
                            "date": "$createdAt"
                        }
                    }
                }}
            ]
            
            result = await collection.aggregate(pipeline).to_list(length=1)
            return result[0] if result else {}
            
        except PyMongoError as e:
            logger.error(f"Error getting analysis statistics: {e}")
            return {}


class CoverLetterMongoRepository(MongoRepository):
    """Repositório MongoDB para cartas de apresentação"""
    
    def __init__(self):
        super().__init__()
        self.collection_name = "cover_letters"
    
    async def create_cover_letter(self, cover_letter: Dict[str, Any]) -> str:
        """Criar carta de apresentação"""
        try:
            collection = self.get_collection(self.collection_name)
            
            # Adicionar timestamps
            cover_letter["createdAt"] = datetime.utcnow()
            cover_letter["updatedAt"] = datetime.utcnow()
            
            result = await collection.insert_one(cover_letter)
            return str(result.inserted_id)
            
        except PyMongoError as e:
            logger.error(f"Error creating cover letter: {e}")
            raise
    
    async def get_cover_letter(self, cover_letter_id: str) -> Optional[Dict[str, Any]]:
        """Buscar carta por ID"""
        try:
            collection = self.get_collection(self.collection_name)
            
            result = await collection.find_one({"coverLetterId": cover_letter_id})
            return result
            
        except PyMongoError as e:
            logger.error(f"Error getting cover letter: {e}")
            return None
    
    async def get_user_cover_letters(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Buscar cartas do usuário"""
        try:
            collection = self.get_collection(self.collection_name)
            
            cursor = collection.find(
                {"userId": user_id}
            ).sort("createdAt", -1).limit(limit)
            
            return await cursor.to_list(length=limit)
            
        except PyMongoError as e:
            logger.error(f"Error getting user cover letters: {e}")
            return []
    
    async def update_cover_letter(self, cover_letter_id: str, updates: Dict[str, Any]) -> bool:
        """Atualizar carta"""
        try:
            collection = self.get_collection(self.collection_name)
            
            # Adicionar ao histórico de edições
            if "content" in updates or "customizations" in updates:
                edit_entry = {
                    "version": 1,  # Incrementar baseado no histórico existente
                    "changes": "Content updated",
                    "editedBy": updates.get("editedBy", "user"),
                    "editedAt": datetime.utcnow()
                }
                
                await collection.update_one(
                    {"coverLetterId": cover_letter_id},
                    {"$push": {"editHistory": edit_entry}}
                )
            
            updates["updatedAt"] = datetime.utcnow()
            
            result = await collection.update_one(
                {"coverLetterId": cover_letter_id},
                {"$set": updates}
            )
            
            return result.modified_count > 0
            
        except PyMongoError as e:
            logger.error(f"Error updating cover letter: {e}")
            return False
    
    async def delete_cover_letter(self, cover_letter_id: str) -> bool:
        """Deletar carta"""
        try:
            collection = self.get_collection(self.collection_name)
            
            result = await collection.delete_one({"coverLetterId": cover_letter_id})
            return result.deleted_count > 0
            
        except PyMongoError as e:
            logger.error(f"Error deleting cover letter: {e}")
            return False


class UserPreferencesMongoRepository(MongoRepository):
    """Repositório MongoDB para preferências do usuário"""
    
    def __init__(self):
        super().__init__()
        self.collection_name = "user_preferences"
    
    async def create_user_preferences(self, preferences: Dict[str, Any]) -> str:
        """Criar preferências do usuário"""
        try:
            collection = self.get_collection(self.collection_name)
            
            # Adicionar timestamps
            preferences["createdAt"] = datetime.utcnow()
            preferences["updatedAt"] = datetime.utcnow()
            
            result = await collection.insert_one(preferences)
            return str(result.inserted_id)
            
        except PyMongoError as e:
            logger.error(f"Error creating user preferences: {e}")
            raise
    
    async def get_user_preferences(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Buscar preferências do usuário"""
        try:
            collection = self.get_collection(self.collection_name)
            
            result = await collection.find_one({"userId": user_id})
            return result
            
        except PyMongoError as e:
            logger.error(f"Error getting user preferences: {e}")
            return None
    
    async def update_user_preferences(self, user_id: str, updates: Dict[str, Any]) -> bool:
        """Atualizar preferências do usuário"""
        try:
            collection = self.get_collection(self.collection_name)
            
            updates["updatedAt"] = datetime.utcnow()
            
            result = await collection.update_one(
                {"userId": user_id},
                {"$set": updates},
                upsert=True
            )
            
            return result.modified_count > 0 or result.upserted_id is not None
            
        except PyMongoError as e:
            logger.error(f"Error updating user preferences: {e}")
            return False


class ActivityLogMongoRepository(MongoRepository):
    """Repositório MongoDB para logs de atividade"""
    
    def __init__(self):
        super().__init__()
        self.collection_name = "activity_logs"
    
    async def log_activity(self, activity: Dict[str, Any]) -> str:
        """Registrar atividade"""
        try:
            collection = self.get_collection(self.collection_name)
            
            activity["timestamp"] = datetime.utcnow()
            
            result = await collection.insert_one(activity)
            return str(result.inserted_id)
            
        except PyMongoError as e:
            logger.error(f"Error logging activity: {e}")
            raise
    
    async def get_user_activities(self, user_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Buscar atividades do usuário"""
        try:
            collection = self.get_collection(self.collection_name)
            
            cursor = collection.find(
                {"userId": user_id}
            ).sort("timestamp", -1).limit(limit)
            
            return await cursor.to_list(length=limit)
            
        except PyMongoError as e:
            logger.error(f"Error getting user activities: {e}")
            return []
    
    async def get_activity_statistics(self, user_id: str, days: int = 30) -> Dict[str, Any]:
        """Obter estatísticas de atividade"""
        try:
            collection = self.get_collection(self.collection_name)
            
            start_date = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            start_date = start_date.replace(day=start_date.day - days)
            
            pipeline = [
                {"$match": {
                    "userId": user_id,
                    "timestamp": {"$gte": start_date}
                }},
                {"$group": {
                    "_id": {
                        "action": "$action",
                        "date": {"$dateToString": {"format": "%Y-%m-%d", "date": "$timestamp"}}
                    },
                    "count": {"$sum": 1}
                }},
                {"$group": {
                    "_id": "$_id.action",
                    "totalCount": {"$sum": "$count"},
                    "dailyActivity": {
                        "$push": {
                            "date": "$_id.date",
                            "count": "$count"
                        }
                    }
                }}
            ]
            
            result = await collection.aggregate(pipeline).to_list(length=None)
            return {item["_id"]: item for item in result}
            
        except PyMongoError as e:
            logger.error(f"Error getting activity statistics: {e}")
            return {}


class AIAnalysisCacheRepository(MongoRepository):
    """Repositório MongoDB para cache de análises de IA"""
    
    def __init__(self):
        super().__init__()
        self.collection_name = "ai_analysis_cache"
    
    async def get_cached_analysis(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Buscar análise em cache"""
        try:
            collection = self.get_collection(self.collection_name)
            
            # Verificar se não expirou
            result = await collection.find_one({
                "cacheKey": cache_key,
                "expiresAt": {"$gt": datetime.utcnow()}
            })
            
            if result:
                # Atualizar contador de hits e último uso
                await collection.update_one(
                    {"_id": result["_id"]},
                    {
                        "$inc": {"hitCount": 1},
                        "$set": {"lastUsedAt": datetime.utcnow()}
                    }
                )
            
            return result
            
        except PyMongoError as e:
            logger.error(f"Error getting cached analysis: {e}")
            return None
    
    async def cache_analysis(self, cache_key: str, result: Dict[str, Any], 
                           ttl_hours: int = 24) -> str:
        """Armazenar análise em cache"""
        try:
            collection = self.get_collection(self.collection_name)
            
            expires_at = datetime.utcnow().replace(
                hour=datetime.utcnow().hour + ttl_hours
            )
            
            cache_entry = {
                "cacheKey": cache_key,
                "result": result,
                "createdAt": datetime.utcnow(),
                "lastUsedAt": datetime.utcnow(),
                "expiresAt": expires_at,
                "hitCount": 0
            }
            
            # Upsert para evitar duplicatas
            await collection.update_one(
                {"cacheKey": cache_key},
                {"$set": cache_entry},
                upsert=True
            )
            
            return cache_key
            
        except PyMongoError as e:
            logger.error(f"Error caching analysis: {e}")
            raise
    
    async def cleanup_expired_cache(self) -> int:
        """Limpar cache expirado"""
        try:
            collection = self.get_collection(self.collection_name)
            
            result = await collection.delete_many({
                "expiresAt": {"$lt": datetime.utcnow()}
            })
            
            return result.deleted_count
            
        except PyMongoError as e:
            logger.error(f"Error cleaning up cache: {e}")
            return 0


class FeedbackMongoRepository(MongoRepository):
    """Repositório MongoDB para feedback dos usuários"""
    
    def __init__(self):
        super().__init__()
        self.collection_name = "user_feedback"
    
    async def create_feedback(self, feedback: Dict[str, Any]) -> str:
        """Criar feedback"""
        try:
            collection = self.get_collection(self.collection_name)
            
            feedback["createdAt"] = datetime.utcnow()
            feedback["updatedAt"] = datetime.utcnow()
            feedback["status"] = "new"
            
            result = await collection.insert_one(feedback)
            return str(result.inserted_id)
            
        except PyMongoError as e:
            logger.error(f"Error creating feedback: {e}")
            raise
    
    async def get_user_feedback(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Buscar feedback do usuário"""
        try:
            collection = self.get_collection(self.collection_name)
            
            cursor = collection.find(
                {"userId": user_id}
            ).sort("createdAt", -1).limit(limit)
            
            return await cursor.to_list(length=limit)
            
        except PyMongoError as e:
            logger.error(f"Error getting user feedback: {e}")
            return []
    
    async def update_feedback_status(self, feedback_id: str, status: str, 
                                   resolution: Optional[str] = None) -> bool:
        """Atualizar status do feedback"""
        try:
            collection = self.get_collection(self.collection_name)
            
            updates = {
                "status": status,
                "updatedAt": datetime.utcnow()
            }
            
            if resolution:
                updates["resolution"] = resolution
            
            if status == "resolved":
                updates["resolvedAt"] = datetime.utcnow()
            
            result = await collection.update_one(
                {"_id": feedback_id},
                {"$set": updates}
            )
            
            return result.modified_count > 0
            
        except PyMongoError as e:
            logger.error(f"Error updating feedback status: {e}")
            return False
