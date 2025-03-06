#!/usr/bin/env python3
import asyncio
import sys
import logging
from controllers.meme_controller import MemeController

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('test_simple_mvc')

async def test_meme_controller(subject='Les développeurs'):
    """Test the MemeController by generating a meme with the given subject."""
    try:
        logger.info(f"Testing MemeController with subject: {subject}")
        controller = MemeController()
        result = await controller.generate_meme(subject=subject)
        
        logger.info(f"✅ Meme generated successfully!")
        logger.info(f"📝 Text: {result['text']}")
        logger.info(f"🎥 Video: {result['video_path']}")
        
        return result
    except Exception as e:
        logger.error(f"❌ MemeController test failed: {str(e)}")
        raise

if __name__ == "__main__":
    # Get subject from command line argument or use default
    subject = sys.argv[1] if len(sys.argv) > 1 else 'Les développeurs'
    
    # Run the test
    asyncio.run(test_meme_controller(subject)) 