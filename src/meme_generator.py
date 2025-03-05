from openai_client import OpenAIClient
from video_processor import VideoProcessor
from telegram_client import TelegramClient

class MemeGenerator:
    def __init__(self):
        self.openai_client = OpenAIClient()
        self.video_processor = VideoProcessor()
        self.telegram_client = TelegramClient()
    
    async def generate_meme(self, custom_text=None, subject=None, economy_mode=None, send_to_telegram=None):
        """
        Génère un mème vidéo en suivant ces étapes:
        1. Générer une punchline avec OpenAI GPT-4 (si custom_text n'est pas fourni)
        2. Ajouter la punchline sur la vidéo template
        3. Exporter la vidéo avec le texte incrusté
        4. Générer des hashtags et une description pour les réseaux sociaux
        5. Envoyer la vidéo sur Telegram (si configuré)
        
        Args:
            custom_text (str, optional): Texte personnalisé à utiliser au lieu de générer une punchline
            subject (str, optional): Le sujet sur lequel générer une punchline
            economy_mode (bool, optional): Activer le mode économie de tokens
            send_to_telegram (bool, optional): Forcer l'envoi ou non sur Telegram
            
        Returns:
            dict: Informations sur le mème généré (texte et chemin du fichier)
        """
        try:
            # Étape 1: Générer une punchline (si nécessaire)
            if custom_text:
                text = custom_text
            else:
                # Utiliser le prompt prédéfini dans OpenAIClient avec le sujet spécifié
                text = await self.openai_client.generate_punchline(subject=subject, economy_mode=economy_mode)
            
            # Étape 2 & 3: Ajouter le texte sur la vidéo et l'exporter
            output_path = await self.video_processor.create_meme(text)
            
            # Déterminer le sujet final (celui fourni ou celui par défaut)
            final_subject = subject if subject else self.openai_client.default_subject
            
            # Créer le résultat de base
            result = {
                "text": text,
                "video_path": output_path,
                "subject": final_subject
            }
            
            # Étape 4: Générer des hashtags et une description pour les réseaux sociaux
            try:
                # Générer les hashtags
                hashtags = await self.openai_client.generate_hashtags(final_subject, text, economy_mode)
                result["hashtags"] = hashtags
                
                # Générer la description
                description = await self.openai_client.generate_description(final_subject, text, economy_mode)
                result["description"] = description
                
                print(f"✅ Contenu social généré avec succès!")
                print(f"📝 Hashtags: {' '.join(hashtags)}")
                print(f"📝 Description: {description}")
            except Exception as e:
                print(f"⚠️ Erreur lors de la génération du contenu social: {str(e)}")
                # Utiliser des valeurs par défaut
                result["hashtags"] = ["#LARROGANCE", "#meme", "#humour"]
                result["description"] = f"Un regard satirique sur {final_subject}."
            
            # Étape 5: Envoyer la vidéo sur Telegram si configuré
            should_send = send_to_telegram if send_to_telegram is not None else self.telegram_client.auto_send
            if should_send:
                # Créer un message complet avec le sujet, la punchline, la description et les hashtags
                # Format du message pour Telegram (avec formatage Markdown)
                caption = f"*🎭 L'ARROGANCE!*\n\n"
                caption += f"*Sujet:* {result['subject']}\n\n"
                caption += f"*\"{text}\"*\n\n"
                caption += f"{result['description']}\n\n"
                caption += " ".join(result['hashtags'])
                
                await self.telegram_client.send_video(output_path, caption)
            
            return result
        except Exception as e:
            print(f"❌ Erreur lors de la génération du mème: {str(e)}")
            raise e
    
    async def generate_batch_memes(self, subjects, economy_mode=None, send_to_telegram=None):
        """
        Génère plusieurs mèmes à partir d'une liste de sujets
        
        Args:
            subjects (list): Liste des sujets
            economy_mode (bool, optional): Activer le mode économie de tokens
            send_to_telegram (bool, optional): Forcer l'envoi ou non sur Telegram
            
        Returns:
            list: Liste des résultats de génération de mèmes
        """
        results = []
        # Déterminer si on doit envoyer les vidéos sur Telegram
        should_send = send_to_telegram if send_to_telegram is not None else self.telegram_client.auto_send
        
        for i, subject in enumerate(subjects):
            try:
                print(f"\n[{i+1}/{len(subjects)}] 🤖 Génération d'un mème sur le sujet: \"{subject}\"")
                
                # Afficher le mode utilisé
                if economy_mode:
                    print("💰 Mode économie activé: utilisation de GPT-3.5-turbo avec un prompt simplifié")
                
                # Générer le mème et l'envoyer immédiatement sur Telegram si configuré
                result = await self.generate_meme(subject=subject, economy_mode=economy_mode, send_to_telegram=should_send)
                
                print(f"✅ Mème généré avec succès!")
                print(f"📝 Texte: {result['text']}")
                print(f"🎥 Vidéo: {result['video_path']}")
                
                results.append(result)
            except Exception as e:
                print(f"❌ Erreur lors de la génération du mème pour le sujet '{subject}': {str(e)}")
                # Continuer avec le sujet suivant
        
        # Nous n'avons plus besoin d'envoyer les vidéos en batch à la fin
        # car chaque vidéo est envoyée immédiatement après sa génération
        
        return results 