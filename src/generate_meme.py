#!/usr/bin/env python3
import os
import sys
import json
import asyncio
import getpass
from dotenv import load_dotenv, set_key
from datetime import datetime
import logging
from typing import Dict, List, Optional, Any, Union
import argparse
import random

from core.meme_generator import MemeGenerator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('meme_generator')

# Load environment variables
load_dotenv()

# Default text if OpenAI is not configured
DEFAULT_TEXT = "Quand le dev junior déploie son code sans tests"

# Environment file path
ENV_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')

async def ensure_openai_api_key() -> str:
    """
    Ensures a valid OpenAI API key is configured
    
    Returns:
        str: The OpenAI API key
    """
    api_key = os.getenv('OPENAI_API_KEY')
    
    if not api_key or api_key == 'your_openai_api_key_here' or 'your_' in api_key:
        logger.warning("⚠️ No valid OpenAI API key found in .env file")
        logger.info("To generate punchlines, you must provide a valid OpenAI API key.")
        api_key = getpass.getpass("Enter your OpenAI API key: ")
        
        if not api_key:
            raise ValueError("No OpenAI API key provided. Cannot generate a punchline.")
        
        # Update .env file with the new API key
        set_key(ENV_PATH, 'OPENAI_API_KEY', api_key)
        os.environ['OPENAI_API_KEY'] = api_key
        logger.info("✅ OpenAI API key saved to .env file")
    
    return api_key

