import os
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv


# Exceções customizadas
class YouTubeAPIError(Exception):
    """Exceção base para erros da API do YouTube"""
    pass


class VideoNotFoundError(YouTubeAPIError):
    """Erro quando nenhum vídeo é encontrado"""
    pass


class CommentsDisabledError(YouTubeAPIError):
    """Erro quando comentários estão desativados"""
    pass


class QuotaExceededError(YouTubeAPIError):
    """Erro quando a quota da API é excedida"""
    pass


# Carrega variáveis de ambiente
load_dotenv()
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")


def search_video(movie_name: str, language: str = "en") -> dict:
    """
    Busca vídeo trailer do filme no YouTube
    
    Args:
        movie_name: Nome do filme
        language: Código do idioma para relevância (padrão: "en")
        
    Returns:
        dict: Informações do vídeo (video_id, title, channel, description)
        
    Raises:
        VideoNotFoundError: Se nenhum vídeo for encontrado
        QuotaExceededError: Se a quota da API for excedida
        YouTubeAPIError: Para outros erros da API
    """
    if not YOUTUBE_API_KEY:
        raise YouTubeAPIError("YOUTUBE_API_KEY não configurada nas variáveis de ambiente")
    
    try:
        youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)
        query = f"{movie_name} trailer oficial"
        
        print(f"🔍 Buscando: {query}")
        
        request = youtube.search().list(
            part="snippet",
            q=query,
            type="video",
            maxResults=1,
            relevanceLanguage=language,
            order="relevance"
        )
        response = request.execute()
        
        items = response.get('items', [])
        
        if not items:
            raise VideoNotFoundError(f"Nenhum vídeo encontrado para '{movie_name}'")
        
        video = items[0]
        video_id = video['id']['videoId']
        video_title = video['snippet']['title']
        
        print(f"✓ Vídeo encontrado: {video_title}")
        print(f"  ID: {video_id}")
        
        return {
            'video_id': video_id,
            'title': video_title,
            'channel': video['snippet']['channelTitle'],
            'description': video['snippet']['description']
        }
        
    except HttpError as e:
        if e.resp.status == 403:
            error_message = "Quota da API do YouTube excedida"
            print(f"✗ {error_message}")
            raise QuotaExceededError(error_message) from e
        elif e.resp.status == 400:
            error_message = f"Busca inválida para '{movie_name}'"
            print(f"✗ {error_message}")
            raise ValueError(error_message) from e
        else:
            error_message = f"Erro de comunicação com a API: {e.resp.status}"
            print(f"✗ {error_message}")
            raise YouTubeAPIError(error_message) from e
    except VideoNotFoundError:
        raise
    except Exception as e:
        error_message = f"Erro inesperado ao buscar vídeo: {e}"
        print(f"✗ {error_message}")
        raise YouTubeAPIError(error_message) from e


def get_comments(video_id: str, max_results: int = 150) -> list:
    """
    Obtém comentários do vídeo do YouTube
    
    Args:
        video_id: ID do vídeo
        max_results: Número máximo de comentários (padrão: 150)
        
    Returns:
        list: Lista de dicionários com comentários (author, text, likes, published_at)
        
    Raises:
        CommentsDisabledError: Se comentários estiverem desativados
        QuotaExceededError: Se a quota da API for excedida
        VideoNotFoundError: Se o vídeo não existir
        YouTubeAPIError: Para outros erros da API
    """
    if not YOUTUBE_API_KEY:
        raise YouTubeAPIError("YOUTUBE_API_KEY não configurada nas variáveis de ambiente")
    
    comments = []
    next_page_token = None
    
    try:
        youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)
        
        print(f"💬 Coletando comentários do vídeo {video_id}...")
        
        while len(comments) < max_results:
            request = youtube.commentThreads().list(
                part="snippet",
                videoId=video_id,
                maxResults=min(100, max_results - len(comments)),
                textFormat="plainText",
                pageToken=next_page_token,
                order="relevance"
            )
            response = request.execute()
            
            for item in response.get('items', []):
                try:
                    snippet = item['snippet']['topLevelComment']['snippet']
                    text = snippet['textDisplay'].strip()
                    
                    # Filtra comentários muito curtos
                    if len(text) > 5:
                        comments.append({
                            'author': snippet['authorDisplayName'],
                            'text': text,
                            'likes': snippet.get('likeCount', 0),
                            'published_at': snippet['publishedAt']
                        })
                except KeyError:
                    # Ignora comentários mal formatados
                    continue
            
            next_page_token = response.get('nextPageToken')
            
            # Imprime progresso
            print(f"  ↳ {len(comments)} comentários coletados até agora...")
            
            if not next_page_token:
                break
        
        print(f"✓ Total de {len(comments)} comentários coletados")
        return comments
        
    except HttpError as e:
        error_content = str(e.content) if hasattr(e, 'content') else str(e)
        
        if "commentsDisabled" in error_content:
            error_message = "Comentários estão desativados para este vídeo"
            print(f"✗ {error_message}")
            raise CommentsDisabledError(error_message) from e
        elif e.resp.status == 403:
            error_message = "Quota da API do YouTube excedida"
            print(f"✗ {error_message}")
            raise QuotaExceededError(error_message) from e
        elif e.resp.status == 404 or e.resp.status == 400:
            error_message = f"Vídeo {video_id} não encontrado"
            print(f"✗ {error_message}")
            raise VideoNotFoundError(error_message) from e
        else:
            error_message = f"Erro ao buscar comentários: {e.resp.status}"
            print(f"✗ {error_message}")
            raise YouTubeAPIError(error_message) from e
    except Exception as e:
        error_message = f"Erro inesperado ao coletar comentários: {e}"
        print(f"✗ {error_message}")
        raise YouTubeAPIError(error_message) from e


# Exemplo de uso
if __name__ == "__main__":
    try:
        # Buscar vídeo
        movie = "Inception"
        video_info = search_video(movie)
        print(f"\n📹 Vídeo: {video_info['title']}")
        print(f"📺 Canal: {video_info['channel']}")
        
        # Obter comentários
        comments = get_comments(video_info['video_id'], max_results=50)
        
        print(f"\n💭 Primeiros 5 comentários:")
        for i, comment in enumerate(comments[:5], 1):
            print(f"\n{i}. {comment['author']} (👍 {comment['likes']})")
            print(f"   {comment['text'][:100]}...")
            
    except VideoNotFoundError as e:
        print(f"❌ Vídeo não encontrado: {e}")
    except CommentsDisabledError as e:
        print(f"❌ Comentários desativados: {e}")
    except QuotaExceededError as e:
        print(f"❌ Quota excedida: {e}")
    except YouTubeAPIError as e:
        print(f"❌ Erro na API: {e}")
        