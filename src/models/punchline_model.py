from typing import Dict, List, Any, Optional, Tuple
import os
import sqlite3
import json
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('punchline_model')

class PunchlineModel:
    """
    Model for handling punchline data and quality evaluation storage.
    """
    
    def __init__(self, db_path: str = None):
        """
        Initialize the punchline model with database connection.
        
        Args:
            db_path: Path to the database (default: data/quality_data.db)
        """
        # Set up database path
        if db_path is None:
            self.db_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                'data',
                'quality_data.db'
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
            
            # Create punchlines table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS punchlines (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text TEXT NOT NULL,
                subject TEXT NOT NULL,
                evaluation TEXT,
                overall_score REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                selected INTEGER DEFAULT 0
            )
            ''')
            
            conn.commit()
            conn.close()
            logger.info(f"Database initialized at {self.db_path}")
        except Exception as e:
            logger.error(f"Error initializing database: {str(e)}")
            raise
    
    def store_evaluation(self, punchline: str, subject: str, evaluation: Dict[str, float], overall_score: float) -> int:
        """
        Store a punchline evaluation in the database.
        
        Args:
            punchline: The punchline text
            subject: The subject of the punchline
            evaluation: Dictionary of evaluation criteria scores
            overall_score: The overall quality score
            
        Returns:
            int: ID of the stored evaluation
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Convert evaluation dict to JSON string
            evaluation_json = json.dumps(evaluation)
            
            # Insert into database
            cursor.execute(
                '''
                INSERT INTO punchlines (text, subject, evaluation, overall_score)
                VALUES (?, ?, ?, ?)
                ''',
                (punchline, subject, evaluation_json, overall_score)
            )
            
            punchline_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            logger.info(f"Punchline evaluation stored with ID {punchline_id}")
            return punchline_id
        except Exception as e:
            logger.error(f"Error storing punchline evaluation: {str(e)}")
            raise
    
    def mark_as_selected(self, punchline: str) -> bool:
        """
        Mark a punchline as selected (used in a meme).
        
        Args:
            punchline: The punchline text
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Update the selected status
            cursor.execute(
                'UPDATE punchlines SET selected = 1 WHERE text = ?',
                (punchline,)
            )
            
            affected_rows = cursor.rowcount
            conn.commit()
            conn.close()
            
            if affected_rows > 0:
                logger.info(f"Punchline marked as selected: '{punchline[:30]}...'")
                return True
            else:
                logger.warning(f"No punchline found to mark as selected: '{punchline[:30]}...'")
                return False
        except Exception as e:
            logger.error(f"Error marking punchline as selected: {str(e)}")
            return False
    
    def get_evaluation_stats(self) -> Dict[str, Any]:
        """
        Get statistics about punchline evaluations.
        
        Returns:
            Dict: Statistics about punchline evaluations
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get total count
            cursor.execute('SELECT COUNT(*) FROM punchlines')
            total_punchlines = cursor.fetchone()[0]
            
            # Get selected count
            cursor.execute('SELECT COUNT(*) FROM punchlines WHERE selected = 1')
            selected_punchlines = cursor.fetchone()[0]
            
            # Get average score
            cursor.execute('SELECT AVG(overall_score) FROM punchlines')
            average_score = cursor.fetchone()[0] or 0
            
            # Get average score of selected punchlines
            cursor.execute('SELECT AVG(overall_score) FROM punchlines WHERE selected = 1')
            average_selected_score = cursor.fetchone()[0] or 0
            
            # Get criteria averages
            criteria_averages = {}
            cursor.execute('SELECT evaluation FROM punchlines')
            rows = cursor.fetchall()
            
            if rows:
                # Get the first evaluation to determine criteria
                first_eval = json.loads(rows[0][0])
                criteria = first_eval.keys()
                
                # Initialize sums
                criteria_sums = {criterion: 0 for criterion in criteria}
                criteria_counts = {criterion: 0 for criterion in criteria}
                
                # Sum up all criteria values
                for row in rows:
                    evaluation = json.loads(row[0])
                    for criterion, value in evaluation.items():
                        if criterion in criteria_sums:
                            criteria_sums[criterion] += value
                            criteria_counts[criterion] += 1
                
                # Calculate averages
                for criterion in criteria:
                    if criteria_counts[criterion] > 0:
                        criteria_averages[criterion] = criteria_sums[criterion] / criteria_counts[criterion]
                    else:
                        criteria_averages[criterion] = 0
            
            conn.close()
            
            return {
                'total_punchlines': total_punchlines,
                'selected_punchlines': selected_punchlines,
                'average_score': average_score,
                'average_selected_score': average_selected_score,
                'criteria_averages': criteria_averages
            }
        except Exception as e:
            logger.error(f"Error getting evaluation stats: {str(e)}")
            return {
                'total_punchlines': 0,
                'selected_punchlines': 0,
                'average_score': 0,
                'average_selected_score': 0,
                'criteria_averages': {}
            }
    
    def export_punchlines_for_training(self, output_file: str = None) -> str:
        """
        Export punchlines for training purposes.
        
        Args:
            output_file: Path to the output file (default: data/training_data.json)
            
        Returns:
            str: Path to the exported file
        """
        try:
            if output_file is None:
                output_dir = os.path.join(
                    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                    'data'
                )
                os.makedirs(output_dir, exist_ok=True)
                output_file = os.path.join(output_dir, 'training_data.json')
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get all punchlines with their evaluations
            cursor.execute('''
                SELECT text, subject, evaluation, overall_score, selected
                FROM punchlines
                ORDER BY overall_score DESC
            ''')
            
            rows = cursor.fetchall()
            
            # Format the data
            training_data = []
            for row in rows:
                text, subject, evaluation_json, overall_score, selected = row
                evaluation = json.loads(evaluation_json)
                
                training_data.append({
                    'punchline': text,
                    'subject': subject,
                    'evaluation': evaluation,
                    'overall_score': overall_score,
                    'selected': bool(selected)
                })
            
            # Write to file
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(training_data, f, ensure_ascii=False, indent=2)
            
            conn.close()
            logger.info(f"Exported {len(training_data)} punchlines to {output_file}")
            
            return output_file
        except Exception as e:
            logger.error(f"Error exporting punchlines for training: {str(e)}")
            raise 