async def generate_meme(
    custom_text: Optional[str] = None, 
    subject: Optional[str] = None, 
    economy_mode: Optional[bool] = None, 
    send_to_telegram: Optional[bool] = None
) -> Dict[str, Any]:
    """
    Génère un mème avec le texte personnalisé ou une punchline générée par GPT-4
    
    Args:
        custom_text: Texte personnalisé à utiliser (optionnel)
        subject: Sujet pour générer une punchline (optionnel)
        economy_mode: Utiliser le mode économie de tokens (optionnel)
        send_to_telegram: Envoyer le mème sur Telegram (optionnel)
        
    Returns:
        Dict: Informations sur le mème généré
    """
    try:
        logger.info("🎬 Starting 'L'ARROGANCE!' meme generator...")
        
        # Ensure a valid OpenAI API key is configured if needed
        if not custom_text:
            await ensure_openai_api_key()
        
        # Initialize the meme generator
        meme_generator = MemeGenerator()
        
        if custom_text:
            logger.info(f"📝 Using custom text: \"{custom_text}\"")
            result = await meme_generator.generate_meme(
                custom_text=custom_text, 
                send_to_telegram=send_to_telegram
            )
        else:
            # Use OpenAI to generate a punchline with the specified subject
            if subject:
                logger.info(f"🤖 Generating a punchline with OpenAI on subject: \"{subject}\"")
            else:
                logger.info(f"🤖 Generating a punchline with OpenAI on default subject")
            
            # Display the mode used
            if economy_mode:
                logger.info("💰 Economy mode enabled: using GPT-3.5-turbo with simplified prompt")
            
            result = await meme_generator.generate_meme(
                subject=subject, 
                economy_mode=economy_mode, 
                send_to_telegram=send_to_telegram
            )
        
        logger.info(f"✅ Meme generated successfully!")
        logger.info(f"📝 Text: {result['text']}")
        logger.info(f"🎥 Video: {result['video_path']}")
        
        # Afficher les informations pour faciliter le copier-coller
        if result.get('hashtags') and result.get('description'):
            # Formater les hashtags pour qu'ils soient plus facilement copiables
            hashtags = result.get('hashtags', '')
            if isinstance(hashtags, list):
                hashtags = ' '.join(hashtags)
            # Supprimer les crochets et les guillemets si présents
            hashtags = hashtags.replace('[', '').replace(']', '').replace("'", "").replace('"', '')
            
            print("\n" + "="*80)
            print("📋 INFORMATIONS POUR COPIER-COLLER:")
            print("="*80)
            
            print("\n📝 TEXTE DU MÈME:")
            print("-"*80)
            print(result.get('text', ''))
            print("-"*80)
            
            print("\n🏷️ HASHTAGS:")
            print("-"*80)
            print(hashtags)
            print("-"*80)
            
            print("\n📄 DESCRIPTION:")
            print("-"*80)
            print(result.get('description', ''))
            print("-"*80)
            print("\n")
        
        return result
    except Exception as e:
        logger.error(f"❌ Error generating meme: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

async def generate_batch_memes(
    json_file_path: str, 
    economy_mode: Optional[bool] = None, 
    limit: Optional[int] = None, 
    send_to_telegram: Optional[bool] = None
) -> List[Dict[str, Any]]:
    """
    Génère plusieurs mèmes à partir d'un fichier JSON contenant des sujets
    
    Args:
        json_file_path: Chemin vers le fichier JSON contenant les sujets
        economy_mode: Utiliser le mode économie de tokens (optionnel)
        limit: Nombre maximum de mèmes à générer (optionnel)
        send_to_telegram: Envoyer les mèmes sur Telegram (optionnel)
        
    Returns:
        List[Dict]: Liste des informations sur les mèmes générés
    """
    try:
        # Vérifier si le fichier existe
        if not os.path.exists(json_file_path):
            logging.error(f"❌ Le fichier {json_file_path} n'existe pas.")
            return []
        
        # Charger le fichier JSON
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Extraire les sujets
        subjects = []
        for key in data:
            if isinstance(data[key], list):
                subjects.extend(data[key])
        
        if not subjects:
            logging.error("❌ Aucun sujet trouvé dans le fichier JSON.")
            return []
        
        # Limiter le nombre de sujets si nécessaire
        if limit and limit > 0:
            logging.info(f"🎲 Sélection aléatoire de {limit} sujets parmi {len(subjects)} disponibles.")
            subjects = random.sample(subjects, min(limit, len(subjects)))
        
        # Initialiser le générateur de mèmes
        meme_generator = MemeGenerator()
        
        # Générer les mèmes
        results = []
        for subject in subjects:
            logging.info(f"🎯 Génération d'un mème sur le sujet: {subject}")
            
            result = await meme_generator.generate_meme(
                subject=subject,
                economy_mode=economy_mode,
                send_to_telegram=send_to_telegram
            )
            
            results.append(result)
            
            # Afficher les informations pour faciliter le copier-coller
            if result.get('hashtags') and result.get('description'):
                # Formater les hashtags pour qu'ils soient plus facilement copiables
                hashtags = result.get('hashtags', '')
                if isinstance(hashtags, list):
                    hashtags = ' '.join(hashtags)
                # Supprimer les crochets et les guillemets si présents
                hashtags = hashtags.replace('[', '').replace(']', '').replace("'", "").replace('"', '')
                
                print("\n" + "="*80)
                print(f"📋 INFORMATIONS POUR COPIER-COLLER (Sujet: {subject}):")
                print("="*80)
                
                print("\n📝 TEXTE DU MÈME:")
                print("-"*80)
                print(result.get('text', ''))
                print("-"*80)
                
                print("\n🏷️ HASHTAGS:")
                print("-"*80)
                print(hashtags)
                print("-"*80)
                
                print("\n📄 DESCRIPTION:")
                print("-"*80)
                print(result.get('description', ''))
                print("-"*80)
                print("\n")
        
        # Enregistrer un rapport de génération
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_dir = os.path.join(os.environ.get('OUTPUT_DIRECTORY', 'output'), 'reports')
        os.makedirs(report_dir, exist_ok=True)
        report_path = os.path.join(report_dir, f"batch_report_{timestamp}.json")
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        logging.info(f"📝 Rapport de génération par lots enregistré: {report_path}")
        logging.info(f"✅ {len(results)} mèmes générés avec succès!")
        
        return results
    
    except Exception as e:
        logging.error(f"❌ Erreur lors de la génération par lots: {str(e)}")
        return []

def set_economy_mode_in_env(value: bool) -> None:
    """
    Sets the default economy mode in the .env file
    
    Args:
        value: True to enable economy mode, False to disable
    """
    set_key(ENV_PATH, 'ECONOMY_MODE', str(value).lower())
    os.environ['ECONOMY_MODE'] = str(value).lower()
    logger.info(f"✅ Mode économie {'activé' if value else 'désactivé'} par défaut dans .env")

def set_telegram_auto_send_in_env(value: bool) -> None:
    """
    Sets the default automatic sending to Telegram in the .env file
    
    Args:
        value: True to enable automatic sending, False to disable
    """
    set_key(ENV_PATH, 'TELEGRAM_AUTO_SEND', str(value).lower())
    os.environ['TELEGRAM_AUTO_SEND'] = str(value).lower()
    logger.info(f"✅ Envoi automatique sur Telegram {'activé' if value else 'désactivé'} par défaut dans .env")

def parse_arguments() -> Dict[str, Any]:
    """
    Parse command line arguments
    
    Returns:
        Dictionary of parsed arguments
    """
    parser = argparse.ArgumentParser(description='Générateur de mèmes "L\'ARROGANCE!"')
    
    # Groupe d'options mutuellement exclusives pour le texte
    text_group = parser.add_mutually_exclusive_group()
    text_group.add_argument('-t', '--text', type=str, help='Texte personnalisé pour le mème')
    text_group.add_argument('-s', '--subject', type=str, help='Sujet pour générer une punchline')
    text_group.add_argument('-b', '--batch', type=str, help='Chemin vers un fichier JSON contenant des sujets')
    
    # Options supplémentaires
    parser.add_argument('-e', '--economy', action='store_true', help='Activer le mode économie de tokens (GPT-3.5 au lieu de GPT-4)')
    parser.add_argument('--telegram', action='store_true', help='Envoyer le mème sur Telegram')
    parser.add_argument('-l', '--limit', type=int, help='Limiter le nombre de mèmes générés en mode batch')
    
    args = parser.parse_args()
    
    # Vérifier si aucune option n'est spécifiée
    if not args.text and not args.subject and not args.batch:
        # Utiliser le fichier JSON par défaut
        default_json = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'json.json')
        if os.path.exists(default_json):
            logger.info(f"🔄 Aucun sujet spécifié, utilisation du fichier par défaut: {default_json}")
            args.batch = default_json
        else:
            # Utiliser le sujet par défaut
            logger.info("🔄 Aucun sujet spécifié, utilisation du sujet par défaut")
            args.subject = "L'arrogance des développeurs"
    
    # Convertir les arguments en dictionnaire
    return {
        'custom_text': args.text,
        'subject': args.subject,
        'batch_file': args.batch,
        'economy_mode': args.economy,
        'send_to_telegram': args.telegram,
        'limit': args.limit
    }

