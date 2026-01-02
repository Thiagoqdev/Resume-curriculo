# """
# Serviço de Análise
# Lógica de negócio para análises de compatibilidade
# """
# """
# Serviço de Análise
# (Temporariamente desativado para refatoração do User)
# """

# from typing import Optional, List, Dict, Any
# from uuid import UUID, uuid4
# from datetime import datetime
# import json
# import hashlib
# import logging

# from core.config import settings, ai_settings
# from models.domain import CompatibilityAnalysis, AnalysisStatus
# from dto.requests import AnalysisCreateRequest
# from dto.responses import AnalysisResponse, DetailedAnalysisResponse
# from data.sql_repository import AnalysisRepository, ResumeRepository
# from data.mongo_repository import AnalysisMongoRepository, AIAnalysisCacheRepository, ActivityLogMongoRepository
# from services.ai_service import AIService
# from services.file_service import FileService
import logging
logger = logging.getLogger(__name__)



# #class AnalysisService:
#     """Serviço de análises de compatibilidade"""
   
#     def __init__(self):
#         self.analysis_repo = AnalysisRepository()
#         self.resume_repo = ResumeRepository()
#         self.mongo_repo = AnalysisMongoRepository()
#         self.cache_repo = AIAnalysisCacheRepository()
#         self.activity_repo = ActivityLogMongoRepository()
#         self.ai_service = AIService()
#         self.file_service = FileService()
    
#     async def create_analysis(self, user_id: UUID, request: AnalysisCreateRequest) -> AnalysisResponse:
#         """Criar nova análise de compatibilidade"""
#         try:
#             # Verificar se o currículo existe e pertence ao usuário
#             resume = await self.resume_repo.get_resume_by_id(request.resume_id)
#             if not resume or resume.user_id != user_id:
#                 raise ValueError("Resume not found or access denied")
            
#             # Criar análise no SQL
#             analysis = CompatibilityAnalysis(
#                 analysis_id=uuid4(),
#                 user_id=user_id,
#                 resume_id=request.resume_id,
#                 job_id=request.job_id,
#                 match_score=0.0,  # Será atualizado após processamento
#                 status=AnalysisStatus.PENDING,
#                 analysis_type=request.analysis_type
#             )
            
#             created_analysis = await self.analysis_repo.create_analysis(analysis)
            
#             # Log da atividade
#             await self.activity_repo.log_activity({
#                 "userId": str(user_id),
#                 "action": "analysis_created",
#                 "resource": "analysis",
#                 "resourceId": str(created_analysis.analysis_id),
#                 "details": {
#                     "resume_id": str(request.resume_id),
#                     "job_id": str(request.job_id) if request.job_id else None,
#                     "analysis_type": request.analysis_type
#                 }
#             })
            
#             # Processar análise em background (simulado)
#             await self._process_analysis_async(created_analysis, request.job_description)
            
#             return AnalysisResponse(
#                 analysis_id=created_analysis.analysis_id,
#                 user_id=created_analysis.user_id,
#                 resume_id=created_analysis.resume_id,
#                 job_id=created_analysis.job_id,
#                 match_score=created_analysis.match_score,
#                 status=created_analysis.status,
#                 analysis_type=created_analysis.analysis_type,
#                 processing_time_ms=created_analysis.processing_time_ms,
#                 created_at=created_analysis.created_at,
#                 completed_at=created_analysis.completed_at
#             )
            
#         except Exception as e:
#             logger.error(f"Error creating analysis: {e}")
#             raise
    
#     async def get_analysis(self, analysis_id: UUID, user_id: UUID) -> Optional[DetailedAnalysisResponse]:
#         """Obter análise detalhada"""
#         try:
#             # Buscar análise no SQL
#             sql_result = await self.analysis_repo.execute_query(
#                 """
#                 SELECT AnalysisId, UserId, ResumeId, JobId, MatchScore, Status,
#                        AnalysisType, ProcessingTimeMs, CreatedAt, CompletedAt, MongoAnalysisId
#                 FROM CompatibilityAnalyses 
#                 WHERE AnalysisId = :analysis_id AND UserId = :user_id
#                 """,
#                 {"analysis_id": str(analysis_id), "user_id": str(user_id)}
#             )
            
#             if not sql_result:
#                 return None
            
#             analysis_data = sql_result[0]
            
