from models.video_model import VideoModel
from views.video_view import VideoView
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('video_controller')

class VideoController:
    """
    Controller for handling video processing logic.
    """
    
    def __init__(self):
        """Initialize the video controller with model and view."""
        self.model = VideoModel()
        self.view = VideoView()
        logger.info("Video controller initialized")
    
    async def create_meme(self, text: str) -> str:
        """
        Create a meme video by adding text to the template.
        
        Args:
            text: Text to add to the video
            
        Returns:
            str: Path to the generated video
        """
        try:
            # Get template path from model
            template_path = self.model.get_template_path()
            
            # Generate output filename
            output_filename = self.model.generate_output_filename()
            output_path = self.model.get_output_path(output_filename)
            
            # Get font configuration
            font_config = self.model.get_font_config()
            
            # Use view to render the video
            logger.info(f"Creating meme with text: \"{text}\"")
            result_path = self.view.render_video_with_text(
                template_path=template_path,
                text=text,
                output_path=output_path,
                font_config=font_config
            )
            
            logger.info(f"Meme created successfully: {result_path}")
            return result_path
        except Exception as e:
            logger.error(f"Error creating meme: {str(e)}")
            raise 