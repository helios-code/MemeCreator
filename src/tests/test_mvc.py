#!/usr/bin/env python3
"""
Test script for the MVC architecture.
This script tests the basic functionality of the MVC architecture.
"""

import os
import sys
import asyncio
import logging
from typing import Dict, List, Any, Optional

# Add the src directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from controllers.meme_controller import MemeController
from controllers.punchline_controller import PunchlineController
from controllers.video_controller import VideoController
from models.meme_model import MemeModel
from models.punchline_model import PunchlineModel
from models.video_model import VideoModel
from views.video_view import VideoView
from views.telegram_view import TelegramView

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('test_mvc')

async def test_meme_controller(subject: str = "L'arrogance des développeurs") -> None:
    """
    Test the MemeController.
    
    Args:
        subject: The subject to generate a meme about
    """
    logger.info(f"🧪 Testing MemeController with subject: {subject}")
    
    try:
        # Initialize the controller
        controller = MemeController()
        
        # Generate a meme
        result = await controller.generate_meme(subject=subject)
        
        # Verify the result
        assert 'text' in result, "Result should contain 'text'"
        assert 'video_path' in result, "Result should contain 'video_path'"
        assert os.path.exists(result['video_path']), f"Video file {result['video_path']} should exist"
        
        logger.info(f"✅ MemeController test passed!")
        logger.info(f"📝 Generated text: {result['text']}")
        logger.info(f"🎥 Video path: {result['video_path']}")
        
        return result
    except Exception as e:
        logger.error(f"❌ MemeController test failed: {str(e)}")
        raise

async def test_punchline_controller(subject: str = "L'arrogance des développeurs") -> None:
    """
    Test the PunchlineController.
    
    Args:
        subject: The subject to generate a punchline about
    """
    logger.info(f"🧪 Testing PunchlineController with subject: {subject}")
    
    try:
        # Initialize the controller
        controller = PunchlineController()
        
        # Generate a punchline
        text, metadata = await controller.get_best_punchline(subject=subject)
        
        # Verify the result
        assert text, "Punchline should not be empty"
        assert 'overall_score' in metadata, "Metadata should contain 'overall_score'"
        assert 'evaluation' in metadata, "Metadata should contain 'evaluation'"
        
        logger.info(f"✅ PunchlineController test passed!")
        logger.info(f"📝 Generated punchline: {text}")
        logger.info(f"📊 Overall score: {metadata['overall_score']:.2f}")
        
        return text, metadata
    except Exception as e:
        logger.error(f"❌ PunchlineController test failed: {str(e)}")
        raise

async def test_video_controller(text: str = "Test text for video") -> None:
    """
    Test the VideoController.
    
    Args:
        text: The text to add to the video
    """
    logger.info(f"🧪 Testing VideoController with text: {text}")
    
    try:
        # Initialize the controller
        controller = VideoController()
        
        # Create a meme video
        output_path = await controller.create_meme(text)
        
        # Verify the result
        assert output_path, "Output path should not be empty"
        assert os.path.exists(output_path), f"Video file {output_path} should exist"
        
        logger.info(f"✅ VideoController test passed!")
        logger.info(f"🎥 Video path: {output_path}")
        
        return output_path
    except Exception as e:
        logger.error(f"❌ VideoController test failed: {str(e)}")
        raise

async def test_models() -> None:
    """Test the models."""
    logger.info(f"🧪 Testing models")
    
    try:
        # Test MemeModel
        meme_model = MemeModel()
        
        # Test VideoModel
        video_model = VideoModel()
        template_path = video_model.get_template_path()
        assert os.path.exists(template_path), f"Template file {template_path} should exist"
        
        # Test PunchlineModel
        punchline_model = PunchlineModel()
        
        logger.info(f"✅ Models test passed!")
    except Exception as e:
        logger.error(f"❌ Models test failed: {str(e)}")
        raise

async def test_views() -> None:
    """Test the views."""
    logger.info(f"🧪 Testing views")
    
    try:
        # Test VideoView
        video_view = VideoView()
        
        # Test TelegramView
        telegram_view = TelegramView()
        
        logger.info(f"✅ Views test passed!")
    except Exception as e:
        logger.error(f"❌ Views test failed: {str(e)}")
        raise

async def run_all_tests(subject: str = "L'arrogance des développeurs") -> None:
    """
    Run all tests.
    
    Args:
        subject: The subject to use for tests
    """
    logger.info(f"🧪 Running all MVC tests with subject: {subject}")
    
    try:
        # Test models
        await test_models()
        
        # Test views
        await test_views()
        
        # Test controllers
        text, metadata = await test_punchline_controller(subject)
        output_path = await test_video_controller(text)
        result = await test_meme_controller(subject)
        
        logger.info(f"✅ All MVC tests passed!")
    except Exception as e:
        logger.error(f"❌ Some tests failed: {str(e)}")
        raise

if __name__ == "__main__":
    # Get subject from command line arguments
    subject = sys.argv[1] if len(sys.argv) > 1 else "L'arrogance des développeurs"
    
    # Run all tests
    asyncio.run(run_all_tests(subject)) 