#             # Buscar detalhes no MongoDB
#             detailed_analysis = None
#             if analysis_data["MongoAnalysisId"]:
#                 detailed_analysis = await self.mongo_repo.get_detailed_analysis(
#                     analysis_data["MongoAnalysisId"]
#                 )
            
#             if not detailed_analysis:
#                 # Retornar resposta básica se não houver detalhes
#                 return DetailedAnalysisResponse(
#                     analysis_id=UUID(analysis_data["AnalysisId"]),
#                     match_score=analysis_data["MatchScore"],
#                     status=analysis_data["Status"],
#                     job_analysis={},
#                     extracted_skills=[],
#                     experience_matches=[],
#                     education=[],
#                     languages=[],
#                     certifications=[],
#                     compatibility_scores={
#                         "overall_score": analysis_data["MatchScore"],
#                         "skills": 0.0,
#                         "experience": 0.0,
#                         "education": 0.0,
#                         "cultural": 0.0
#                     },
#                     strengths=[],
#                     weaknesses=[],
#                     recommendations=[],
#                     improvement_areas=[],
#                     processing_time_ms=analysis_data["ProcessingTimeMs"] or 0,
#                     ai_model="unknown",
#                     created_at=analysis_data["CreatedAt"]
#                 )
            
#             # Converter dados do MongoDB para resposta
#             return self._convert_mongo_to_response(detailed_analysis, analysis_data)
            
#         except Exception as e:
#             logger.error(f"Error getting analysis: {e}")
#             return None
    
#     async def get_user_analyses(self, user_id: UUID, limit: int = 50) -> List[AnalysisResponse]:
#         """Obter análises do usuário"""
#         try:
#             analyses = await self.analysis_repo.get_user_analyses(user_id, limit)
            
#             return [
#                 AnalysisResponse(
#                     analysis_id=analysis.analysis_id,
#                     user_id=analysis.user_id,
#                     resume_id=analysis.resume_id,
#                     job_id=analysis.job_id,
#                     match_score=analysis.match_score,
#                     status=analysis.status,
#                     analysis_type=analysis.analysis_type,
#                     processing_time_ms=analysis.processing_time_ms,
#                     created_at=analysis.created_at,
#                     completed_at=analysis.completed_at
#                 )
#                 for analysis in analyses
#             ]
            
#         except Exception as e:
#             logger.error(f"Error getting user analyses: {e}")
#             return []
    
#     async def _process_analysis_async(self, analysis: CompatibilityAnalysis, 
#                                     job_description: Optional[str] = None) -> None:
#         """Processar análise de forma assíncrona"""
#         try:
#             start_time = datetime.utcnow()
            
#             # Atualizar status para processando
#             await self.analysis_repo.update_analysis_status(
#                 analysis.analysis_id, 
#                 AnalysisStatus.PROCESSING.value
#             )
            
#             # Obter conteúdo do currículo
#             resume_content = await self._get_resume_content(analysis.resume_id)
#             if not resume_content:
#                 await self._handle_analysis_error(analysis.analysis_id, "Failed to extract resume content")
#                 return
            
#             # Obter descrição da vaga
#             job_content = await self._get_job_content(analysis.job_id, job_description)
#             if not job_content:
#                 await self._handle_analysis_error(analysis.analysis_id, "Failed to get job description")
#                 return
            
#             # Verificar cache
#             cache_key = self._generate_cache_key(resume_content, job_content)
#             cached_result = await self.cache_repo.get_cached_analysis(cache_key)
            
#             if cached_result:
#                 detailed_analysis = cached_result["result"]
#             else:
#                 # Processar com IA
#                 detailed_analysis = await self._analyze_with_ai(resume_content, job_content)
                
#                 # Armazenar em cache
#                 await self.cache_repo.cache_analysis(cache_key, detailed_analysis, ttl_hours=24)
            
#             # Salvar análise detalhada no MongoDB
#             detailed_analysis["analysisId"] = str(analysis.analysis_id)
#             detailed_analysis["userId"] = str(analysis.user_id)
#             detailed_analysis["resumeId"] = str(analysis.resume_id)
#             detailed_analysis["jobId"] = str(analysis.job_id) if analysis.job_id else None
            
#             mongo_id = await self.mongo_repo.create_detailed_analysis(detailed_analysis)
            
