import os
from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def read_root():
    """Endpoint raiz da API"""
    YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
    
    return {
        "message": "Absolute Cinema API - Análise de Sentimentos Real",
        "version": "2.1.0",
        "status": "online",
        "youtube_api": "conectada" if YOUTUBE_API_KEY else "desconectada"
    }

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
    
    return {
        "status": "healthy",
        "youtube_configured": bool(YOUTUBE_API_KEY)
    }