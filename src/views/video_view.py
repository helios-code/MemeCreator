from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('video_view')

class VideoView:
    """
    View for handling video rendering and display.
    """
    
    def render_video_with_text(self, template_path: str, text: str, output_path: str, font_config: dict) -> str:
        """
        Render a video with text overlay.
        
        Args:
            template_path: Path to the template video
            text: Text to overlay on the video
            output_path: Path to save the output video
            font_config: Font configuration dictionary
            
        Returns:
            str: Path to the rendered video
        """
        try:
            # Load the template video
            logger.info(f"Loading template video: {template_path}")
            video = VideoFileClip(template_path)
            
            # Verify the video has a valid duration
            if not hasattr(video, 'duration') or video.duration <= 0:
                raise ValueError(f"Video has no valid duration")
            
            # Create the text clip
            logger.info(f"Creating text clip with text: \"{text}\"")
            text_clip = self._create_text_clip(text, video.size, font_config)
            
            # Overlay the text on the video
            logger.info(f"Overlaying text on video...")
            final_clip = CompositeVideoClip([video, text_clip])
            
            # Set the duration of the final clip
            final_clip = final_clip.set_duration(video.duration)
            
            # Export the video
            logger.info(f"Exporting video to: {output_path}")
            final_clip.write_videofile(
                output_path,
                codec='libx264',
                audio_codec='aac',
                temp_audiofile='temp-audio.m4a',
                remove_temp=True
            )
            
            # Close the clips to free resources
            video.close()
            text_clip.close()
            final_clip.close()
            
            logger.info(f"Video rendered successfully: {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"Error rendering video: {str(e)}")
            import traceback
            traceback.print_exc()
            raise Exception(f"Error rendering video: {str(e)}")
    
    def _create_text_clip(self, text: str, video_size: tuple, font_config: dict) -> TextClip:
        """
        Create a text clip with background.
        
        Args:
            text: Text to display
            video_size: Size of the video (width, height)
            font_config: Font configuration dictionary
            
        Returns:
            TextClip: The text clip
        """
        try:
            width, height = video_size
            
            # Extract font configuration
            font = font_config.get('font', 'Arial')
            font_size = font_config.get('font_size', 40)
            text_color = font_config.get('text_color', 'white')
            text_bg = font_config.get('text_bg', 'black')
            text_position_y = font_config.get('text_position_y', 0.19)
            text_margin_x = font_config.get('text_margin_x', 0.02)
            
            # Calculate the y position of the text
            position_y = height * text_position_y
            
            # Calculate the text width with margins
            text_width = width * (1 - 2 * text_margin_x)
            
            # Create the text clip with background
            text_clip = TextClip(
                text,
                font=font,
                fontsize=font_size,
                color=text_color,
                bg_color=text_bg,
                method='caption',
                align='center',
                size=(text_width, None),
                stroke_color='black',
                stroke_width=1
            )
            
            # Position the text
            margin_x = width * text_margin_x
            text_clip = text_clip.set_position((margin_x, position_y))
            
            return text_clip
        except Exception as e:
            logger.error(f"Error creating text clip: {str(e)}")
            # Create an error text clip
            error_clip = TextClip(
                "Text Error",
                font='Arial',
                fontsize=40,
                color='red',
                bg_color='black',
                method='caption',
                align='center',
                size=(video_size[0] * 0.8, None)
            )
            error_clip = error_clip.set_position(('center', 50))
            return error_clip 