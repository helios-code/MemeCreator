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
            'data',
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
    
    # Scores moyens - Nous devons extraire les scores du JSON d'évaluation
    cursor.execute("SELECT evaluation, overall_score FROM punchlines")
    rows = cursor.fetchall()
    
    # Initialiser les compteurs pour les scores
    cruaute_total = 0
    provocation_total = 0
    pertinence_total = 0
    concision_total = 0
    impact_total = 0
    overall_total = 0
    valid_rows = 0
    
    # Calculer les moyennes
    for row in rows:
        try:
            evaluation = json.loads(row[0])
            cruaute_total += evaluation.get('cruaute', 0)
            provocation_total += evaluation.get('provocation', 0)
            pertinence_total += evaluation.get('pertinence', 0)
            concision_total += evaluation.get('concision', 0)
            impact_total += evaluation.get('impact', 0)
            overall_total += row[1]
            valid_rows += 1
        except (json.JSONDecodeError, TypeError):
            # Ignorer les lignes avec des données invalides
            pass
    
    # Calculer les moyennes
    avg_cruaute = cruaute_total / valid_rows if valid_rows > 0 else 0
    avg_provocation = provocation_total / valid_rows if valid_rows > 0 else 0
    avg_pertinence = pertinence_total / valid_rows if valid_rows > 0 else 0
    avg_concision = concision_total / valid_rows if valid_rows > 0 else 0
    avg_impact = impact_total / valid_rows if valid_rows > 0 else 0
    avg_overall = overall_total / valid_rows if valid_rows > 0 else 0
    
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
    print(f"Cruauté: {avg_cruaute:.2f}")
    print(f"Provocation: {avg_provocation:.2f}")
    print(f"Pertinence: {avg_pertinence:.2f}")
    print(f"Concision: {avg_concision:.2f}")
    print(f"Impact: {avg_impact:.2f}")
    print(f"Score global: {avg_overall:.2f}")
    
    print("\nSujets les plus fréquents:")
    for subject, count in top_subjects:
        print(f"- {subject}: {count} punchlines")
    
    conn.close()

if __name__ == "__main__":
    get_punchlines_stats() 