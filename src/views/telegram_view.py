import logging
from typing import Dict, List, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('telegram_view')

class TelegramView:
    """
    View for handling Telegram message formatting and display.
    """
    
    def format_meme_caption(self, meme_data: Dict[str, Any]) -> str:
        """
        Format a caption for a meme to be sent to Telegram.
        
        Args:
            meme_data: Dictionary containing meme data
            
        Returns:
            str: Formatted caption
        """
        try:
            # Extract data
            text = meme_data.get('text', '')
            subject = meme_data.get('subject', '')
            description = meme_data.get('description', '')
            hashtags = meme_data.get('hashtags', [])
            
            # Format the message with Markdown
            caption = f"*🎭 L'ARROGANCE!*\n\n"
            
            if subject:
                caption += f"*Sujet:* {subject}\n\n"
                
            caption += f"*\"{text}\"*\n\n"
            
            if description:
                caption += f"{description}\n\n"
                
            if hashtags:
                caption += " ".join(hashtags)
            
            # Add quality score if available
            if 'quality_evaluation' in meme_data:
                caption += f"\n\n📊 *Score de qualité:* {meme_data['quality_evaluation']['overall_score']:.2f}/1"
            
            return caption
        except Exception as e:
            logger.error(f"Error formatting Telegram caption: {str(e)}")
            # Return a simple caption as fallback
            return f"*L'ARROGANCE!*\n\n\"{meme_data.get('text', '')}\"" 
    
    def format_batch_summary(self, results: List[Dict[str, Any]]) -> str:
        """
        Format a summary of batch meme generation for Telegram.
        
        Args:
            results: List of meme generation results
            
        Returns:
            str: Formatted summary
        """
        try:
            if not results:
                return "*Aucun mème généré*"
            
            summary = f"*📊 Résumé de la génération par lot*\n\n"
            summary += f"*Nombre de mèmes générés:* {len(results)}\n\n"
            
            # Add a brief summary of each meme
            for i, result in enumerate(results):
                text = result.get('text', '')
                subject = result.get('subject', '')
                
                summary += f"*{i+1}.* {subject}: \"{text[:50]}{'...' if len(text) > 50 else ''}\"\n"
            
            return summary
        except Exception as e:
            logger.error(f"Error formatting batch summary: {str(e)}")
            return f"*{len(results)} mèmes générés*" 