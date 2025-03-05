#!/usr/bin/env python3
import os
import sys
import json
import asyncio
import getpass
from dotenv import load_dotenv, set_key
import datetime

from meme_generator import MemeGenerator

# Charger les variables d'environnement
load_dotenv()

# Texte par défaut si OpenAI n'est pas configuré
DEFAULT_TEXT = "Quand le dev junior déploie son code sans tests"

async def ensure_openai_api_key():
    """
    S'assure qu'une clé API OpenAI valide est configurée
    """
    api_key = os.getenv('OPENAI_API_KEY')
    
    if not api_key or api_key == 'your_openai_api_key_here' or 'your_' in api_key:
        print("⚠️ Aucune clé API OpenAI valide n'a été trouvée dans le fichier .env")
        print("Pour générer des punchlines, vous devez fournir une clé API OpenAI valide.")
        api_key = getpass.getpass("Entrez votre clé API OpenAI: ")
        
        if not api_key:
            raise ValueError("Aucune clé API OpenAI fournie. Impossible de générer une punchline.")
        
        # Mettre à jour le fichier .env avec la nouvelle clé API
        env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
        set_key(env_path, 'OPENAI_API_KEY', api_key)
        os.environ['OPENAI_API_KEY'] = api_key
        print("✅ Clé API OpenAI enregistrée dans le fichier .env")
    
    return api_key

async def generate_meme(custom_text=None, subject=None, economy_mode=None, send_to_telegram=None):
    """
    Génère un mème vidéo 'L'ARROGANCE!' avec une punchline générée par GPT-4
    
    Args:
        custom_text (str, optional): Texte personnalisé à utiliser (ignoré si non None)
        subject (str, optional): Le sujet sur lequel générer une punchline
        economy_mode (bool, optional): Activer le mode économie de tokens
        send_to_telegram (bool, optional): Forcer l'envoi ou non sur Telegram
    """
    try:
        print("🎬 Démarrage du générateur de mèmes 'L'ARROGANCE!'...")
        
        # S'assurer qu'une clé API OpenAI valide est configurée
        if not custom_text:
            await ensure_openai_api_key()
        
        # Initialiser le générateur de mèmes
        meme_generator = MemeGenerator()
        
        if custom_text:
            print(f"📝 Utilisation du texte personnalisé: \"{custom_text}\"")
            result = await meme_generator.generate_meme(custom_text=custom_text, send_to_telegram=send_to_telegram)
        else:
            # Utiliser OpenAI pour générer une punchline avec le sujet spécifié
            if subject:
                print(f"🤖 Génération d'une punchline avec OpenAI sur le sujet: \"{subject}\"")
            else:
                print(f"🤖 Génération d'une punchline avec OpenAI sur le sujet par défaut")
            
            # Afficher le mode utilisé
            if economy_mode:
                print("💰 Mode économie activé: utilisation de GPT-3.5-turbo avec un prompt simplifié")
            
            result = await meme_generator.generate_meme(subject=subject, economy_mode=economy_mode, send_to_telegram=send_to_telegram)
        
        print(f"✅ Mème généré avec succès!")
        print(f"📝 Texte: {result['text']}")
        print(f"🎥 Vidéo: {result['video_path']}")
        
        return result
    except Exception as e:
        print(f"❌ Erreur lors de la génération du mème: {str(e)}")
        raise e

async def generate_batch_memes(json_file_path, economy_mode=None, limit=None, send_to_telegram=None):
    """
    Génère plusieurs mèmes à partir d'une liste de sujets dans un fichier JSON
    
    Args:
        json_file_path (str): Chemin vers le fichier JSON contenant les sujets
        economy_mode (bool, optional): Activer le mode économie de tokens
        limit (int, optional): Limite le nombre de mèmes à générer
        send_to_telegram (bool, optional): Forcer l'envoi ou non sur Telegram
    
    Returns:
        list: Liste des résultats de génération de mèmes
    """
    try:
        # Charger les sujets depuis le fichier JSON
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Vérifier que le fichier contient une liste de sujets
        if 'sujets_clivants' not in data:
            raise ValueError("Le fichier JSON doit contenir une clé 'sujets_clivants' avec une liste de sujets")
        
        subjects = data['sujets_clivants']
        
        # Limiter le nombre de sujets si demandé
        if limit and limit > 0:
            subjects = subjects[:limit]
        
        print(f"🎬 Démarrage de la génération par lots de {len(subjects)} mèmes...")
        
        # S'assurer qu'une clé API OpenAI valide est configurée
        await ensure_openai_api_key()
        
        # Initialiser le générateur de mèmes
        meme_generator = MemeGenerator()
        
        # Générer les mèmes en batch
        results = await meme_generator.generate_batch_memes(subjects, economy_mode=economy_mode, send_to_telegram=send_to_telegram)
        
        # Générer un rapport JSON des mèmes générés
        if results:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            report_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'output', f'batch_report_{timestamp}.json')
            
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump({
                    'timestamp': timestamp,
                    'total_subjects': len(subjects),
                    'successful_generations': len(results),
                    'economy_mode': bool(economy_mode),
                    'results': results
                }, f, ensure_ascii=False, indent=2)
            
            print(f"\n📊 Rapport de génération enregistré: {report_path}")
        
        print(f"\n✅ Génération par lots terminée! {len(results)}/{len(subjects)} mèmes générés avec succès.")
        return results
    except Exception as e:
        print(f"❌ Erreur lors de la génération par lots: {str(e)}")
        raise e

