from deep_translator import GoogleTranslator

def translate_to_english(text: str) -> str:
    """Traduz texto para inglês"""
    if not text:
        return text
    
    try:
        translated = GoogleTranslator(source='auto', target='en').translate(text)
        return translated
    except:
        return text