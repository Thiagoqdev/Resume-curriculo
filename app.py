"""
Aplicação Principal SkillSync API
Seguindo Arquitetura IT Valley
"""
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
import time
from datetime import datetime

from core.config import settings
from api import auth
from schemas.responses import ErrorResponse, HealthCheckResponse

# Configurar logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format=settings.LOG_FORMAT
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerenciar ciclo de vida da aplicação"""
    # Startup
    logger.info("Starting SkillSync API...")
    
    try:
        # Conectar ao MongoDB (comentado por enquanto)
        # await mongo_repo.connect()
        # logger.info("Connected to MongoDB")
        
        # Outras inicializações aqui
        logger.info("SkillSync API started successfully")
        
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down SkillSync API...")
    
    try:
        # Desconectar do MongoDB (comentado por enquanto)
        # await mongo_repo.disconnect()
        # logger.info("Disconnected from MongoDB")
        
        logger.info("SkillSync API shut down successfully")
        
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")


# Criar aplicação FastAPI
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="API para análise de currículos e compatibilidade com vagas - Arquitetura IT Valley",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan
)

# Middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware de hosts confiáveis
if not settings.DEBUG:
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["skillsync.app", "api.skillsync.app", "localhost"]
    )


# Middleware de logging de requisições
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log de todas as requisições"""
    start_time = time.time()
    
    # Log da requisição
    logger.info(f"Request: {request.method} {request.url}")
    
    try:
        response = await call_next(request)
        
        # Calcular tempo de processamento
        process_time = time.time() - start_time
        
        # Log da resposta
        logger.info(
            f"Response: {response.status_code} - "
            f"Time: {process_time:.3f}s - "
            f"Path: {request.url.path}"
        )
        
        # Adicionar header de tempo de processamento
        response.headers["X-Process-Time"] = str(process_time)
        
        return response
        
    except Exception as e:
        process_time = time.time() - start_time
        logger.error(f"Request failed: {request.method} {request.url} - Error: {e} - Time: {process_time:.3f}s")
        raise


# Handler global de exceções
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handler para exceções HTTP"""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            success=False,
            message=exc.detail,
            error_code=f"HTTP_{exc.status_code}",
            details={
                "path": str(request.url),
                "method": request.method
            }
        ).dict()
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handler para exceções gerais"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            success=False,
            message="Internal server error",
            error_code="INTERNAL_ERROR",
            details={
                "path": str(request.url),
                "method": request.method
            } if settings.DEBUG else None
        ).dict()
    )


# Incluir routers
app.include_router(auth.router, prefix=settings.API_V1_STR)


# Endpoints básicos
@app.get("/")
async def root():
    """Endpoint raiz"""
    return {
        "message": "SkillSync API - Arquitetura IT Valley",
        "version": settings.APP_VERSION,
        "status": "running",
        "architecture": "IT Valley",
        "timestamp": datetime.utcnow()
    }


@app.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """Health check da aplicação"""
    try:
        # Verificar conexões com bancos de dados
        database_status = "healthy"
        mongodb_status = "disabled"  # Comentado por enquanto
        blob_storage_status = "disabled"  # Comentado por enquanto
        redis_status = "disabled"  # Comentado por enquanto
        ai_services_status = "disabled"  # Comentado por enquanto
        
        # Em uma implementação real, você faria verificações reais
        # Por enquanto, assumimos que tudo está funcionando
        
        return HealthCheckResponse(
            status="healthy",
            version=settings.APP_VERSION,
            uptime_seconds=0,  # Calcular uptime real
            database={
                "status": database_status,
                "response_time_ms": 0
            },
            mongodb={
                "status": mongodb_status,
                "response_time_ms": 0
            },
            blob_storage={
                "status": blob_storage_status,
                "response_time_ms": 0
            },
            redis={
                "status": redis_status,
                "response_time_ms": 0
            },
            ai_services={
                "status": ai_services_status,
                "response_time_ms": 0
            }
        )
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return HealthCheckResponse(
            status="unhealthy",
            version=settings.APP_VERSION,
            uptime_seconds=0,
            database={"status": "unknown", "response_time_ms": 0},
            mongodb={"status": "unknown", "response_time_ms": 0},
            blob_storage={"status": "unknown", "response_time_ms": 0},
            redis={"status": "unknown", "response_time_ms": 0},
            ai_services={"status": "unknown", "response_time_ms": 0}
        )


@app.get("/metrics")
async def get_metrics():
    """Métricas básicas da aplicação"""
    # Em uma implementação real, você coletaria métricas reais
    return {
        "requests_total": 0,
        "requests_per_second": 0.0,
        "average_response_time_ms": 0.0,
        "error_rate_percentage": 0.0,
        "active_users": 0,
        "database_connections": 0,
        "memory_usage_mb": 0.0,
        "cpu_usage_percentage": 0.0,
        "architecture": "IT Valley"
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
