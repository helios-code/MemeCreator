import os
import asyncio
from dotenv import load_dotenv

from meme_generator import MemeGenerator

# Charger les variables d'environnement
load_dotenv()

# Prompt par défaut pour la génération de punchlines
DEFAULT_PROMPT = "Génère une punchline humoristique pour introduire quelqu'un qui crie 'L'ARROGANCE!'"

async def main():
    """
    Fonction principale qui génère un mème vidéo 'L'ARROGANCE!' à chaque exécution
    """
    try:
        print("🎬 Démarrage du générateur de mèmes 'L'ARROGANCE!'...")
        
        # Initialiser le générateur de mèmes
        meme_generator = MemeGenerator()
        
        # Générer le mème avec le prompt par défaut
        result = await meme_generator.generate_meme(prompt=DEFAULT_PROMPT)
        
        print(f"✅ Mème généré avec succès!")
        print(f"📝 Texte: {result['text']}")
        print(f"🎥 Vidéo: {result['video_path']}")
        
        return result
    except Exception as e:
        print(f"❌ Erreur lors de la génération du mème: {str(e)}")
        raise e

if __name__ == "__main__":
    # Exécuter la fonction principale de manière asynchrone
    result = asyncio.run(main()) 