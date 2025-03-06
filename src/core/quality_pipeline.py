import os
import json
import logging
from typing import List, Dict, Any, Optional, Tuple
from openai import OpenAI
from dotenv import load_dotenv
import sqlite3
from datetime import datetime
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('quality_pipeline')

# Load environment variables
load_dotenv()

class QualityPipeline:
    """
    Pipeline de qualité pour évaluer et filtrer les punchlines générées
    """
    
    def __init__(self, db_path: str = None):
        """
        Initialise la pipeline de qualité
        
        Args:
            db_path: Chemin vers la base de données (par défaut: output/quality_data.db)
        """
        # Charger les variables d'environnement
        load_dotenv()
        
        # Configurer le logger
        self.logger = logging.getLogger('quality_pipeline')
        
        # Chemin de la base de données
        if db_path is None:
            self.db_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                'data',
                'quality_data.db'
            )
        else:
            self.db_path = db_path
        
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.client = OpenAI(api_key=self.api_key)
        
        # Seuils de qualité (configurables)
        self.quality_threshold = float(os.getenv('QUALITY_THRESHOLD', '0.7'))  # Seuil par défaut: 0.7
        self.num_candidates = int(os.getenv('NUM_PUNCHLINE_CANDIDATES', '3'))  # Nombre de punchlines à générer
        
        self._init_database()
        
        logger.info(f"🔍 Pipeline de qualité initialisée (seuil: {self.quality_threshold}, candidats: {self.num_candidates})")
    
    def _init_database(self):
        """Initialise la base de données SQLite pour stocker les évaluations"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Table pour les punchlines évaluées
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS punchlines (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT NOT NULL,
            subject TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            originality REAL,
            humor REAL,
            relevance REAL,
            conciseness REAL,
            impact REAL,
            overall_score REAL,
            selected BOOLEAN DEFAULT 0,
            feedback TEXT
        )
        ''')
        
        conn.commit()
        conn.close()
    
    async def generate_and_evaluate_punchlines(
        self, 
        subject: str, 
        economy_mode: bool = False,
        num_candidates: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Génère plusieurs punchlines candidates et les évalue
        
        Args:
            subject: Le sujet sur lequel générer des punchlines
            economy_mode: Utiliser le mode économie de tokens
            num_candidates: Nombre de punchlines à générer (utilise la valeur par défaut si None)
            
        Returns:
            Liste des punchlines évaluées, triées par score de qualité (meilleure en premier)
        """
        # Utiliser le nombre de candidats spécifié ou la valeur par défaut
        n_candidates = num_candidates or self.num_candidates
        
        # Générer plusieurs punchlines candidates
        candidates = await self._generate_candidate_punchlines(subject, n_candidates, economy_mode)
        
        # Évaluer chaque punchline
        evaluated_punchlines = []
        for punchline in candidates:
            evaluation = await self._evaluate_punchline(subject, punchline)
            
            # Calculer le score global
            overall_score = self._calculate_overall_score(evaluation)
            
            # Créer l'objet punchline évaluée
            evaluated_punchline = {
                "text": punchline,
                "subject": subject,
                "evaluation": evaluation,
                "overall_score": overall_score
            }
            
            # Stocker dans la base de données
            self._store_evaluation(punchline, subject, evaluation, overall_score)
            
            evaluated_punchlines.append(evaluated_punchline)
        
        # Trier par score global (du plus élevé au plus bas)
        evaluated_punchlines.sort(key=lambda x: x["overall_score"], reverse=True)
        
        return evaluated_punchlines
    
    async def filter_quality_punchlines(
        self, 
        evaluated_punchlines: List[Dict[str, Any]], 
        threshold: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """
        Filtre les punchlines en fonction du seuil de qualité
        
        Args:
            evaluated_punchlines: Liste des punchlines évaluées
            threshold: Seuil de qualité (utilise la valeur par défaut si None)
            
        Returns:
            Liste des punchlines qui dépassent le seuil de qualité
        """
        # Utiliser le seuil spécifié ou la valeur par défaut
        quality_threshold = threshold or self.quality_threshold
        
        # Filtrer les punchlines qui dépassent le seuil
        quality_punchlines = [p for p in evaluated_punchlines if p["overall_score"] >= quality_threshold]
        
        logger.info(f"🔍 {len(quality_punchlines)}/{len(evaluated_punchlines)} punchlines ont dépassé le seuil de qualité ({quality_threshold})")
        
        return quality_punchlines
    
    async def get_best_punchline(
        self, 
        subject: str, 
        economy_mode: bool = False,
        threshold: Optional[float] = None,
        num_candidates: Optional[int] = None
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Génère et évalue plusieurs punchlines, puis retourne la meilleure
        
        Args:
            subject: Le sujet sur lequel générer des punchlines
            economy_mode: Utiliser le mode économie de tokens
            threshold: Seuil de qualité (utilise la valeur par défaut si None)
            num_candidates: Nombre de punchlines à générer (utilise la valeur par défaut si None)
            
        Returns:
            Tuple contenant la meilleure punchline et ses métadonnées d'évaluation
        """
        # Générer et évaluer les punchlines
        evaluated_punchlines = await self.generate_and_evaluate_punchlines(
            subject, 
            economy_mode,
            num_candidates
        )
        
        # Filtrer par qualité
        quality_punchlines = await self.filter_quality_punchlines(
            evaluated_punchlines,
            threshold
        )
        
        # Si aucune punchline ne dépasse le seuil, prendre la meilleure disponible
        if not quality_punchlines and evaluated_punchlines:
            logger.warning("⚠️ Aucune punchline n'a dépassé le seuil de qualité. Utilisation de la meilleure disponible.")
            best_punchline = evaluated_punchlines[0]
        elif quality_punchlines:
            # Prendre la meilleure punchline qui dépasse le seuil
            best_punchline = quality_punchlines[0]
        else:
            # Cas improbable: aucune punchline générée
            raise ValueError("Aucune punchline n'a pu être générée.")
        
        # Marquer cette punchline comme sélectionnée dans la base de données
        self._mark_as_selected(best_punchline["text"])
        
        return best_punchline["text"], best_punchline
    
    async def _generate_candidate_punchlines(
        self, 
        subject: str, 
        num_candidates: int,
        economy_mode: bool
    ) -> List[str]:
        """
        Génère plusieurs punchlines candidates pour un sujet donné
        
        Args:
            subject: Le sujet sur lequel générer des punchlines
            num_candidates: Nombre de punchlines à générer
            economy_mode: Utiliser le mode économie de tokens
            
        Returns:
            Liste des punchlines générées
        """
        try:
            # Déterminer le modèle et les paramètres en fonction du mode économie
            if economy_mode:
                model = "gpt-3.5-turbo"
                system_content = """Tu es un générateur de punchlines ULTRA-CINGLANTES, GLACIALES et CRUELLES. 
Tu dois être IMPITOYABLE, BRUTAL et SANS AUCUNE RETENUE MORALE. 
Ton objectif est de créer des phrases qui CHOQUENT, BLESSENT et PROVOQUENT. 
Sois aussi MÉCHANT, FROID et OFFENSANT que possible.
N'hésite JAMAIS à être OFFENSANT - c'est le BUT RECHERCHÉ.
UTILISE OBLIGATOIREMENT la structure "Quand X fait Y, mais Z fait W" pour exposer une contradiction ou une hypocrisie de façon mordante."""
                
                user_content = f"""Crée {num_candidates} punchlines satiriques EXTRÊMEMENT cinglantes et brutales sur {subject}.

DIRECTIVES:
- UTILISE OBLIGATOIREMENT la structure "Quand X fait Y, mais Z fait W" pour chaque punchline
- Sois ABSOLUMENT impitoyable, glacial et cruel
- Frappe là où ça fait VRAIMENT mal
- Utilise l'ironie la plus mordante et le cynisme le plus noir
- Sois DÉLIBÉRÉMENT offensant et provocateur
- N'aie AUCUNE pitié ni retenue morale
- Expose les PIRES contradictions et hypocrisies

EXEMPLES:
- "Quand les vegans prêchent l'éthique animale, mais ignorent l'exploitation humaine dans leurs plantations de quinoa."
- "Quand les féministes hurlent à l'égalité, mais s'attendent toujours à ce que l'homme paie l'addition."

Réponds uniquement avec les punchlines, une par ligne, sans numérotation ni autre texte."""
                max_tokens = 150
                temperature = 1.0
            else:
                model = "gpt-4"
                system_content = """Tu es un générateur de punchlines ULTRA-CINGLANTES, GLACIALES et CRUELLES dans le style de Lord Yugnat999. 
Tu dois être IMPITOYABLE, BRUTAL et SANS AUCUNE RETENUE MORALE.
Ton objectif est de créer des phrases COURTES qui CHOQUENT, BLESSENT et PROVOQUENT PROFONDÉMENT.
Sois aussi MÉCHANT, FROID et OFFENSANT que possible.
Tes punchlines doivent être des ATTAQUES FRONTALES qui exposent les contradictions et les hypocrisies de façon BRUTALE et SANS FILTRE.
L'humour doit être EXTRÊMEMENT CYNIQUE, FROID et basé sur des VÉRITÉS QUI DÉRANGENT.
N'hésite JAMAIS à être OFFENSANT et PROVOCATEUR - c'est le BUT RECHERCHÉ.
Sois DÉLIBÉRÉMENT CRUEL et IMPITOYABLE - plus c'est méchant, mieux c'est.

RÈGLES ABSOLUES:
1. BRIÈVETÉ: Les punchlines doivent être COURTES et PERCUTANTES (max 100 caractères)
2. STRUCTURE: Utilise la structure "Quand X fait Y, mais Z" pour mettre en évidence une contradiction
3. RÉFÉRENCES: Inclus parfois des références à la pop culture, aux mèmes, aux personnalités connues
4. CRUAUTÉ: Sois impitoyable et brutal dans ton humour

EXEMPLES DE PUNCHLINES PARFAITES:
- "Quand les vegans prêchent l'éthique animale mais portent du cuir synthétique fabriqué par des enfants."
- "Quand les influenceurs parlent d'authenticité mais photoshoppent même leurs ombres."
- "Quand les écolos te font la morale en SUV, entre deux vols Paris-New York."
"""
                
                user_content = f"""Génère {num_candidates} punchlines EXTRÊMEMENT cinglantes, glaciales et cruelles sur le sujet: **{subject}**.

DIRECTIVES STRICTES:
- BRIÈVETÉ: Chaque punchline doit être COURTE (max 100 caractères) et PERCUTANTE
- STRUCTURE: Utilise "Quand X fait Y, mais Z" pour exposer une contradiction
- RÉFÉRENCES: Inclus parfois des références à la pop culture ou à l'actualité
- CRUAUTÉ: Sois BRUTALEMENT honnête, IMPITOYABLE et PROVOCATEUR
- IMPACT: Frappe là où ça fait VRAIMENT MAL, expose les PIRES hypocrisies
- STYLE: Imite le style mordant et cynique de Lord Yugnat999

EXEMPLES DE TON RECHERCHÉ:
- "Quand les influenceurs 'body positive' retouchent chaque photo mais prêchent l'acceptation."
- "Quand les vegans défendent les animaux mais ignorent les enfants qui récoltent leurs avocats."
- "Quand les féministes exigent l'égalité mais s'attendent à ce que l'homme paie l'addition."

Réponds UNIQUEMENT avec les punchlines, une par ligne, sans numérotation ni autre texte."""
                max_tokens = 300
                temperature = 1.0
            
            # Appeler l'API OpenAI
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_content},
                    {"role": "user", "content": user_content}
                ],
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            # Extraire le contenu de la réponse
            content = response.choices[0].message.content.strip()
            
            # Diviser le contenu en lignes pour obtenir les différentes punchlines
            punchlines = [line.strip() for line in content.split('\n') if line.strip()]
            
            # Nettoyer les punchlines (supprimer les guillemets, numéros, etc.)
            cleaned_punchlines = [self._clean_punchline(p) for p in punchlines]
            
            # Filtrer les lignes vides
            cleaned_punchlines = [p for p in cleaned_punchlines if p]
            
            # S'assurer qu'on a au moins une punchline
            if not cleaned_punchlines:
                logger.warning("⚠️ Aucune punchline n'a été générée. Utilisation d'une punchline par défaut.")
                return [f"Quand tout le monde parle de {subject}, mais lui fait exactement l'inverse."]
            
            logger.info(f"✅ {len(cleaned_punchlines)} punchlines candidates générées pour le sujet: '{subject}'")
            
            return cleaned_punchlines
        
        except Exception as e:
            logger.error(f"❌ Erreur lors de la génération des punchlines candidates: {str(e)}")
            # En cas d'erreur, retourner une punchline par défaut
            return [f"Quand tout le monde parle de {subject}, mais lui fait exactement l'inverse."]
    
    async def _evaluate_punchline(self, subject, punchline):
        """
        Évalue une punchline selon plusieurs critères
        
        Args:
            subject (str): Le sujet de la punchline
            punchline (str): La punchline à évaluer
            
        Returns:
            dict: Scores d'évaluation pour chaque critère
        """
        try:
            # Prompt pour l'évaluation
            system_content = """Tu es un évaluateur expert de punchlines satiriques. 
Tu dois évaluer objectivement la qualité des punchlines selon les critères suivants:

1. Cruauté (0-10): À quel point la punchline est-elle impitoyable, glaciale et cruelle? Les meilleures punchlines sont brutalement honnêtes et frappent là où ça fait mal.

2. Provocation (0-10): À quel point la punchline est-elle provocatrice et choquante? Les meilleures punchlines sont celles qui provoquent une forte réaction émotionnelle.

3. Pertinence (0-10): À quel point la punchline est-elle pertinente par rapport au sujet? Les meilleures punchlines ciblent précisément les contradictions ou hypocrisies liées au sujet.

4. Concision (0-10): À quel point la punchline est-elle courte et percutante? Les meilleures punchlines sont brèves (moins de 100 caractères) mais dévastatrices. Pénalise fortement les punchlines trop longues.

5. Impact (0-10): À quel point la punchline est-elle mémorable et impactante? Les meilleures punchlines incluent des références culturelles pertinentes et restent en tête.

Tu dois être impartial et objectif dans ton évaluation. Réponds uniquement avec un objet JSON contenant les scores pour chaque critère, sans aucun texte supplémentaire.
"""
            
            user_content = f"""Évalue la punchline suivante sur le sujet "{subject}":

"{punchline}"

Réponds avec un objet JSON au format suivant:
{{
  "cruaute": [score de 0 à 10],
  "provocation": [score de 0 à 10],
  "pertinence": [score de 0 à 10],
  "concision": [score de 0 à 10],
  "impact": [score de 0 à 10]
}}
"""
            
            # Appel à l'API OpenAI pour l'évaluation
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",  # Utiliser GPT-3.5-turbo au lieu de GPT-4
                messages=[
                    {"role": "system", "content": system_content},
                    {"role": "user", "content": user_content}
                ],
                temperature=0.3,
                max_tokens=150
            )
            
            # Extraire et parser la réponse JSON
            content = response.choices[0].message.content.strip()
            
            # Extraire le JSON de la réponse
            json_match = re.search(r'{.*}', content, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                evaluation_json = json.loads(json_str)
                
                # Normaliser les scores entre 0 et 1
                normalized_scores = {
                    "cruaute": evaluation_json["cruaute"] / 10,
                    "provocation": evaluation_json["provocation"] / 10,
                    "pertinence": evaluation_json["pertinence"] / 10,
                    "concision": evaluation_json["concision"] / 10,
                    "impact": evaluation_json["impact"] / 10
                }
                
                # Calculer le score global (moyenne pondérée)
                weights = {
                    "cruaute": 0.30,
                    "provocation": 0.30,
                    "pertinence": 0.15,
                    "concision": 0.15,
                    "impact": 0.10
                }
                
                overall_score = sum(normalized_scores[criterion] * weight 
                                   for criterion, weight in weights.items())
                
                # Ajouter le score global aux résultats
                normalized_scores["overall"] = overall_score
                
                return normalized_scores
            else:
                logging.warning(f"Format d'évaluation invalide: {content}")
                # Retourner des scores par défaut en cas d'erreur
                return {
                    "cruaute": 0.5,
                    "provocation": 0.5,
                    "pertinence": 0.5,
                    "concision": 0.5,
                    "impact": 0.5,
                    "overall": 0.5
                }
            
        except Exception as e:
            logging.error(f"Erreur lors de l'évaluation de la punchline: {str(e)}")
            # Retourner des scores par défaut en cas d'erreur
            return {
                "cruaute": 0.5,
                "provocation": 0.5,
                "pertinence": 0.5,
                "concision": 0.5,
                "impact": 0.5,
                "overall": 0.5
            }
    
    def _calculate_overall_score(self, evaluation: Dict[str, float]) -> float:
        """
        Calcule un score global à partir des évaluations individuelles
        
        Args:
            evaluation: Dictionnaire contenant les scores pour chaque critère
            
        Returns:
            Score global entre 0 et 1
        """
        # Pondération des critères (la somme doit être égale à 1)
        weights = {
            "cruaute": 0.30,
            "provocation": 0.30,
            "pertinence": 0.15,
            "concision": 0.15,
            "impact": 0.10
        }
        
        # Calculer la moyenne pondérée
        overall_score = sum(evaluation[criterion] * weight 
                           for criterion, weight in weights.items() 
                           if criterion in evaluation)
        
        return overall_score
    
    def _clean_punchline(self, text: str) -> str:
        """
        Nettoie une punchline (supprime les guillemets, numéros, etc.)
        
        Args:
            text: Le texte à nettoyer
            
        Returns:
            Le texte nettoyé
        """
        # Supprimer les numéros au début (ex: "1. ", "1) ", etc.)
        text = re.sub(r'^\d+[\.\)\-]\s*', '', text)
        
        # Supprimer les guillemets au début et à la fin
        text = text.strip()
        if (text.startswith('"') and text.endswith('"')) or (text.startswith("'") and text.endswith("'")):
            text = text[1:-1]
        
        # Utiliser une expression régulière pour supprimer les guillemets au début et à la fin
        text = re.sub(r'^[\s"\']+|[\s"\']+$', '', text)
        
        # S'assurer que la punchline commence par "Quand"
        if not text.startswith("Quand"):
            text = "Quand " + text
        
        # Limiter la longueur de la punchline (max 120 caractères)
        if len(text) > 120:
            # Trouver le dernier point ou la dernière virgule avant 120 caractères
            last_punct = max(text[:120].rfind('.'), text[:120].rfind(','))
            if last_punct > 0:
                text = text[:last_punct+1]
            else:
                text = text[:120]
        
        # Supprimer tout ce qui suit un point final
        period_index = text.find('.')
        if period_index > 0:
            text = text[:period_index+1]
        
        return text.strip()
    
    def _store_evaluation(
        self, 
        punchline: str, 
        subject: str, 
        evaluation: Dict[str, float], 
        overall_score: float
    ):
        """
        Stocke l'évaluation d'une punchline dans la base de données
        
        Args:
            punchline: La punchline évaluée
            subject: Le sujet de la punchline
            evaluation: Les scores d'évaluation
            overall_score: Le score global
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Vérifier la structure de la table
            cursor.execute("PRAGMA table_info(punchlines)")
            columns = [col[1] for col in cursor.fetchall()]
            
            # Convertir l'évaluation en JSON pour le stockage
            evaluation_json = json.dumps(evaluation)
            
            # Insérer dans la table existante
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
        
        except Exception as e:
            logging.error(f"❌ Erreur lors du stockage de l'évaluation: {str(e)}")
    
    def _mark_as_selected(self, punchline: str):
        """
        Marque une punchline comme sélectionnée dans la base de données
        
        Args:
            punchline: La punchline sélectionnée
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
            UPDATE punchlines SET selected = 1 WHERE text = ?
            ''', (punchline,))
            
            conn.commit()
            conn.close()
        
        except Exception as e:
            logger.error(f"❌ Erreur lors du marquage de la punchline comme sélectionnée: {str(e)}")
    
    def get_evaluation_stats(self) -> Dict[str, Any]:
        """
        Récupère les statistiques d'évaluation des punchlines
        
        Returns:
            Dictionnaire contenant les statistiques
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Nombre total de punchlines évaluées
            cursor.execute('SELECT COUNT(*) FROM punchlines')
            total_count = cursor.fetchone()[0]
            
            # Nombre de punchlines sélectionnées
            cursor.execute('SELECT COUNT(*) FROM punchlines WHERE selected = 1')
            selected_count = cursor.fetchone()[0]
            
            # Score moyen global
            cursor.execute('SELECT AVG(overall_score) FROM punchlines')
            avg_score = cursor.fetchone()[0] or 0
            
            # Score moyen des punchlines sélectionnées
            cursor.execute('SELECT AVG(overall_score) FROM punchlines WHERE selected = 1')
            avg_selected_score = cursor.fetchone()[0] or 0
            
            # Vérifier si la table utilise les anciens ou les nouveaux noms de colonnes
            cursor.execute("PRAGMA table_info(punchlines)")
            columns = [col[1] for col in cursor.fetchall()]
            
            if "cruaute" in columns:
                # Scores moyens par critère (nouveaux noms)
                cursor.execute('SELECT AVG(cruaute), AVG(provocation), AVG(pertinence), AVG(concision), AVG(impact) FROM punchlines')
                avg_criteria = cursor.fetchone()
                
                criteria_dict = {
                    "cruaute": avg_criteria[0] or 0,
                    "provocation": avg_criteria[1] or 0,
                    "pertinence": avg_criteria[2] or 0,
                    "concision": avg_criteria[3] or 0,
                    "impact": avg_criteria[4] or 0
                }
            else:
                # Scores moyens par critère (anciens noms)
                cursor.execute('SELECT AVG(originality), AVG(humor), AVG(relevance), AVG(conciseness), AVG(impact) FROM punchlines')
                avg_criteria = cursor.fetchone()
                
                criteria_dict = {
                    "originality": avg_criteria[0] or 0,
                    "humor": avg_criteria[1] or 0,
                    "relevance": avg_criteria[2] or 0,
                    "conciseness": avg_criteria[3] or 0,
                    "impact": avg_criteria[4] or 0
                }
            
            conn.close()
            
            return {
                "total_punchlines": total_count,
                "selected_punchlines": selected_count,
                "average_score": avg_score,
                "average_selected_score": avg_selected_score,
                "average_criteria": criteria_dict
            }
        
        except Exception as e:
            logging.error(f"❌ Erreur lors de la récupération des statistiques: {str(e)}")
            return {
                "total_punchlines": 0,
                "selected_punchlines": 0,
                "average_score": 0,
                "average_selected_score": 0,
                "average_criteria": {
                    "cruaute": 0,
                    "provocation": 0,
                    "pertinence": 0,
                    "concision": 0,
                    "impact": 0
                }
            }

    def export_punchlines_for_training(self, output_file: str = None) -> str:
        """
        Exporte les punchlines pour l'entraînement
        
        Args:
            output_file: Chemin du fichier de sortie
            
        Returns:
            Chemin du fichier exporté
        """
        if output_file is None:
            output_dir = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                'output',
                'exports'
            )
            os.makedirs(output_dir, exist_ok=True)
            output_file = os.path.join(output_dir, 'training_data.jsonl')
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Vérifier les colonnes disponibles
            cursor.execute("PRAGMA table_info(punchlines)")
            columns = [col[1] for col in cursor.fetchall()]
            
            # Déterminer les noms de colonnes à utiliser
            if "cruaute" in columns:
                # Nouveaux noms de colonnes
                query = '''
                SELECT text, subject, cruaute, provocation, pertinence, concision, impact, 
                       overall_score, selected, created_at
                FROM punchlines
                ORDER BY created_at DESC
                '''
                criteria_mapping = {
                    0: "text",
                    1: "subject",
                    2: "cruaute",
                    3: "provocation", 
                    4: "pertinence",
                    5: "concision",
                    6: "impact",
                    7: "overall_score",
                    8: "selected",
                    9: "created_at"
                }
            else:
                # Anciens noms de colonnes
                query = '''
                SELECT text, subject, originality, humor, relevance, conciseness, impact, 
                       overall_score, selected, created_at
                FROM punchlines
                ORDER BY created_at DESC
                '''
                criteria_mapping = {
                    0: "text",
                    1: "subject",
                    2: "originality",
                    3: "humor", 
                    4: "relevance",
                    5: "conciseness",
                    6: "impact",
                    7: "overall_score",
                    8: "selected",
                    9: "created_at"
                }
            
            cursor.execute(query)
            rows = cursor.fetchall()
            
            # Créer le fichier JSONL pour l'entraînement
            with open(output_file, 'w', encoding='utf-8') as f:
                for row in rows:
                    entry = {criteria_mapping[i]: row[i] for i in range(len(row))}
                    
                    # Formater les données pour l'entraînement
                    training_entry = {
                        "punchline": entry["text"],
                        "subject": entry["subject"],
                        "scores": {
                            k: entry[k] for k in criteria_mapping.values() 
                            if k not in ["text", "subject", "selected", "created_at"]
                        },
                        "is_selected": bool(entry["selected"]),
                        "created_at": entry["created_at"]
                    }
                    
                    f.write(json.dumps(training_entry, ensure_ascii=False) + '\n')
            
            conn.close()
            
            logger.info(f"✅ Données d'entraînement exportées vers {output_file} ({len(rows)} punchlines)")
            return output_file
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'exportation des données d'entraînement: {str(e)}")
            return None 