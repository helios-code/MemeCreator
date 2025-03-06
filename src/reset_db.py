#!/usr/bin/env python3
import os
import logging
import shutil
from models.meme_model import MemeModel
from models.punchline_model import PunchlineModel

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('reset_db')

def reset_databases():
    """Reset all databases by deleting and recreating them."""
    # Get database paths
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(project_root, 'data')
    meme_db_path = os.path.join(data_dir, 'meme_data.db')
    quality_db_path = os.path.join(data_dir, 'quality_data.db')
    
    # Delete existing databases
    for db_path in [meme_db_path, quality_db_path]:
        if os.path.exists(db_path):
            logger.info(f"Deleting existing database: {db_path}")
            os.remove(db_path)
    
    # Create backup directory
    backup_dir = os.path.join(project_root, 'data', 'backup')
    os.makedirs(backup_dir, exist_ok=True)
    
    # Initialize new databases
    logger.info("Initializing new meme database...")
    meme_model = MemeModel()
    
    logger.info("Initializing new punchline database...")
    punchline_model = PunchlineModel()
    
    logger.info("✅ Databases reset successfully!")

if __name__ == "__main__":
    reset_databases() 