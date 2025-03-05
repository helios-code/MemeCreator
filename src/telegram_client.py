import os
import asyncio
import time
from telegram import Bot
from telegram.error import TelegramError, TimedOut, NetworkError
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

class TelegramClient:
    def __init__(self):
        """
        Initialise le client Telegram avec les paramètres du fichier .env
        """
        self.token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.chat_id = os.getenv('TELEGRAM_CHAT_ID')
        
        # Gérer correctement la valeur booléenne, même si elle est entourée de guillemets
        auto_send_value = os.getenv('TELEGRAM_AUTO_SEND', 'false')
        # Supprimer les guillemets éventuels
        auto_send_value = auto_send_value.strip("'\"")
        self.auto_send = auto_send_value.lower() == 'true'
        
        # Afficher les paramètres pour le débogage
        print(f"🔍 Configuration Telegram:")
        print(f"  - Token configuré: {'Oui' if self.token and self.token != 'your_telegram_bot_token_here' else 'Non'}")
        print(f"  - Chat ID configuré: {'Oui' if self.chat_id and self.chat_id != 'your_telegram_chat_id_here' else 'Non'}")
        print(f"  - Valeur brute de TELEGRAM_AUTO_SEND: '{auto_send_value}'")
        print(f"  - Envoi automatique: {'Activé' if self.auto_send else 'Désactivé'}")
        
        # Vérifier si les paramètres sont configurés
        if self.auto_send and (not self.token or self.token == 'your_telegram_bot_token_here'):
            print("⚠️ L'envoi automatique sur Telegram est activé mais le token du bot n'est pas configuré.")
            self.auto_send = False
        
        if self.auto_send and (not self.chat_id or self.chat_id == 'your_telegram_chat_id_here'):
            print("⚠️ L'envoi automatique sur Telegram est activé mais l'ID du chat n'est pas configuré.")
            self.auto_send = False
        
        # Initialiser le bot si les paramètres sont valides
        if self.token and self.token != 'your_telegram_bot_token_here':
            try:
                self.bot = Bot(token=self.token)
                print("✅ Client Telegram initialisé avec succès.")
            except Exception as e:
                print(f"❌ Erreur lors de l'initialisation du client Telegram: {str(e)}")
                self.auto_send = False
                self.bot = None
        else:
            print("❌ Token Telegram non configuré ou invalide.")
            self.bot = None
            self.auto_send = False
    
    async def send_video(self, video_path, caption=None, max_retries=3):
        """
        Envoie une vidéo sur Telegram
        
        Args:
            video_path (str): Chemin vers la vidéo à envoyer
            caption (str, optional): Légende de la vidéo
            max_retries (int, optional): Nombre maximum de tentatives en cas d'erreur
            
        Returns:
            bool: True si l'envoi a réussi, False sinon
        """
        # Vérifier si l'envoi est activé
        if not self.auto_send:
            print("ℹ️ L'envoi sur Telegram est désactivé.")
            return False
        
        if not self.bot:
            print("❌ Le bot Telegram n'est pas initialisé.")
            return False
        
        # Vérifier que le fichier existe
        if not os.path.exists(video_path):
            print(f"❌ Erreur: Le fichier vidéo n'existe pas: {video_path}")
            return False
        
        # Afficher les informations pour le débogage
        print(f"🔍 Envoi de la vidéo sur Telegram:")
        print(f"  - Fichier: {video_path}")
        print(f"  - Taille: {os.path.getsize(video_path) / (1024*1024):.2f} MB")
        print(f"  - Chat ID: {self.chat_id}")
        
        # Tentatives d'envoi avec gestion des erreurs
        for attempt in range(1, max_retries + 1):
            try:
                # Envoyer la vidéo
                print(f"📤 Envoi de la vidéo sur Telegram (tentative {attempt}/{max_retries})...")
                with open(video_path, 'rb') as video:
                    message = await self.bot.send_video(
                        chat_id=self.chat_id,
                        video=video,
                        caption=caption,
                        supports_streaming=True,
                        parse_mode='Markdown'  # Activer le formatage Markdown
                    )
                    print(f"✅ Vidéo envoyée avec succès sur Telegram! Message ID: {message.message_id}")
                return True
            except TimedOut as e:
                # Erreur de timeout, on réessaie
                print(f"⚠️ Timeout lors de l'envoi de la vidéo (tentative {attempt}/{max_retries}): {str(e)}")
                if attempt < max_retries:
                    # Attendre un peu plus longtemps à chaque tentative
                    wait_time = 2 * attempt
                    print(f"⏳ Nouvelle tentative dans {wait_time} secondes...")
                    await asyncio.sleep(wait_time)
                else:
                    print(f"❌ Échec après {max_retries} tentatives.")
                    return False
            except NetworkError as e:
                # Erreur réseau, on réessaie
                print(f"⚠️ Erreur réseau lors de l'envoi de la vidéo (tentative {attempt}/{max_retries}): {str(e)}")
                if attempt < max_retries:
                    # Attendre un peu plus longtemps à chaque tentative
                    wait_time = 3 * attempt
                    print(f"⏳ Nouvelle tentative dans {wait_time} secondes...")
                    await asyncio.sleep(wait_time)
                else:
                    print(f"❌ Échec après {max_retries} tentatives.")
                    return False
            except TelegramError as e:
                print(f"❌ Erreur Telegram lors de l'envoi de la vidéo: {str(e)}")
                # Afficher plus de détails sur l'erreur
                if hasattr(e, 'message'):
                    print(f"  - Message d'erreur: {e.message}")
                return False
            except Exception as e:
                print(f"❌ Erreur inattendue lors de l'envoi de la vidéo: {str(e)}")
                import traceback
                traceback.print_exc()
                return False
    
    async def send_batch_videos(self, results, delay_between_videos=2):
        """
        Envoie plusieurs vidéos sur Telegram
        
        Args:
            results (list): Liste des résultats de génération de mèmes
            delay_between_videos (int, optional): Délai en secondes entre chaque envoi
            
        Returns:
            int: Nombre de vidéos envoyées avec succès
        """
        if not self.auto_send or not self.bot:
            print("ℹ️ L'envoi par lots sur Telegram est désactivé.")
            return 0
        
        success_count = 0
        for i, result in enumerate(results):
            try:
                print(f"\n[{i+1}/{len(results)}] 📤 Envoi de la vidéo '{result['subject']}' sur Telegram...")
                
                # Créer un message complet avec le sujet, la punchline, la description et les hashtags
                caption = f"*🎭 L'ARROGANCE!*\n\n"
                caption += f"*Sujet:* {result['subject']}\n\n"
                caption += f"*\"{result['text']}\"*\n\n"
                
                # Ajouter la description si elle existe
                if 'description' in result:
                    caption += f"{result['description']}\n\n"
                
                # Ajouter les hashtags si ils existent
                if 'hashtags' in result:
                    caption += " ".join(result['hashtags'])
                
                success = await self.send_video(result['video_path'], caption)
                if success:
                    success_count += 1
                
                # Attendre un peu entre chaque envoi pour éviter les limitations de l'API
                if i < len(results) - 1:  # Ne pas attendre après le dernier envoi
                    print(f"⏳ Attente de {delay_between_videos} secondes avant le prochain envoi...")
                    await asyncio.sleep(delay_between_videos)
            except Exception as e:
                print(f"❌ Erreur lors de l'envoi d'une vidéo: {str(e)}")
        
        return success_count 