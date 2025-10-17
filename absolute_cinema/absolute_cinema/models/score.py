from pydantic import BaseModel, Field
from typing import List, Optional

class CommentSample(BaseModel):
    """Modelo para comentário de exemplo"""
    author: str
    text: str
    likes: int
    sentiment: str

class ScoreDetails(BaseModel):
    """Detalhes da análise de sentimentos"""
    total_comments: int
    positive_percentage: float
    negative_percentage: float
    neutral_percentage: float
    average_polarity: float

class Score(BaseModel):
    """Modelo de resposta completo para análise de filme"""
    score: float = Field(..., description="Score final do filme (0-100)")
    movie_name: str = Field(..., description="Nome do filme analisado")
    video_id: str = Field(..., description="ID do vídeo no YouTube")
    video_title: str = Field(..., description="Título do vídeo")
    status: str = Field(default="success", description="Status da operação")
    message: str = Field(..., description="Mensagem de status")
    details: ScoreDetails = Field(..., description="Detalhes da análise")
    sample_comments: List[CommentSample] = Field(default_factory=list, description="Comentários de exemplo")