#             # Calcular tempo de processamento
#             processing_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            
#             # Atualizar análise no SQL
#             await self.analysis_repo.execute_query(
#                 """
#                 UPDATE CompatibilityAnalyses 
#                 SET MatchScore = :match_score,
#                     Status = 'completed',
#                     ProcessingTimeMs = :processing_time,
#                     CompletedAt = GETUTCDATE(),
#                     MongoAnalysisId = :mongo_id
#                 WHERE AnalysisId = :analysis_id
#                 """,
#                 {
#                     "analysis_id": str(analysis.analysis_id),
#                     "match_score": detailed_analysis["compatibilityReport"]["overallScore"],
#                     "processing_time": processing_time,
#                     "mongo_id": mongo_id
#                 }
#             )
            
#             # Atualizar estatísticas do currículo
#             await self.resume_repo.update_resume_analysis_stats(
#                 analysis.resume_id,
#                 detailed_analysis["compatibilityReport"]["overallScore"]
#             )
            
#             # Log da atividade
#             await self.activity_repo.log_activity({
#                 "userId": str(analysis.user_id),
#                 "action": "analysis_completed",
#                 "resource": "analysis",
#                 "resourceId": str(analysis.analysis_id),
#                 "details": {
#                     "match_score": detailed_analysis["compatibilityReport"]["overallScore"],
#                     "processing_time_ms": processing_time,
#                     "ai_model": detailed_analysis.get("aiModel", "unknown")
#                 }
#             })
            
#         except Exception as e:
#             logger.error(f"Error processing analysis: {e}")
#             await self._handle_analysis_error(analysis.analysis_id, str(e))
    
#     async def _get_resume_content(self, resume_id: UUID) -> Optional[str]:
#         """Obter conteúdo do currículo"""
#         try:
#             resume = await self.resume_repo.get_resume_by_id(resume_id)
#             if not resume or not resume.data_lake_file_id:
#                 return None
            
#             # Extrair texto do arquivo
#             content = await self.file_service.extract_text_from_file(resume.data_lake_file_id)
#             return content
            
#         except Exception as e:
#             logger.error(f"Error getting resume content: {e}")
#             return None
    
#     async def _get_job_content(self, job_id: Optional[UUID], job_description: Optional[str]) -> Optional[str]:
#         """Obter descrição da vaga"""
#         try:
#             if job_description:
#                 return job_description
            
#             if job_id:
#                 result = await self.analysis_repo.execute_query(
#                     """
#                     SELECT jd.Title, jd.Description, jd.Requirements, jd.Benefits,
#                            c.Name as CompanyName, c.Industry
#                     FROM JobDescriptions jd
#                     LEFT JOIN Companies c ON jd.CompanyId = c.CompanyId
#                     WHERE jd.JobId = :job_id
#                     """,
#                     {"job_id": str(job_id)}
#                 )
                
#                 if result:
#                     job_data = result[0]
#                     return f"""
#                     Company: {job_data['CompanyName'] or 'Not specified'}
#                     Industry: {job_data['Industry'] or 'Not specified'}
#                     Position: {job_data['Title']}
                    
#                     Description:
#                     {job_data['Description'] or 'Not provided'}
                    
#                     Requirements:
#                     {job_data['Requirements'] or 'Not provided'}
                    
#                     Benefits:
#                     {job_data['Benefits'] or 'Not provided'}
#                     """
            
#             return None
            
#         except Exception as e:
#             logger.error(f"Error getting job content: {e}")
#             return None
    
#     async def _analyze_with_ai(self, resume_content: str, job_content: str) -> Dict[str, Any]:
#         """Analisar compatibilidade usando IA"""
#         try:
#             # Análise do currículo
#             resume_analysis = await self.ai_service.analyze_resume(resume_content)
            
#             # Análise da vaga
#             job_analysis = await self.ai_service.analyze_job_description(job_content)
            
#             # Análise de compatibilidade
#             compatibility_report = await self.ai_service.analyze_compatibility(
#                 resume_analysis, job_analysis
#             )
            
#             return {
#                 "matchScore": compatibility_report["overallScore"],
#                 "jobAnalysis": job_analysis,
#                 "resumeAnalysis": resume_analysis,
#                 "compatibilityReport": compatibility_report,
#                 "processingTime": 0,  # Será calculado externamente
#                 "aiModel": settings.OPENAI_MODEL,
#                 "version": "1.0"
#             }
            
#         except Exception as e:
#             logger.error(f"Error analyzing with AI: {e}")
#             raise
    
