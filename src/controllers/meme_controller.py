from models.meme_model import MemeModel
from controllers.video_controller import VideoController
from controllers.punchline_controller import PunchlineController
from views.telegram_view import TelegramView
from typing import Dict, List, Any, Optional
import logging
import os
from clients.telegram_client import TelegramClient
from clients.openai_client import OpenAIClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('meme_controller')

class MemeController:
    """
    Controller for handling meme generation and management.
    """
    
    def __init__(self):
        """Initialize the meme controller with models, views, and clients."""
        # Initialize models
        self.meme_model = MemeModel()
        
        # Initialize controllers
        self.video_controller = VideoController()
        self.punchline_controller = PunchlineController()
        
        # Initialize views
        self.telegram_view = TelegramView()
        
        # Initialize clients
        self.telegram_client = TelegramClient()
        self.openai_client = OpenAIClient()
        
        # Check if quality pipeline is enabled
        self.use_quality_pipeline = os.getenv('USE_QUALITY_PIPELINE', 'true').lower() == 'true'
        
        if self.use_quality_pipeline:
            logger.info("🔍 Quality pipeline enabled for punchline generation")
        else:
            logger.info("🔍 Quality pipeline disabled (using simple generation)")
            
        logger.info("Meme controller initialized")
    
    async def generate_meme(
        self, 
        custom_text: Optional[str] = None, 
        subject: Optional[str] = None, 
        economy_mode: Optional[bool] = None, 
        send_to_telegram: Optional[bool] = None
    ) -> Dict[str, Any]:
        """
        Generate a meme video with the following steps:
        1. Generate a punchline with OpenAI GPT-4 (if custom_text is not provided)
        2. Add the punchline to the video template
        3. Export the video with the embedded text
        4. Generate hashtags and a description for social media
        5. Send the video to Telegram (if configured)
        
        Args:
            custom_text: Custom text to use instead of generating a punchline
            subject: The subject to generate a punchline about
            economy_mode: Enable token economy mode
            send_to_telegram: Force sending or not sending to Telegram
            
        Returns:
            Dict: Information about the generated meme (text and file path)
        """
        try:
            # Step 1: Generate a punchline (if needed)
            if custom_text:
                text = custom_text
                punchline_metadata = None
            else:
                # Use quality pipeline or simple generation based on configuration
                if self.use_quality_pipeline:
                    logger.info(f"🔍 Generating punchlines with quality pipeline for subject: '{subject or self.openai_client.default_subject}'")
                    text, punchline_metadata = await self.punchline_controller.get_best_punchline(
                        subject=subject or self.openai_client.default_subject,
                        economy_mode=economy_mode
                    )
                    
                    # Display evaluation scores
                    if punchline_metadata and "evaluation" in punchline_metadata:
                        eval_scores = punchline_metadata["evaluation"]
                        logger.info(f"📊 Evaluation scores: Cruelty={eval_scores['cruaute']:.2f}, "
                                   f"Provocation={eval_scores['provocation']:.2f}, Relevance={eval_scores['pertinence']:.2f}, "
                                   f"Conciseness={eval_scores['concision']:.2f}, Impact={eval_scores['impact']:.2f}")
                        logger.info(f"📊 Overall score: {punchline_metadata['overall_score']:.2f}")
                else:
                    # Use the predefined prompt in OpenAIClient with the specified subject
                    text = await self.openai_client.generate_punchline(subject=subject, economy_mode=economy_mode)
                    punchline_metadata = None
            
            # Step 2 & 3: Add the text to the video and export it
            output_path = await self.video_controller.create_meme(text)
            
            # Determine the final subject (provided or default)
            final_subject = subject if subject else self.openai_client.default_subject
            
            # Create the basic result
            result = {
                "text": text,
                "video_path": output_path,
                "subject": final_subject
            }
            
            # Add evaluation metadata if available
            if punchline_metadata:
                result["quality_evaluation"] = {
                    "overall_score": punchline_metadata["overall_score"],
                    "criteria_scores": punchline_metadata["evaluation"]
                }
            
            # Step 4: Generate hashtags and a description for social media
            try:
                # Generate hashtags
                hashtags = await self.openai_client.generate_hashtags(final_subject, text, economy_mode)
                result["hashtags"] = hashtags
                
                # Generate description
                description = await self.openai_client.generate_description(final_subject, text, economy_mode)
                result["description"] = description
                
                logger.info(f"✅ Social content generated successfully!")
                logger.info(f"📝 Hashtags: {' '.join(hashtags)}")
                logger.info(f"📝 Description: {description}")
            except Exception as e:
                logger.error(f"⚠️ Error generating social content: {str(e)}")
                # Use default values
                result["hashtags"] = ["#LARROGANCE", "#meme", "#humour"]
                result["description"] = f"A satirical look at {final_subject}."
            
            # Save the meme to the database
            self.meme_model.save_meme(result)
            
            # Step 5: Send the video to Telegram if configured
            should_send = send_to_telegram if send_to_telegram is not None else self.telegram_client.auto_send
            if should_send:
                # Create a complete message with the subject, punchline, description, and hashtags
                caption = self.telegram_view.format_meme_caption(result)
                
                await self.telegram_client.send_video(output_path, caption)
            
            return result
        except Exception as e:
            logger.error(f"❌ Error generating meme: {str(e)}")
            raise e
    
    async def generate_batch_memes(
        self, 
        subjects: List[str], 
        economy_mode: Optional[bool] = None, 
        send_to_telegram: Optional[bool] = None
    ) -> List[Dict[str, Any]]:
        """
        Generate multiple memes from a list of subjects.
        
        Args:
            subjects: List of subjects
            economy_mode: Enable token economy mode
            send_to_telegram: Force sending or not sending to Telegram
            
        Returns:
            List[Dict]: List of meme generation results
        """
        results = []
        # Determine if we should send videos to Telegram
        should_send = send_to_telegram if send_to_telegram is not None else self.telegram_client.auto_send
        
        for i, subject in enumerate(subjects):
            try:
                logger.info(f"\n[{i+1}/{len(subjects)}] 🤖 Generating a meme on the subject: \"{subject}\"")
                
                # Display the mode used
                if economy_mode:
                    logger.info("💰 Economy mode enabled: using GPT-3.5-turbo with a simplified prompt")
                
                # Generate the meme and send it immediately to Telegram if configured
                result = await self.generate_meme(subject=subject, economy_mode=economy_mode, send_to_telegram=should_send)
                
                logger.info(f"✅ Meme generated successfully!")
                logger.info(f"📝 Text: {result['text']}")
                logger.info(f"🎥 Video: {result['video_path']}")
                
                results.append(result)
            except Exception as e:
                logger.error(f"❌ Error generating meme for subject '{subject}': {str(e)}")
                # Continue with the next subject
        
        # If quality pipeline is enabled, display global statistics
        if self.use_quality_pipeline:
            try:
                stats = self.punchline_controller.get_evaluation_stats()
                logger.info("\n📊 Quality pipeline statistics:")
                logger.info(f"Total punchlines evaluated: {stats['total_punchlines']}")
                logger.info(f"Selected punchlines: {stats['selected_punchlines']}")
                logger.info(f"Average overall score: {stats['average_score']:.2f}")
                logger.info(f"Average score of selected punchlines: {stats['average_selected_score']:.2f}")
            except Exception as e:
                logger.error(f"❌ Error retrieving statistics: {str(e)}")
        
        return results 