async def main() -> None:
    """
    Main function
    """
    try:
        # Parse command line arguments
        args = parse_arguments()
        
        # Ensure a valid OpenAI API key is configured
        await ensure_openai_api_key()
        
        # Set default economy mode if requested
        if args.get('set_default_economy', False):
            set_economy_mode_in_env(args['economy_mode'])
        
        # Set default Telegram auto-send if requested
        if args.get('set_default_telegram', False):
            set_telegram_auto_send_in_env(args['send_to_telegram'])
        
        # Generate meme based on arguments
        if args['batch_file']:
            # Batch generation from JSON file
            logger.info(f"📦 Génération par lots à partir du fichier: {args['batch_file']}")
            results = await generate_batch_memes(
                args['batch_file'],
                economy_mode=args['economy_mode'],
                limit=args['limit'],
                send_to_telegram=args['send_to_telegram']
            )
            logger.info(f"✅ {len(results)} mèmes générés avec succès!")
            
        elif args['custom_text']:
            # Generate meme with custom text
            logger.info(f"🎬 Génération d'un mème avec le texte personnalisé: {args['custom_text']}")
            result = await generate_meme(
                custom_text=args['custom_text'],
                economy_mode=args['economy_mode'],
                send_to_telegram=args['send_to_telegram']
            )
            logger.info(f"✅ Mème généré avec succès: {result['video_path']}")
            
        else:
            # Generate meme with subject
            subject = args['subject'] or "L'arrogance des développeurs"
            logger.info(f"🎬 Génération d'un mème sur le sujet: {subject}")
            result = await generate_meme(
                subject=subject,
                economy_mode=args['economy_mode'],
                send_to_telegram=args['send_to_telegram']
            )
            logger.info(f"✅ Mème généré avec succès: {result['video_path']}")
            logger.info(f"📝 Texte: {result['text']}")
        
    except Exception as e:
        logger.error(f"❌ Erreur: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\n⚠️ Operation cancelled by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"❌ Fatal error: {str(e)}")
        sys.exit(1) 