#     def _generate_cache_key(self, resume_content: str, job_content: str) -> str:
#         """Gerar chave de cache para análise"""
#         combined_content = f"{resume_content}|{job_content}"
#         return hashlib.sha256(combined_content.encode()).hexdigest()
    
#     async def _handle_analysis_error(self, analysis_id: UUID, error_message: str) -> None:
#         """Tratar erro na análise"""
#         try:
#             await self.analysis_repo.update_analysis_status(
#                 analysis_id, 
#                 AnalysisStatus.FAILED.value
#             )
            
#             logger.error(f"Analysis {analysis_id} failed: {error_message}")
            
#         except Exception as e:
#             logger.error(f"Error handling analysis error: {e}")
    
#     def _convert_mongo_to_response(self, mongo_data: Dict[str, Any], 
#                                  sql_data: Dict[str, Any]) -> DetailedAnalysisResponse:
#         """Converter dados do MongoDB para resposta da API"""
#         try:
#             return DetailedAnalysisResponse(
#                 analysis_id=UUID(sql_data["AnalysisId"]),
#                 match_score=mongo_data.get("matchScore", 0.0),
#                 status=sql_data["Status"],
#                 job_analysis=mongo_data.get("jobAnalysis", {}),
#                 extracted_skills=mongo_data.get("resumeAnalysis", {}).get("extractedSkills", []),
#                 experience_matches=mongo_data.get("resumeAnalysis", {}).get("experience", []),
#                 education=mongo_data.get("resumeAnalysis", {}).get("education", []),
#                 languages=mongo_data.get("resumeAnalysis", {}).get("languages", []),
#                 certifications=mongo_data.get("resumeAnalysis", {}).get("certifications", []),
#                 compatibility_scores=mongo_data.get("compatibilityReport", {}).get("categoryScores", {}),
#                 strengths=mongo_data.get("compatibilityReport", {}).get("strengths", []),
#                 weaknesses=mongo_data.get("compatibilityReport", {}).get("weaknesses", []),
#                 recommendations=mongo_data.get("compatibilityReport", {}).get("recommendations", []),
#                 improvement_areas=mongo_data.get("compatibilityReport", {}).get("improvementAreas", []),
#                 processing_time_ms=sql_data["ProcessingTimeMs"] or 0,
#                 ai_model=mongo_data.get("aiModel", "unknown"),
#                 created_at=sql_data["CreatedAt"]
#             )
            
#         except Exception as e:
#             logger.error(f"Error converting mongo data to response: {e}")
#             raise
    
#     async def get_analysis_statistics(self, user_id: UUID) -> Dict[str, Any]:
#         """Obter estatísticas de análises do usuário"""
#         try:
#             # Estatísticas do SQL
#             sql_stats = await self.analysis_repo.execute_query(
#                 """
#                 SELECT 
#                     COUNT(*) as total_analyses,
#                     COUNT(CASE WHEN Status = 'completed' THEN 1 END) as completed_analyses,
#                     COUNT(CASE WHEN Status = 'pending' THEN 1 END) as pending_analyses,
#                     COUNT(CASE WHEN Status = 'failed' THEN 1 END) as failed_analyses,
#                     AVG(CASE WHEN Status = 'completed' THEN MatchScore END) as average_score,
#                     MAX(CASE WHEN Status = 'completed' THEN MatchScore END) as best_score,
#                     AVG(CASE WHEN Status = 'completed' THEN ProcessingTimeMs END) as avg_processing_time
#                 FROM CompatibilityAnalyses 
#                 WHERE UserId = :user_id
#                 """,
#                 {"user_id": str(user_id)}
#             )
            
#             # Estatísticas do MongoDB
#             mongo_stats = await self.mongo_repo.get_analysis_statistics(str(user_id))
            
#             return {
#                 "sql_stats": sql_stats[0] if sql_stats else {},
#                 "mongo_stats": mongo_stats,
#                 "generated_at": datetime.utcnow()
#             }
            
#         except Exception as e:
#             logger.error(f"Error getting analysis statistics: {e}")
#             return {}
# AGORA, ADICIONE A CLASSE "STUB" VAZIA AQUI EMBAIXO
# (Isto é o que o 'user_service' vai importar sem quebrar)
class AnalysisService:
    """Serviço de análises (STUB - Aguardando refatoração)"""
    
    def __init__(self):
        logger.warning("AnalysisService (stub) foi inicializado. Implementação real está pendente.")
        pass


class AnalysisMongoRepository:
    pass

class AIAnalysisCacheRepository:
    pass