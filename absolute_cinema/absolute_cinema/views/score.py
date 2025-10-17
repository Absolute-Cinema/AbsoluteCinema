import os
from fastapi import APIRouter, HTTPException, status
from absolute_cinema.models.movie import Movie
from absolute_cinema.models.score import Score
from absolute_cinema.controllers.movie import MovieController
from absolute_cinema.services.youtube import (
    VideoNotFoundError,
    CommentsDisabledError,
    QuotaExceededError,
    YouTubeAPIError
)

router = APIRouter(
    tags=["movies"],
    responses={
        404: {"description": "Vídeo não encontrado"},
        403: {"description": "Comentários desativados"},
        429: {"description": "Quota da API excedida"},
        500: {"description": "Erro interno do servidor"},
        503: {"description": "Serviço indisponível"}
    }
)


@router.post(
    "/score",
    response_model=Score,
    status_code=status.HTTP_200_OK,
    summary="Calcular score do filme",
    description="Calcula o score de um filme baseado em análise de sentimentos"
)
async def calculate_score(movie: Movie) -> Score:
    """Endpoint para calcular o score de um filme"""
    
    YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
    if not YOUTUBE_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "error": "API não configurada",
                "message": "YouTube API não está configurada",
                "solution": "Configure YOUTUBE_API_KEY no arquivo .env"
            }
        )
    
    try:
        print(f"\n🎬 Processando filme: {movie.name}")
        
        controller = MovieController()
        result = controller.calculate_score(movie)
        
        # Debug: imprime o resultado antes de converter
        print(f"📋 DEBUG - Tipo do resultado: {type(result)}")
        print(f"📋 DEBUG - Keys do resultado: {result.keys() if isinstance(result, dict) else 'não é dict'}")
        
        # Converte dict para Score
        score_response = Score(**result)
        
        print(f"✓ Score calculado: {score_response.score}/100\n")
        return score_response
        
    except VideoNotFoundError as e:
        print(f"✗ Vídeo não encontrado: {movie.name}\n")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "Vídeo não encontrado",
                "message": str(e),
                "movie": movie.name,
                "suggestion": "Verifique o nome do filme ou tente em inglês"
            }
        )
    
    except CommentsDisabledError as e:
        print(f"✗ Comentários desativados: {movie.name}\n")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": "Comentários desativados",
                "message": str(e),
                "movie": movie.name,
                "suggestion": "Este vídeo não permite comentários"
            }
        )
    
    except QuotaExceededError as e:
        print(f"✗ Quota excedida\n")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "error": "Quota excedida",
                "message": str(e),
                "suggestion": "Quota diária excedida. Tente amanhã"
            }
        )
    
    except YouTubeAPIError as e:
        print(f"✗ Erro da API: {str(e)}\n")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Erro na API do YouTube",
                "message": str(e),
                "suggestion": "Tente novamente em alguns instantes"
            }
        )
    
    except ValueError as e:
        print(f"✗ Erro de validação: {str(e)}\n")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "error": "Dados inválidos",
                "message": str(e),
                "suggestion": "Verifique os dados enviados"
            }
        )
    
    except Exception as e:
        print(f"✗ Erro inesperado: {str(e)}\n")
        import traceback
        traceback.print_exc()
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Erro interno",
                "message": f"Erro inesperado: {str(e)}",
                "movie": movie.name,
                "type": type(e)._name_
            }
        )


@router.get("/health")
async def health_check() -> dict:
    """Health check endpoint"""
    YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
    
    return {
        "status": "healthy",
        "youtube_api_configured": bool(YOUTUBE_API_KEY),
        "service": "Absolute Cinema API",
        "version": "1.0.0"
    }


@router.get("/score/{movie_name}", response_model=Score)
async def calculate_score_get(movie_name: str) -> Score:
    """Endpoint GET alternativo para calcular score"""
    movie = Movie(name=movie_name)
    return await calculate_score(movie)