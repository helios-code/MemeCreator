import os
import asyncio
from dotenv import load_dotenv

from core.meme_generator import MemeGenerator

# Charger les variables d'environnement
load_dotenv()

# Sujet par défaut pour la génération de punchlines
DEFAULT_SUBJECT = "L'arrogance des développeurs"

async def main():
    """
    Fonction principale qui génère un mème vidéo 'L'ARROGANCE!' à chaque exécution
    """
    try:
        print("🎬 Démarrage du générateur de mèmes 'L'ARROGANCE!'...")
        
        # Initialiser le générateur de mèmes
        meme_generator = MemeGenerator()
        
        # Générer le mème avec le sujet par défaut
        result = await meme_generator.generate_meme(subject=DEFAULT_SUBJECT)
        
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