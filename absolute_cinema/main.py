import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import uvicorn

# Determinar o diretório raiz do projeto
ROOT_DIR = Path(__file__).resolve().parent
# Adicionar pasta raiz ao sys.path para permitir imports
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR.parent))  # adicionar pasta pai para imports absolutos

# Carregar variáveis de ambiente
load_dotenv(dotenv_path=ROOT_DIR / ".env")

# Importar o app das views
try:
    from absolute_cinema.views.app import app
except ModuleNotFoundError:
    # Se estivermos rodando dentro da própria pasta absolute_cinema
    from views.app import app

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🎬 ABSOLUTE CINEMA API - VERSÃO REAL")
    print("="*60)
    
    YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
    print("✓ YouTube API: " + ("Conectada ✓" if YOUTUBE_API_KEY else "Não configurada ⚠️"))
    print("✓ TextBlob: Análise de Sentimentos Ativa")
    print("="*60)
    print("🚀 Iniciando servidor...")
    print("📍 http://localhost:8000")
    print("📚 Docs: http://localhost:8000/docs")
    print("📁 Frontend: Abra o index.html no navegador")
    print("="*60 + "\n")
    
    uvicorn.run(
        "absolute_cinema.views.app:app" if "absolute_cinema" in sys.modules else "views.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )