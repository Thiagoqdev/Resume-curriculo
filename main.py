"""
Aplicação Principal (Correção de Lifespan)
"""
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
import time
from datetime import datetime
from fastapi.encoders import jsonable_encoder 

# Importa o router que refatorámos
from api import auth as auth_router
from api import resumes as resumes_router

from core.config import settings
# REMOVIDO: from data.database import initialize_database_data 
from schemas.responses.responses import ErrorResponse, HealthCheckResponse

# Configurar logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format=settings.LOG_FORMAT
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerenciar ciclo de vida da aplicação (SIMPLIFICADO)"""
    # Startup
    logger.info("Starting SkillSync API...")
    
    try:
        # REMOVIDO: await initialize_database_data()
        # REMOVIDO: logger.info("Dados de referência do BD verificados com sucesso.")
        
        logger.info("SkillSync API started successfully")
        
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down SkillSync API...")
    
    try:
        # (Lógica de Shutdown, se houver)
        logger.info("SkillSync API shut down successfully")
        
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")


# Criar aplicação FastAPI
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="API para análise de currículos e compatibilidade com vagas",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan # <-- Garante que o lifespan é chamado
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
    
    logger.info(f"Request: {request.method} {request.url}")
    
    try:
        response = await call_next(request)
        
        process_time = time.time() - start_time
        
        logger.info(
            f"Response: {response.status_code} - "
            f"Time: {process_time:.3f}s - "
            f"Path: {request.url.path}"
        )
        
        response.headers["X-Process-Time"] = str(process_time)
        
        return response
        
    except Exception as e:
        process_time = time.time() - start_time
        logger.error(f"Request failed: {request.method} {request.url} - Error: {e} - Time: {process_time:.3f}s", exc_info=True)
        # Re-lança a exceção para os handlers do FastAPI
        raise


# Handler global de exceções
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handler para exceções HTTP"""
    error_content = ErrorResponse(
        success=False,
        message=exc.detail,
        error_code=f"HTTP_{exc.status_code}",
        # timestamp não precisa mais ser passado aqui, o default_factory cuida
        details={
            "path": str(request.url),
            "method": request.method
        }
    )
    return JSONResponse(
        status_code=exc.status_code,
        content=error_content.model_dump() # Use .model_dump() diretamente
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handler para exceções gerais"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)

    error_content = ErrorResponse(
        success=False,
        message="Internal server error",
        error_code="INTERNAL_ERROR",
        # timestamp não precisa mais ser passado aqui, o default_factory cuida
        details={
            "path": str(request.url),
            "method": request.method,
            "error_type": str(type(exc).__name__)
        } if settings.DEBUG else None
    )
    return JSONResponse(
        status_code=500,
        content=error_content.model_dump() # Use .model_dump() diretamente
    )


# Incluir routers (Apenas a versão com prefixo)
app.include_router(auth_router.router, prefix=settings.API_V1_STR)

# (Aqui você adicionará os outros routers: resumes, analysis, etc.)

app.include_router(resumes_router.router, prefix=settings.API_V1_STR)

# Endpoints básicos
@app.get("/")
async def root():
    """Endpoint raiz"""
    return {
        "message": "SkillSync API",
        "version": settings.APP_VERSION,
        "status": "running",
        "timestamp": datetime.utcnow()
    }


@app.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """Health check da aplicação"""
    # (A sua lógica de health check existente...)
    return HealthCheckResponse(
        status="healthy",
        version=settings.APP_VERSION,
        uptime_seconds=0,
        database={"status": "checking", "response_time_ms": 0},
        mongodb={"status": "disabled", "response_time_ms": 0},
        blob_storage={"status": "disabled", "response_time_ms": 0},
        redis={"status": "disabled", "response_time_ms": 0},
        ai_services={"status": "disabled", "response_time_ms": 0}
    )


@app.get("/metrics")
async def get_metrics():
    """Métricas básicas da aplicação"""
    return {"requests_total": 0}


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )