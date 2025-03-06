"""
DEPRECATED: This module is deprecated and will be removed in a future version.
Please use the new MVC structure instead:
- controllers/meme_controller.py for meme generation logic
"""

import warnings

warnings.warn(
    "The MemeGenerator class is deprecated and will be removed in a future version. "
    "Please use MemeController from controllers/meme_controller.py instead.",
    DeprecationWarning,
    stacklevel=2
)

from clients.openai_client import OpenAIClient
from core.video_processor import VideoProcessor
from clients.telegram_client import TelegramClient
from core.quality_pipeline import QualityPipeline
import logging
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('meme_generator')

class MemeGenerator:
    def __init__(self):
        self.openai_client = OpenAIClient()
        self.video_processor = VideoProcessor()
        self.telegram_client = TelegramClient()
        self.quality_pipeline = QualityPipeline()
        
        # Vérifier si la pipeline de qualité est activée
        self.use_quality_pipeline = os.getenv('USE_QUALITY_PIPELINE', 'true').lower() == 'true'
        
        if self.use_quality_pipeline:
            logger.info("🔍 Pipeline de qualité activée pour la génération de punchlines")
        else:
            logger.info("🔍 Pipeline de qualité désactivée (utilisation de la génération simple)")
    
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
                punchline_metadata = None
            else:
                # Utiliser la pipeline de qualité ou la génération simple selon la configuration
                if self.use_quality_pipeline:
                    logger.info(f"🔍 Génération de punchlines avec la pipeline de qualité pour le sujet: '{subject or self.openai_client.default_subject}'")
                    text, punchline_metadata = await self.quality_pipeline.get_best_punchline(
                        subject=subject or self.openai_client.default_subject,
                        economy_mode=economy_mode
                    )
                    
                    # Afficher les scores d'évaluation
                    if punchline_metadata and "evaluation" in punchline_metadata:
                        eval_scores = punchline_metadata["evaluation"]
                        # Vérifier quels critères sont disponibles dans l'évaluation
                        if "cruaute" in eval_scores:
                            # Nouveaux critères
                            logger.info(f"📊 Scores d'évaluation: Cruauté={eval_scores['cruaute']:.2f}, "
                                       f"Provocation={eval_scores['provocation']:.2f}, Pertinence={eval_scores['pertinence']:.2f}, "
                                       f"Concision={eval_scores['concision']:.2f}, Impact={eval_scores['impact']:.2f}")
                        else:
                            # Anciens critères (pour la compatibilité)
                            logger.info(f"📊 Scores d'évaluation: Originalité={eval_scores.get('originality', 0):.2f}, "
                                       f"Humour={eval_scores.get('humor', 0):.2f}, Pertinence={eval_scores.get('relevance', 0):.2f}, "
                                       f"Concision={eval_scores.get('conciseness', 0):.2f}, Impact={eval_scores.get('impact', 0):.2f}")
                        
                        logger.info(f"📊 Score global: {punchline_metadata['overall_score']:.2f}")
                else:
                    # Utiliser le prompt prédéfini dans OpenAIClient avec le sujet spécifié
                    text = await self.openai_client.generate_punchline(subject=subject, economy_mode=economy_mode)
                    punchline_metadata = None
            
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
            
            # Ajouter les métadonnées d'évaluation si disponibles
            if punchline_metadata:
                result["quality_evaluation"] = {
                    "overall_score": punchline_metadata["overall_score"],
                    "criteria_scores": punchline_metadata["evaluation"]
                }
            
            # Étape 4: Générer des hashtags et une description pour les réseaux sociaux
            try:
                # Générer les hashtags
                hashtags = await self.openai_client.generate_hashtags(final_subject, text, economy_mode)
                result["hashtags"] = hashtags
                
                # Générer la description
                description = await self.openai_client.generate_description(final_subject, text, economy_mode)
                result["description"] = description
                
                logger.info(f"✅ Contenu social généré avec succès!")
                logger.info(f"📝 Hashtags: {' '.join(hashtags)}")
                logger.info(f"📝 Description: {description}")
            except Exception as e:
                logger.error(f"⚠️ Erreur lors de la génération du contenu social: {str(e)}")
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
                
                # Ajouter les scores d'évaluation si disponibles
                if "quality_evaluation" in result:
                    caption += f"\n\n📊 *Score de qualité:* {result['quality_evaluation']['overall_score']:.2f}/1"
                
                await self.telegram_client.send_video(output_path, caption)
            
            return result
        except Exception as e:
            logger.error(f"❌ Erreur lors de la génération du mème: {str(e)}")
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
                logger.info(f"\n[{i+1}/{len(subjects)}] 🤖 Génération d'un mème sur le sujet: \"{subject}\"")
                
                # Afficher le mode utilisé
                if economy_mode:
                    logger.info("💰 Mode économie activé: utilisation de GPT-3.5-turbo avec un prompt simplifié")
                
                # Générer le mème et l'envoyer immédiatement sur Telegram si configuré
                result = await self.generate_meme(subject=subject, economy_mode=economy_mode, send_to_telegram=should_send)
                
                logger.info(f"✅ Mème généré avec succès!")
                logger.info(f"📝 Texte: {result['text']}")
                logger.info(f"🎥 Vidéo: {result['video_path']}")
                
                results.append(result)
            except Exception as e:
                logger.error(f"❌ Erreur lors de la génération du mème pour le sujet '{subject}': {str(e)}")
                # Continuer avec le sujet suivant
        
        # Si la pipeline de qualité est activée, afficher les statistiques globales
        if self.use_quality_pipeline:
            try:
                stats = self.quality_pipeline.get_evaluation_stats()
                logger.info("\n📊 Statistiques de la pipeline de qualité:")
                logger.info(f"Total des punchlines évaluées: {stats['total_punchlines']}")
                logger.info(f"Punchlines sélectionnées: {stats['selected_punchlines']}")
                logger.info(f"Score moyen global: {stats['average_score']:.2f}")
                logger.info(f"Score moyen des punchlines sélectionnées: {stats['average_selected_score']:.2f}")
            except Exception as e:
                logger.error(f"❌ Erreur lors de la récupération des statistiques: {str(e)}")
        
        return results 