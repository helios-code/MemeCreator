#!/usr/bin/env python3
import os
import json
import sqlite3
from datetime import datetime

def export_punchlines(output_file=None):
    """
    Exporte toutes les punchlines de la base de données en format JSONL
    
    Args:
        output_file: Chemin du fichier de sortie (par défaut: output/punchlines.jsonl)
    
    Returns:
        Le chemin du fichier exporté
    """
    # Chemin de la base de données
    db_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        'data',
        'quality_data.db'
    )
    
    # Vérifier si la base de données existe
    if not os.path.exists(db_path):
        print(f"❌ La base de données {db_path} n'existe pas.")
        return None
    
    # Chemin du fichier de sortie
    if not output_file:
        output_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            'output',
            'exports'
        )
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, 'punchlines.jsonl')
    
    # Connexion à la base de données
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Récupérer les noms des colonnes
    cursor.execute("PRAGMA table_info(punchlines)")
    columns = [column[1] for column in cursor.fetchall()]
    
    # Récupérer toutes les punchlines avec leurs scores
    cursor.execute(f"SELECT * FROM punchlines ORDER BY timestamp DESC")
    
    rows = cursor.fetchall()
    conn.close()
    
    # Exporter les punchlines en format JSONL
    with open(output_file, 'w', encoding='utf-8') as f:
        for row in rows:
            punchline_data = {columns[i]: row[i] for i in range(len(row))}
            f.write(json.dumps(punchline_data, ensure_ascii=False) + '\n')
    
    print(f"✅ {len(rows)} punchlines exportées vers {output_file}")
    return output_file

if __name__ == "__main__":
    export_punchlines() 