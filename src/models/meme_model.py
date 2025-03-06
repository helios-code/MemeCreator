from typing import Dict, List, Any, Optional
import os
import sqlite3
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('meme_model')

class MemeModel:
    """
    Model for handling meme data and database operations.
    """
    
    def __init__(self, db_path: str = None):
        """
        Initialize the meme model with database connection.
        
        Args:
            db_path: Path to the database (default: data/meme_data.db)
        """
        # Set up database path
        if db_path is None:
            self.db_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                'data',
                'meme_data.db'
            )
        else:
            self.db_path = db_path
            
        # Initialize database
        self._init_database()
    
    def _init_database(self):
        """Initialize the database with required tables if they don't exist."""
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            
            # Connect to database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create memes table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS memes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text TEXT NOT NULL,
                subject TEXT,
                video_path TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                quality_score REAL,
                hashtags TEXT,
                description TEXT
            )
            ''')
            
            conn.commit()
            conn.close()
            logger.info(f"Database initialized at {self.db_path}")
        except Exception as e:
            logger.error(f"Error initializing database: {str(e)}")
            raise
    
    def save_meme(self, meme_data: Dict[str, Any]) -> int:
        """
        Save a meme to the database.
        
        Args:
            meme_data: Dictionary containing meme data
            
        Returns:
            int: ID of the saved meme
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Extract data
            text = meme_data.get('text', '')
            subject = meme_data.get('subject', '')
            video_path = meme_data.get('video_path', '')
            quality_score = None
            
            if 'quality_evaluation' in meme_data:
                quality_score = meme_data['quality_evaluation'].get('overall_score')
                
            hashtags = ','.join(meme_data.get('hashtags', []))
            description = meme_data.get('description', '')
            
            # Insert into database
            cursor.execute(
                '''
                INSERT INTO memes (text, subject, video_path, quality_score, hashtags, description)
                VALUES (?, ?, ?, ?, ?, ?)
                ''',
                (text, subject, video_path, quality_score, hashtags, description)
            )
            
            meme_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            logger.info(f"Meme saved to database with ID {meme_id}")
            return meme_id
        except Exception as e:
            logger.error(f"Error saving meme to database: {str(e)}")
            raise
    
    def get_meme(self, meme_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a meme from the database by ID.
        
        Args:
            meme_id: ID of the meme to retrieve
            
        Returns:
            Dict or None: Meme data if found, None otherwise
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM memes WHERE id = ?', (meme_id,))
            row = cursor.fetchone()
            
            if row:
                meme_data = dict(row)
                # Convert hashtags back to list
                if meme_data.get('hashtags'):
                    meme_data['hashtags'] = meme_data['hashtags'].split(',')
                else:
                    meme_data['hashtags'] = []
                    
                conn.close()
                return meme_data
            
            conn.close()
            return None
        except Exception as e:
            logger.error(f"Error retrieving meme from database: {str(e)}")
            raise
    
    def get_all_memes(self) -> List[Dict[str, Any]]:
        """
        Get all memes from the database.
        
        Returns:
            List[Dict]: List of meme data dictionaries
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM memes ORDER BY created_at DESC')
            rows = cursor.fetchall()
            
            memes = []
            for row in rows:
                meme_data = dict(row)
                # Convert hashtags back to list
                if meme_data.get('hashtags'):
                    meme_data['hashtags'] = meme_data['hashtags'].split(',')
                else:
                    meme_data['hashtags'] = []
                memes.append(meme_data)
            
            conn.close()
            return memes
        except Exception as e:
            logger.error(f"Error retrieving all memes from database: {str(e)}")
            raise 