#!/usr/bin/env python3
import os
import sys
import json
import asyncio
import getpass
from dotenv import load_dotenv, set_key
import datetime
import logging
from typing import Dict, List, Optional, Any, Union
import argparse

# Add the src directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from controllers.meme_controller import MemeController

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('meme_generator')

# Load environment variables
load_dotenv()

# Default text if OpenAI is not configured
DEFAULT_TEXT = "Quand le dev junior déploie son code sans tests"

# Environment file path
ENV_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')

async def ensure_openai_api_key() -> str:
    """
    Ensures a valid OpenAI API key is configured
    
    Returns:
        str: The OpenAI API key
    """
    api_key = os.getenv('OPENAI_API_KEY')
    
    if not api_key or api_key == 'your_openai_api_key_here' or 'your_' in api_key:
        logger.warning("⚠️ No valid OpenAI API key found in .env file")
        logger.info("To generate punchlines, you must provide a valid OpenAI API key.")
        api_key = getpass.getpass("Enter your OpenAI API key: ")
        
        if not api_key:
            raise ValueError("No OpenAI API key provided. Cannot generate a punchline.")
        
        # Update .env file with the new API key
        set_key(ENV_PATH, 'OPENAI_API_KEY', api_key)
        os.environ['OPENAI_API_KEY'] = api_key
        logger.info("✅ OpenAI API key saved to .env file")
    
    return api_key

async def generate_meme(args):
    """
    Generate a meme with the given arguments
    
    Args:
        args: Command line arguments
    """
    try:
        # Initialize the meme controller
        meme_controller = MemeController()
        
        if args.batch:
            # Generate multiple memes from a list of subjects
            subjects = args.subject.split(',')
            print(f"🎬 Generating {len(subjects)} memes in batch mode...")
            
            results = await meme_controller.generate_batch_memes(
                subjects=subjects,
                economy_mode=args.economy,
                send_to_telegram=args.telegram
            )
            
            print(f"✅ Generated {len(results)} memes successfully!")
            
        else:
            # Generate a single meme
            print(f"🎬 Generating a meme on subject: '{args.subject}'...")
            
            result = await meme_controller.generate_meme(
                custom_text=args.text,
                subject=args.subject,
                economy_mode=args.economy,
                send_to_telegram=args.telegram
            )
            
            print(f"✅ Meme generated successfully!")
            print(f"📝 Text: {result['text']}")
            print(f"🎥 Video: {result['video_path']}")
            
    except Exception as e:
        print(f"❌ Error generating meme: {str(e)}")
        sys.exit(1)

def main():
    """
    Main function to parse command line arguments and generate memes
    """
    parser = argparse.ArgumentParser(description="Generate 'L'ARROGANCE!' memes")
    
    parser.add_argument('--subject', '-s', type=str, default="L'arrogance des développeurs",
                        help="Subject for the meme (or comma-separated list in batch mode)")
    
    parser.add_argument('--text', '-t', type=str, default=None,
                        help="Custom text to use instead of generating a punchline")
    
    parser.add_argument('--economy', '-e', action='store_true',
                        help="Enable economy mode (use GPT-3.5 instead of GPT-4)")
    
    parser.add_argument('--telegram', action='store_true',
                        help="Force sending to Telegram (overrides AUTO_SEND_TELEGRAM)")
    
    parser.add_argument('--no-telegram', dest='telegram', action='store_false',
                        help="Force not sending to Telegram (overrides AUTO_SEND_TELEGRAM)")
    
    parser.add_argument('--batch', '-b', action='store_true',
                        help="Batch mode: generate multiple memes from a comma-separated list of subjects")
    
    parser.set_defaults(telegram=None)
    
    args = parser.parse_args()
    
    # Run the generate_meme function asynchronously
    asyncio.run(generate_meme(args))

if __name__ == "__main__":
    main() 