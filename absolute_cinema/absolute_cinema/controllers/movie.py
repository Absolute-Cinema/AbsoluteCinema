from absolute_cinema.models.movie import Movie
from absolute_cinema.models.score import Score
from absolute_cinema.services.youtube import search_video, get_comments
from absolute_cinema.internals.sentimeter import get_sentiment, calculate_score_from_comments

class MovieController:
    """Controller para gerenciar análise de filmes"""
    
    def calculate_score(self, movie: Movie) -> dict:
        """
        Calcula o score de um filme baseado em comentários do YouTube
        
        Args:
            movie: Objeto Movie com o nome do filme
            
        Returns:
            dict: Resultado da análise com score e detalhes
        """
        if not movie.name or movie.name.strip() == "":
            raise ValueError("Nome do filme não pode estar vazio")
        
        print(f"\n🔍 Analisando: {movie.name}")
        
        # 1. Buscar vídeo no YouTube
        print("📹 Buscando trailer no YouTube...")
        video_info = search_video(movie.name)
        
        if not video_info:
            raise ValueError(f"Nenhum trailer encontrado para '{movie.name}'")
        
        video_id = video_info['video_id']
        video_title = video_info['title']
        
        # 2. Coletar comentários
        print("💬 Coletando comentários...")
        comments = get_comments(video_id, max_results=150)
        
        if not comments:
            raise ValueError("Nenhum comentário encontrado para este vídeo")
        
        # 3. Analisar sentimentos
        print("📊 Analisando sentimentos...")
        analysis = calculate_score_from_comments(comments)
        
        # 4. Selecionar comentários de exemplo
        print("📝 Selecionando comentários de exemplo...")
        sample_comments = self._select_sample_comments(comments)
        
        print(f"✓ {len(sample_comments)} comentários de exemplo selecionados")
        print(f"✓ Análise concluída!")
        print(f"  Score: {analysis['score']}/100")
        print(f"  Positivos: {analysis['positive']}%")
        print(f"  Negativos: {analysis['negative']}%")
        print(f"  Video ID: {video_id}\n")
        
        # 5. Montar resposta
        return {
            "score": analysis['score'],
            "movie_name": movie.name,
            "video_id": video_id,
            "video_title": video_title,
            "status": "success",
            "message": f"Análise concluída para '{movie.name}'",
            "details": {
                "total_comments": analysis['total_comments'],
                "positive_percentage": analysis['positive'],
                "negative_percentage": analysis['negative'],
                "neutral_percentage": analysis['neutral'],
                "average_polarity": analysis['avg_polarity']
            },
            "sample_comments": sample_comments
        }
    
    def _select_sample_comments(self, comments: list) -> list:
        """Seleciona comentários de exemplo para exibição"""
        analyzed_comments = []
        
        # Analisar todos os comentários
        for comment in comments:
            sentiment_result = get_sentiment(comment['text'])
            analyzed_comments.append({
                'comment': comment,
                'sentiment': sentiment_result
            })
        
        # Separar por sentimento
        positive = [c for c in analyzed_comments if c['sentiment'] == 'Positive']
        negative = [c for c in analyzed_comments if c['sentiment'] == 'Negative']
        neutral = [c for c in analyzed_comments if c['sentiment'] == 'Neutral']
        
        # Selecionar amostras (3 positivos, 2 negativos)
        selected = []
        selected.extend(positive[:3])
        selected.extend(negative[:2])
        
        # Se não tiver suficientes, adicionar neutros
        if len(selected) < 5:
            selected.extend(neutral[:5-len(selected)])
        
        # Formatar para o frontend
        formatted = []
        for item in selected[:5]:
            comment = item['comment']
            formatted.append({
                'author': comment['author'],
                'text': comment['text'][:200] + ('...' if len(comment['text']) > 200 else ''),
                'likes': comment['likes'],
                'sentiment': item['sentiment']
            })
        
        return formatted