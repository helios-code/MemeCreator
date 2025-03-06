#!/usr/bin/env python3
import os
import json
import sqlite3
from collections import Counter
from datetime import datetime

def get_meme_stats(db_path=None):
    """
    Récupère et affiche des statistiques sur les mèmes générés
    
    Args:
        db_path: Chemin de la base de données (par défaut: data/meme_data.db)
    """
    # Chemin de la base de données
    if not db_path:
        db_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            'data',
            'meme_data.db'
        )
    
    # Vérifier si la base de données existe
    if not os.path.exists(db_path):
        print(f"❌ La base de données {db_path} n'existe pas.")
        return
    
    # Connexion à la base de données
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Nombre total de mèmes
    cursor.execute("SELECT COUNT(*) FROM memes")
    total_memes = cursor.fetchone()[0]
    
    # Score moyen de qualité
    cursor.execute("SELECT AVG(quality_score) FROM memes")
    avg_quality = cursor.fetchone()[0] or 0
    
    # Sujets les plus fréquents
    cursor.execute("SELECT subject FROM memes")
    subjects = [row[0] for row in cursor.fetchall()]
    subject_counter = Counter(subjects)
    top_subjects = subject_counter.most_common(5)
    
    # Mèmes par jour
    cursor.execute("SELECT created_at FROM memes")
    dates = [row[0].split(' ')[0] if ' ' in row[0] else row[0] for row in cursor.fetchall()]
    date_counter = Counter(dates)
    
    # Mèmes les plus récents
    cursor.execute("""
        SELECT id, subject, text, quality_score, created_at 
        FROM memes 
        ORDER BY created_at DESC 
        LIMIT 5
    """)
    recent_memes = cursor.fetchall()
    
    # Afficher les statistiques
    print("\n📊 Statistiques des mèmes:")
    print(f"Total: {total_memes} mèmes générés")
    print(f"Score de qualité moyen: {avg_quality:.2f}")
    
    print("\nSujets les plus fréquents:")
    for subject, count in top_subjects:
        print(f"- {subject}: {count} mèmes")
    
    print("\nActivité de génération:")
    for date, count in sorted(date_counter.items(), key=lambda x: x[0], reverse=True)[:7]:
        print(f"- {date}: {count} mèmes")
    
    print("\nMèmes récents:")
    for meme in recent_memes:
        meme_id, subject, text, score, date = meme
        print(f"- ID {meme_id}: '{subject}' ({date}) - Score: {score:.2f}")
        print(f"  \"{text[:50]}...\"")
    
    conn.close()

if __name__ == "__main__":
    get_meme_stats() 