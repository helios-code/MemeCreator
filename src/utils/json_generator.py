#!/usr/bin/env python3
import os
import sys
import json
import asyncio
import argparse
import logging
from typing import List, Dict, Any, Optional

# Add the src directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from controllers.meme_controller import MemeController

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('json_generator')

async def generate_from_json(json_file: str, limit: int = 10, economy_mode: bool = False, send_to_telegram: Optional[bool] = None) -> List[Dict[str, Any]]:
    """
    Generate memes from subjects in a JSON file
    
    Args:
        json_file: Path to the JSON file containing subjects
        limit: Maximum number of memes to generate
        economy_mode: Whether to use economy mode
        send_to_telegram: Whether to send to Telegram
        
    Returns:
        List of generated meme results
    """
    # Load the JSON file
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        logger.error(f"❌ Error loading JSON file: {str(e)}")
        return []
    
    # Extract subjects from the JSON file
    subjects = []
    if isinstance(data, dict):
        # Try to find a list of subjects in the JSON
        for key, value in data.items():
            if isinstance(value, list) and len(value) > 0 and isinstance(value[0], str):
                subjects.extend(value)
                logger.info(f"Found {len(value)} subjects in key '{key}'")
                break
    elif isinstance(data, list) and len(data) > 0 and isinstance(data[0], str):
        # The JSON is directly a list of subjects
        subjects = data
        logger.info(f"Found {len(subjects)} subjects in JSON array")
    
    if not subjects:
        logger.error("❌ No subjects found in the JSON file")
        return []
    
    # Limit the number of subjects
    subjects = subjects[:limit]
    logger.info(f"🎬 Generating {len(subjects)} memes from JSON file")
    
    # Initialize the meme controller
    meme_controller = MemeController()
    
    # Generate memes
    results = await meme_controller.generate_batch_memes(
        subjects=subjects,
        economy_mode=economy_mode,
        send_to_telegram=send_to_telegram
    )
    
    return results

async def main():
    """
    Main function to parse command line arguments and generate memes from JSON
    """
    parser = argparse.ArgumentParser(description="Generate 'L'ARROGANCE!' memes from JSON file")
    
    parser.add_argument('--json', '-j', type=str, required=True,
                        help="Path to JSON file containing subjects")
    
    parser.add_argument('--limit', '-l', type=int, default=10,
                        help="Maximum number of memes to generate")
    
    parser.add_argument('--economy', '-e', action='store_true',
                        help="Enable economy mode (use GPT-3.5 instead of GPT-4)")
    
    parser.add_argument('--telegram', action='store_true',
                        help="Force sending to Telegram (overrides AUTO_SEND_TELEGRAM)")
    
    parser.add_argument('--no-telegram', dest='telegram', action='store_false',
                        help="Force not sending to Telegram (overrides AUTO_SEND_TELEGRAM)")
    
    parser.set_defaults(telegram=None)
    
    args = parser.parse_args()
    
    # Generate memes from JSON
    results = await generate_from_json(
        json_file=args.json,
        limit=args.limit,
        economy_mode=args.economy,
        send_to_telegram=args.telegram
    )
    
    # Print results
    if results:
        logger.info(f"✅ Generated {len(results)} memes successfully!")
        for i, result in enumerate(results, 1):
            logger.info(f"[{i}/{len(results)}] Subject: '{result['subject']}' - Video: {os.path.basename(result['video_path'])}")
    else:
        logger.error("❌ No memes were generated")

if __name__ == "__main__":
    asyncio.run(main()) 