import os
import sqlite3
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

class PunchlineModel:
    """
    Modèle pour gérer les punchlines et leurs évaluations dans la base de données.
    """
    
    def __init__(self, db_path: str = None):
        """
        Initialise le modèle avec le chemin de la base de données.
        
        Args:
            db_path: Chemin vers la base de données SQLite (par défaut: data/quality_data.db)
        """
        # Chemin par défaut de la base de données
        if not db_path:
            db_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                'data',
                'quality_data.db'
            )
        
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """
        Initialise la base de données si elle n'existe pas.
        """
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Vérifier si la table existe déjà
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='punchlines'")
        if not cursor.fetchone():
            # Créer la table si elle n'existe pas
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
    
    def store_evaluation(
        self, 
        punchline: str, 
        subject: str, 
        evaluation: Dict[str, float], 
        overall_score: float
    ):
        """
        Stocke l'évaluation d'une punchline dans la base de données.
        
        Args:
            punchline: La punchline évaluée
            subject: Le sujet de la punchline
            evaluation: Les scores d'évaluation
            overall_score: Le score global
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Convertir l'évaluation en JSON pour le stockage
            evaluation_json = json.dumps(evaluation)
            
            # Insérer la punchline et son évaluation
            cursor.execute('''
            INSERT INTO punchlines (
                text, subject, evaluation, overall_score, created_at, selected
            ) VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                punchline,
                subject,
                evaluation_json,
                overall_score,
                datetime.now().isoformat(),
                0  # Non sélectionnée par défaut
            ))
            
            conn.commit()
            conn.close()
            
            logging.info(f"✅ Évaluation stockée pour la punchline: '{punchline[:30]}...'")
        
        except Exception as e:
            logging.error(f"❌ Erreur lors du stockage de l'évaluation: {str(e)}")
    
    def mark_as_selected(self, punchline: str):
        """
        Marque une punchline comme sélectionnée dans la base de données.
        
        Args:
            punchline: La punchline à marquer comme sélectionnée
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Marquer la punchline comme sélectionnée
            cursor.execute('''
            UPDATE punchlines SET selected = 1 WHERE text = ?
            ''', (punchline,))
            
            conn.commit()
            conn.close()
            
            logging.info(f"✅ Punchline marquée comme sélectionnée: '{punchline[:30]}...'")
        
        except Exception as e:
            logging.error(f"❌ Erreur lors du marquage de la punchline comme sélectionnée: {str(e)}")
    
    def get_evaluation_stats(self) -> Dict[str, Any]:
        """
        Récupère des statistiques sur les punchlines évaluées.
        
        Returns:
            Dict[str, Any]: Statistiques sur les punchlines
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Nombre total de punchlines
            cursor.execute("SELECT COUNT(*) FROM punchlines")
            total_punchlines = cursor.fetchone()[0]
            
            # Nombre de punchlines sélectionnées
            cursor.execute("SELECT COUNT(*) FROM punchlines WHERE selected = 1")
            selected_punchlines = cursor.fetchone()[0]
            
            # Score moyen global
            cursor.execute("SELECT AVG(overall_score) FROM punchlines")
            avg_score = cursor.fetchone()[0] or 0
            
            # Sujets les plus fréquents
            cursor.execute("SELECT subject, COUNT(*) FROM punchlines GROUP BY subject ORDER BY COUNT(*) DESC LIMIT 5")
            top_subjects = cursor.fetchall()
            
            # Récupérer les scores moyens des critères d'évaluation
            cursor.execute("SELECT evaluation FROM punchlines")
            evaluations = cursor.fetchall()
            
            conn.close()
            
            # Calculer les scores moyens pour chaque critère
            criteria_scores = {
                'cruaute': 0,
                'provocation': 0,
                'pertinence': 0,
                'concision': 0,
                'impact': 0
            }
            
            count = 0
            for eval_row in evaluations:
                try:
                    if eval_row[0]:
                        evaluation = json.loads(eval_row[0])
                        for criterion in criteria_scores:
                            if criterion in evaluation:
                                criteria_scores[criterion] += evaluation[criterion]
                        count += 1
                except:
                    pass
            
            # Calculer les moyennes
            if count > 0:
                for criterion in criteria_scores:
                    criteria_scores[criterion] /= count
            
            return {
                'total_punchlines': total_punchlines,
                'selected_punchlines': selected_punchlines,
                'selection_rate': selected_punchlines / total_punchlines if total_punchlines > 0 else 0,
                'avg_score': avg_score,
                'top_subjects': top_subjects,
                'criteria_scores': criteria_scores
            }
        
        except Exception as e:
            logging.error(f"❌ Erreur lors de la récupération des statistiques: {str(e)}")
            return {
                'total_punchlines': 0,
                'selected_punchlines': 0,
                'selection_rate': 0,
                'avg_score': 0,
                'top_subjects': [],
                'criteria_scores': {
                    'cruaute': 0,
                    'provocation': 0,
                    'pertinence': 0,
                    'concision': 0,
                    'impact': 0
                }
            }
    
    def export_punchlines_for_training(self, output_file: str = None) -> str:
        """
        Exporte les punchlines pour l'entraînement.
        
        Args:
            output_file: Chemin du fichier de sortie
            
        Returns:
            str: Chemin du fichier exporté
        """
        try:
            # Chemin par défaut du fichier de sortie
            if not output_file:
                output_dir = os.path.join(
                    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                    'output',
                    'exports'
                )
                os.makedirs(output_dir, exist_ok=True)
                output_file = os.path.join(output_dir, 'punchlines.jsonl')
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Récupérer toutes les punchlines avec leurs évaluations
            cursor.execute('''
            SELECT id, text, subject, evaluation, overall_score, created_at, selected
            FROM punchlines
            ORDER BY created_at DESC
            ''')
            
            rows = cursor.fetchall()
            conn.close()
            
            # Exporter les punchlines en format JSONL
            with open(output_file, 'w', encoding='utf-8') as f:
                for row in rows:
                    punchline_data = {
                        'id': row[0],
                        'text': row[1],
                        'subject': row[2],
                        'evaluation': json.loads(row[3]) if row[3] else {},
                        'overall_score': row[4],
                        'created_at': row[5],
                        'selected': bool(row[6])
                    }
                    f.write(json.dumps(punchline_data, ensure_ascii=False) + '\n')
            
            logging.info(f"✅ {len(rows)} punchlines exportées vers {output_file}")
            return output_file
        
        except Exception as e:
            logging.error(f"❌ Erreur lors de l'exportation des punchlines: {str(e)}")
            return None 