def print_usage():
    """Affiche l'aide pour l'utilisation du script"""
    print(f"""
Usage: python {sys.argv[0]} [options]

Options:
  -h, --help                  Affiche cette aide
  -t, --text "texte"          Utilise un texte personnalisé au lieu de générer une punchline
  -s, --subject "sujet"       Spécifie le sujet sur lequel générer une punchline
  -e, --economy               Active le mode économie de tokens (utilise GPT-3.5-turbo)
  -b, --batch "fichier.json"  Génère des mèmes par lots à partir d'un fichier JSON
  -l, --limit N               Limite le nombre de mèmes à générer en mode batch
  --telegram                  Force l'envoi des mèmes sur Telegram
  --no-telegram               Désactive l'envoi des mèmes sur Telegram
  
Exemples:
  python {sys.argv[0]}                                  # Génère un mème avec une punchline satirique sur le sujet par défaut
  python {sys.argv[0]} -t "Mon texte personnalisé"      # Génère un mème avec un texte personnalisé
  python {sys.argv[0]} -s "Les banques suisses"         # Génère un mème sur le sujet des banques suisses
  python {sys.argv[0]} -e                               # Génère un mème en mode économie de tokens
  python {sys.argv[0]} -s "Les politiciens" -e          # Génère un mème sur les politiciens en mode économie
  python {sys.argv[0]} -b "sujets.json"                 # Génère des mèmes pour tous les sujets du fichier JSON
  python {sys.argv[0]} -b "sujets.json" -l 5            # Génère des mèmes pour les 5 premiers sujets du fichier JSON
  python {sys.argv[0]} -b "sujets.json" -e              # Génère des mèmes en mode économie pour tous les sujets
  python {sys.argv[0]} -s "Les médias" --telegram       # Génère un mème et l'envoie sur Telegram
""")

def set_economy_mode_in_env(value):
    """
    Définit le mode économie dans le fichier .env
    
    Args:
        value (bool): Valeur du mode économie
    """
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
    set_key(env_path, 'ECONOMY_MODE', str(value).lower())
    os.environ['ECONOMY_MODE'] = str(value).lower()
    print(f"💰 Mode économie {'activé' if value else 'désactivé'} par défaut dans le fichier .env")

def set_telegram_auto_send_in_env(value):
    """
    Définit l'envoi automatique sur Telegram dans le fichier .env
    
    Args:
        value (bool): Valeur de l'envoi automatique
    """
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
    set_key(env_path, 'TELEGRAM_AUTO_SEND', str(value).lower())
    os.environ['TELEGRAM_AUTO_SEND'] = str(value).lower()
    print(f"📱 Envoi automatique sur Telegram {'activé' if value else 'désactivé'} par défaut dans le fichier .env")

if __name__ == "__main__":
    # Analyser les arguments de la ligne de commande
    custom_text = None
    subject = None
    economy_mode = None
    set_default_economy = False
    batch_file = None
    limit = None
    send_to_telegram = None
    set_default_telegram = False
    
    i = 1
    while i < len(sys.argv):
        arg = sys.argv[i]
        
        if arg in ("-h", "--help"):
            print_usage()
            sys.exit(0)
        elif arg in ("-t", "--text") and i + 1 < len(sys.argv):
            custom_text = sys.argv[i + 1]
            i += 2
        elif arg in ("-s", "--subject") and i + 1 < len(sys.argv):
            subject = sys.argv[i + 1]
            i += 2
        elif arg in ("-e", "--economy"):
            economy_mode = True
            i += 1
        elif arg in ("--set-economy"):
            set_default_economy = True
            economy_mode = True
            i += 1
        elif arg in ("--unset-economy"):
            set_default_economy = True
            economy_mode = False
            i += 1
        elif arg in ("-b", "--batch") and i + 1 < len(sys.argv):
            batch_file = sys.argv[i + 1]
            i += 2
        elif arg in ("-l", "--limit") and i + 1 < len(sys.argv):
            try:
                limit = int(sys.argv[i + 1])
                if limit <= 0:
                    raise ValueError("La limite doit être un entier positif")
            except ValueError as e:
                print(f"❌ Erreur: {str(e)}")
                print_usage()
                sys.exit(1)
            i += 2
        elif arg in ("--telegram"):
            send_to_telegram = True
            i += 1
        elif arg in ("--no-telegram"):
            send_to_telegram = False
            i += 1
        elif arg in ("--set-telegram"):
            set_default_telegram = True
            send_to_telegram = True
            i += 1
        elif arg in ("--unset-telegram"):
            set_default_telegram = True
            send_to_telegram = False
            i += 1
        elif arg in ("-p", "--prompt"):
            print("⚠️ L'option -p/--prompt est obsolète. Utilisez -s/--subject pour spécifier un sujet.")
            if i + 1 < len(sys.argv) and not sys.argv[i + 1].startswith("-"):
                i += 2  # Ignorer l'argument suivant s'il ne commence pas par -
            else:
                i += 1
        else:
            print(f"Option inconnue: {arg}")
            print_usage()
            sys.exit(1)
    
    # Définir le mode économie par défaut si demandé
    if set_default_economy:
        set_economy_mode_in_env(economy_mode)
    
    # Définir l'envoi automatique sur Telegram par défaut si demandé
    if set_default_telegram:
        set_telegram_auto_send_in_env(send_to_telegram)
    
    # Exécuter la fonction principale de manière asynchrone
    if batch_file:
        asyncio.run(generate_batch_memes(batch_file, economy_mode=economy_mode, limit=limit, send_to_telegram=send_to_telegram))
    else:
        asyncio.run(generate_meme(custom_text=custom_text, subject=subject, economy_mode=economy_mode, send_to_telegram=send_to_telegram)) 