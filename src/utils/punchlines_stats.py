#!/usr/bin/env python3
import os
import json
import sqlite3
from collections import Counter

def get_punchlines_stats(db_path=None):
    """
    Récupère et affiche des statistiques sur les punchlines stockées
    
    Args:
        db_path: Chemin de la base de données (par défaut: output/quality_data.db)
    """
    # Chemin de la base de données
    if not db_path:
        db_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            'output',
            'quality_data.db'
        )
    
    # Vérifier si la base de données existe
    if not os.path.exists(db_path):
        print(f"❌ La base de données {db_path} n'existe pas.")
        return
    
    # Connexion à la base de données
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Nombre total de punchlines
    cursor.execute("SELECT COUNT(*) FROM punchlines")
    total_punchlines = cursor.fetchone()[0]
    
    # Nombre de punchlines sélectionnées
    cursor.execute("SELECT COUNT(*) FROM punchlines WHERE selected = 1")
    selected_punchlines = cursor.fetchone()[0]
    
    # Scores moyens
    cursor.execute("""
        SELECT 
            AVG(originality), 
            AVG(humor), 
            AVG(relevance), 
            AVG(conciseness), 
            AVG(impact), 
            AVG(overall_score)
        FROM punchlines
    """)
    avg_scores = cursor.fetchone()
    
    # Sujets les plus fréquents
    cursor.execute("SELECT subject FROM punchlines")
    subjects = [row[0] for row in cursor.fetchall()]
    subject_counter = Counter(subjects)
    top_subjects = subject_counter.most_common(5)
    
    # Afficher les statistiques
    print("\n📊 Statistiques des punchlines:")
    print(f"Total: {total_punchlines} punchlines")
    print(f"Sélectionnées: {selected_punchlines} ({selected_punchlines/total_punchlines*100:.1f}% du total)")
    
    print("\nScores moyens:")
    print(f"Originalité: {avg_scores[0]:.2f}")
    print(f"Humour: {avg_scores[1]:.2f}")
    print(f"Pertinence: {avg_scores[2]:.2f}")
    print(f"Concision: {avg_scores[3]:.2f}")
    print(f"Impact: {avg_scores[4]:.2f}")
    print(f"Score global: {avg_scores[5]:.2f}")
    
    print("\nSujets les plus fréquents:")
    for subject, count in top_subjects:
        print(f"- {subject}: {count} punchlines")
    
    conn.close()

if __name__ == "__main__":
    get_punchlines_stats() 