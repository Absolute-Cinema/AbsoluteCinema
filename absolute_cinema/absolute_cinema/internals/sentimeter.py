from textblob import TextBlob

def get_sentiment(text: str) -> str:
    """
    Classifica o sentimento de um texto
    
    Args:
        text: Texto para análise
        
    Returns:
        str: 'Positive', 'Negative' ou 'Neutral'
    """
    try:
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity
        
        if polarity > 0.1:
            return 'Positive'
        elif polarity < -0.1:
            return 'Negative'
        else:
            return 'Neutral'
    except:
        return 'Neutral'

def get_polarity(text: str) -> float:
    """
    Retorna a polaridade de um texto (-1 a 1)
    
    Args:
        text: Texto para análise
        
    Returns:
        float: Polaridade do texto
    """
    try:
        blob = TextBlob(text)
        return blob.sentiment.polarity
    except:
        return 0.0

def calculate_score_from_comments(comments: list) -> dict:
    """
    Calcula score baseado em lista de comentários
    
    Args:
        comments: Lista de comentários (cada um com 'text')
        
    Returns:
        dict: Estatísticas da análise
    """
    if not comments:
        return {
            'score': 50.0,
            'positive': 0,
            'negative': 0,
            'neutral': 0,
            'total_comments': 0,
            'avg_polarity': 0
        }
    
    sentiments = []
    polarities = []
    
    for comment in comments:
        sentiment = get_sentiment(comment['text'])
        polarity = get_polarity(comment['text'])
        
        sentiments.append(sentiment)
        polarities.append(polarity)
    
    # Contar sentimentos
    total = len(sentiments)
    positive = sentiments.count('Positive')
    negative = sentiments.count('Negative')
    neutral = sentiments.count('Neutral')
    
    # Calcular percentuais
    positive_pct = (positive / total * 100) if total > 0 else 0
    negative_pct = (negative / total * 100) if total > 0 else 0
    neutral_pct = (neutral / total * 100) if total > 0 else 0
    
    # Score final (0-100)
    avg_polarity = sum(polarities) / len(polarities) if polarities else 0
    score = ((avg_polarity + 1) / 2) * 100
    score = max(0, min(100, score))
    
    return {
        'score': round(score, 1),
        'positive': round(positive_pct, 1),
        'negative': round(negative_pct, 1),
        'neutral': round(neutral_pct, 1),
        'total_comments': total,
        'avg_polarity': round(avg_polarity, 2)
    }