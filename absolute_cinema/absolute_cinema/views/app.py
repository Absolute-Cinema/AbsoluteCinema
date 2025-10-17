import os
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from absolute_cinema.views.score import router as score_router

# Cria a aplicação FastAPI
app = FastAPI(
    title="Absolute Cinema API",
    description="API para análise de sentimentos de filmes baseada em comentários do YouTube",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configuração CORS (permite requisições de outros domínios)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especifique os domínios permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclui as rotas de score
app.include_router(score_router)


# Exception handler global (deve estar no app, não no router)
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Handler global para exceções não tratadas
    
    Captura qualquer exceção que não foi tratada especificamente
    e retorna uma resposta JSON padronizada
    """
    print(f"❌ Exceção não tratada: {type(exc).__name__}: {str(exc)}")
    print(f"   Path: {request.url.path}")
    print(f"   Method: {request.method}")
    
    # Em modo debug, mostra detalhes do erro
    debug_mode = os.getenv("DEBUG", "False").lower() == "true"
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Erro interno do servidor",
            "message": "Ocorreu um erro inesperado ao processar sua requisição",
            "detail": str(exc) if debug_mode else None,
            "path": str(request.url.path)
        }
    )


# Endpoint raiz
@app.get("/", tags=["root"])
async def root():
    """
    Endpoint raiz da API
    
    Returns:
        dict: Informações sobre a API
    """
    return {
        "service": "Absolute Cinema API",
        "version": "1.0.0",
        "status": "online",
        "docs": "/docs",
        "health": "/health"  # ← CORRIGIDO: era /api/v1/health, agora é /health
    }


# Startup event
@app.on_event("startup")
async def startup_event():
    """
    Executado quando a aplicação inicia
    """
    print("\n" + "="*50)
    print("🎬 Absolute Cinema API")
    print("="*50)
    print(f"✓ Servidor iniciado")
    print(f"✓ Documentação disponível em: /docs")
    
    # Verifica configurações
    youtube_api = os.getenv("YOUTUBE_API_KEY")
    if youtube_api:
        print(f"✓ YouTube API configurada")
    else:
        print(f"⚠️  YouTube API NÃO configurada!")
        print(f"   Configure YOUTUBE_API_KEY no arquivo .env")
    
    print("="*50 + "\n")


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """
    Executado quando a aplicação é encerrada
    """
    print("\n🛑 Servidor encerrado\n")


if __name__ == "__main__":
    import uvicorn
    
    # Configurações do servidor
    uvicorn.run(
        "absolute_cinema.views.app:app",  # ← CORRIGIDO: caminho completo do módulo
        host="0.0.0.0",
        port=8000,
        reload=True,  # Auto-reload em desenvolvimento
        log_level="info"
    )