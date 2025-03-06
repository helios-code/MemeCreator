import os
import uuid
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('video_model')

class VideoModel:
    """
    Model for handling video-related data and operations.
    """
    
    def __init__(self):
        """Initialize the video model with paths and configuration."""
        # Get the absolute path of the current directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(current_dir))
        
        # Template path - check multiple possible locations
        template_paths = [
            os.path.join(os.path.dirname(current_dir), '..', 'data', 'template.mp4'),  # /data/template.mp4
            os.path.join(os.path.dirname(current_dir), 'data', 'template.mp4'),        # /src/data/template.mp4
            os.path.join(os.path.dirname(current_dir), '..', 'src', 'data', 'template.mp4')  # /src/data/template.mp4 (from project root)
        ]
        
        # Try each path until we find one that exists
        self.template_path = None
        for path in template_paths:
            if os.path.exists(path):
                self.template_path = path
                break
        
        # If no template found, use environment variable or raise error
        if not self.template_path:
            env_path = os.getenv('TEMPLATE_VIDEO_PATH')
            if env_path and os.path.exists(env_path):
                self.template_path = env_path
            else:
                raise FileNotFoundError(f"Template file not found in any of the expected locations: {template_paths}")
        
        # Output directory
        output_dir_env = os.getenv('OUTPUT_DIRECTORY', 'output')
        if not os.path.isabs(output_dir_env):
            self.output_dir = os.path.join(project_root, output_dir_env, 'videos')
        else:
            self.output_dir = os.path.join(output_dir_env, 'videos')
        
        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Font configuration
        self.font = os.getenv('FONT_PATH', 'Arial')
        self.font_size = int(os.getenv('FONT_SIZE', '40'))
        self.text_color = os.getenv('TEXT_COLOR', 'white')
        self.text_position_y = 0.19  # Fixed position at 19% of height
        self.text_margin_x = float(os.getenv('TEXT_MARGIN_X', '0.02'))
        self.text_bg = os.getenv('TEXT_BACKGROUND', 'black')
        
        logger.info(f"Video model initialized with template: {self.template_path}")
        logger.info(f"Output directory: {self.output_dir}")
    
    def get_template_path(self) -> str:
        """
        Get the path to the template video.
        
        Returns:
            str: Path to the template video
        """
        return self.template_path
    
    def get_output_directory(self) -> str:
        """
        Get the output directory for generated videos.
        
        Returns:
            str: Path to the output directory
        """
        return self.output_dir
    
    def get_font_config(self) -> dict:
        """
        Get the font configuration for text rendering.
        
        Returns:
            dict: Font configuration
        """
        return {
            'font': self.font,
            'font_size': self.font_size,
            'text_color': self.text_color,
            'text_position_y': self.text_position_y,
            'text_margin_x': self.text_margin_x,
            'text_bg': self.text_bg
        }
    
    def generate_output_filename(self) -> str:
        """
        Generate a unique filename for the output video.
        
        Returns:
            str: Generated filename
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_id = str(uuid.uuid4())[:8]
        return f"arrogance_meme_{timestamp}_{unique_id}.mp4"
    
    def get_output_path(self, filename: str = None) -> str:
        """
        Get the full path for an output video.
        
        Args:
            filename: Optional filename (if None, generates one)
            
        Returns:
            str: Full path to the output file
        """
        if filename is None:
            filename = self.generate_output_filename()
        
        return os.path.join(self.output_dir, filename) 