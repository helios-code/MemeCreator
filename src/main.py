import os
import asyncio
from dotenv import load_dotenv

from controllers.meme_controller import MemeController

# Load environment variables
load_dotenv()

# Default subject for punchline generation
DEFAULT_SUBJECT = "L'arrogance des développeurs"

async def main():
    """
    Main function that generates an 'L'ARROGANCE!' video meme on each execution
    """
    try:
        print("🎬 Starting 'L'ARROGANCE!' meme generator...")
        
        # Initialize the meme controller
        meme_controller = MemeController()
        
        # Generate the meme with the default subject
        result = await meme_controller.generate_meme(subject=DEFAULT_SUBJECT)
        
        print(f"✅ Meme generated successfully!")
        print(f"📝 Text: {result['text']}")
        print(f"🎥 Video: {result['video_path']}")
        
        return result
    except Exception as e:
        print(f"❌ Error generating meme: {str(e)}")
        raise e

if __name__ == "__main__":
    # Run the main function asynchronously
    result = asyncio.run(main()) 