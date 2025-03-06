#!/usr/bin/env python3
import os
import sys
import asyncio
import argparse
import json
import random
from dotenv import load_dotenv
from core.quality_pipeline import QualityPipeline
import logging
from unittest.mock import patch, MagicMock

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('test_quality_pipeline_mock')

# Load environment variables
load_dotenv()

# Mocked punchlines for different subjects
MOCK_PUNCHLINES = {
    "Les politiciens": [
        "Quand il promet de réduire les impôts mais augmente son salaire",
        "Quand il dit 'je suis à l'écoute du peuple' mais coupe son micro",
        "Quand il parle de transparence mais refuse de publier ses comptes"
    ],
    "Les développeurs web": [
        "Quand il dit 'ça marchait sur ma machine' mais crash en production",
        "Quand il promet de livrer dans les délais mais ajoute une 'petite feature'",
        "Quand il dit 'mon code est propre' mais a 200 warnings à la compilation"
    ],
    "Les banques suisses": [
        "Quand elle dit 'votre argent est en sécurité' mais ne précise pas pour qui",
        "Quand elle parle d'éthique mais ouvre un compte pour un dictateur",
        "Quand elle promet la discrétion mais envoie des relevés à la mauvaise adresse"
    ],
    "default": [
        "Quand il parle de {subject} mais fait exactement l'inverse",
        "Quand il prétend connaître {subject} mais ne sait même pas par où commencer",
        "Quand tout le monde parle de {subject}, mais lui fait exactement l'inverse"
    ]
}

# Mocked evaluations with random scores
def get_mock_evaluation():
    """Generate random evaluation scores"""
    return {
        "originality": round(random.uniform(0.5, 1.0), 2),
        "humor": round(random.uniform(0.5, 1.0), 2),
        "relevance": round(random.uniform(0.5, 1.0), 2),
        "conciseness": round(random.uniform(0.5, 1.0), 2),
        "impact": round(random.uniform(0.5, 1.0), 2)
    }

class MockQualityPipeline(QualityPipeline):
    """
    Version mockée de la pipeline de qualité pour les tests
    """
    
    async def _generate_candidate_punchlines(self, subject, num_candidates, economy_mode):
        """
        Version mockée qui retourne des punchlines prédéfinies
        """
        logger.info(f"🔍 Génération de {num_candidates} punchlines mockées pour le sujet: '{subject}'")
        
        if subject in MOCK_PUNCHLINES:
            punchlines = MOCK_PUNCHLINES[subject]
        else:
            punchlines = [p.format(subject=subject) for p in MOCK_PUNCHLINES["default"]]
        
        # Ensure we have enough punchlines
        while len(punchlines) < num_candidates:
            punchlines.append(f"Punchline mockée #{len(punchlines)+1} pour {subject}")
        
        return punchlines[:num_candidates]
    
    async def _evaluate_punchline(self, punchline, subject):
        """
        Version mockée qui retourne des évaluations aléatoires
        """
        logger.info(f"🔍 Évaluation mockée de la punchline: '{punchline}'")
        
        # Generate random evaluation scores
        evaluation = get_mock_evaluation()
        
        # Add some bias for specific keywords to make results more realistic
        if "exactement l'inverse" in punchline:
            evaluation["humor"] = min(1.0, evaluation["humor"] + 0.2)
            evaluation["impact"] = min(1.0, evaluation["impact"] + 0.1)
        
        if len(punchline) < 60:
            evaluation["conciseness"] = min(1.0, evaluation["conciseness"] + 0.15)
        
        if subject.lower() in punchline.lower():
            evaluation["relevance"] = min(1.0, evaluation["relevance"] + 0.2)
        
        return evaluation

async def test_generate_and_evaluate(subject, num_candidates=3, economy_mode=False):
    """
    Teste la génération et l'évaluation de punchlines
    """
    logger.info(f"🧪 Test de génération et évaluation pour le sujet: '{subject}'")
    logger.info(f"🔧 Paramètres: {num_candidates} candidats, mode économie: {economy_mode}")
    
    # Initialiser la pipeline mockée
    pipeline = MockQualityPipeline()
    
    # Générer et évaluer les punchlines
    evaluated_punchlines = await pipeline.generate_and_evaluate_punchlines(
        subject=subject,
        economy_mode=economy_mode,
        num_candidates=num_candidates
    )
    
    # Afficher les résultats
    logger.info(f"✅ {len(evaluated_punchlines)} punchlines générées et évaluées")
    
    for i, punchline in enumerate(evaluated_punchlines):
        logger.info(f"\n📝 Punchline #{i+1}: {punchline['text']}")
        logger.info(f"📊 Score global: {punchline['overall_score']:.2f}")
        logger.info(f"📊 Scores détaillés:")
        for criterion, score in punchline['evaluation'].items():
            logger.info(f"  - {criterion}: {score:.2f}")
    
    return evaluated_punchlines

async def test_filter_quality(subject, threshold=0.7, num_candidates=3, economy_mode=False):
    """
    Teste le filtrage des punchlines par qualité
    """
    logger.info(f"🧪 Test de filtrage par qualité pour le sujet: '{subject}'")
    logger.info(f"🔧 Paramètres: seuil={threshold}, {num_candidates} candidats, mode économie: {economy_mode}")
    
    # Initialiser la pipeline mockée
    pipeline = MockQualityPipeline()
    
    # Générer et évaluer les punchlines
    evaluated_punchlines = await pipeline.generate_and_evaluate_punchlines(
        subject=subject,
        economy_mode=economy_mode,
        num_candidates=num_candidates
    )
    
    # Filtrer les punchlines par qualité
    quality_punchlines = await pipeline.filter_quality_punchlines(
        evaluated_punchlines=evaluated_punchlines,
        threshold=threshold
    )
    
    # Afficher les résultats
    logger.info(f"✅ {len(quality_punchlines)}/{len(evaluated_punchlines)} punchlines ont dépassé le seuil de qualité ({threshold})")
    
    for i, punchline in enumerate(quality_punchlines):
        logger.info(f"\n📝 Punchline de qualité #{i+1}: {punchline['text']}")
        logger.info(f"📊 Score global: {punchline['overall_score']:.2f}")
    
    return quality_punchlines

async def test_get_best_punchline(subject, threshold=0.7, num_candidates=3, economy_mode=False):
    """
    Teste la sélection de la meilleure punchline
    """
    logger.info(f"🧪 Test de sélection de la meilleure punchline pour le sujet: '{subject}'")
    logger.info(f"🔧 Paramètres: seuil={threshold}, {num_candidates} candidats, mode économie: {economy_mode}")
    
    # Initialiser la pipeline mockée
    pipeline = MockQualityPipeline()
    
    # Obtenir la meilleure punchline
    best_text, best_metadata = await pipeline.get_best_punchline(
        subject=subject,
        economy_mode=economy_mode,
        threshold=threshold,
        num_candidates=num_candidates
    )
    
    # Afficher les résultats
    logger.info(f"\n🏆 Meilleure punchline: {best_text}")
    logger.info(f"📊 Score global: {best_metadata['overall_score']:.2f}")
    logger.info(f"📊 Scores détaillés:")
    for criterion, score in best_metadata['evaluation'].items():
        logger.info(f"  - {criterion}: {score:.2f}")
    
    return best_text, best_metadata

async def test_stats():
    """
    Teste la récupération des statistiques
    """
    logger.info(f"🧪 Test de récupération des statistiques")
    
    # Initialiser la pipeline mockée
    pipeline = MockQualityPipeline()
    
    # Récupérer les statistiques
    stats = pipeline.get_evaluation_stats()
    
    # Afficher les résultats
    logger.info(f"\n📊 Statistiques de la pipeline de qualité:")
    logger.info(f"Total des punchlines évaluées: {stats['total_punchlines']}")
    logger.info(f"Punchlines sélectionnées: {stats['selected_punchlines']}")
    
    if stats['total_punchlines'] > 0:
        logger.info(f"Score moyen global: {stats['average_score']:.2f}")
        logger.info(f"Score moyen des punchlines sélectionnées: {stats['average_selected_score']:.2f}")
        logger.info(f"Scores moyens par critère:")
        for criterion, score in stats['average_criteria'].items():
            logger.info(f"  - {criterion}: {score:.2f}")
    else:
        logger.info("Aucune statistique disponible (pas de punchlines évaluées)")
    
    return stats

async def test_batch_subjects(subjects, threshold=0.7, num_candidates=3, economy_mode=False):
    """
    Teste la génération de punchlines pour plusieurs sujets
    """
    logger.info(f"🧪 Test de génération par lots pour {len(subjects)} sujets")
    logger.info(f"🔧 Paramètres: seuil={threshold}, {num_candidates} candidats, mode économie: {economy_mode}")
    
    results = []
    
    # Initialiser la pipeline mockée
    pipeline = MockQualityPipeline()
    
    for i, subject in enumerate(subjects):
        logger.info(f"\n[{i+1}/{len(subjects)}] 🤖 Traitement du sujet: \"{subject}\"")
        
        # Obtenir la meilleure punchline
        best_text, best_metadata = await pipeline.get_best_punchline(
            subject=subject,
            economy_mode=economy_mode,
            threshold=threshold,
            num_candidates=num_candidates
        )
        
        # Afficher les résultats
        logger.info(f"🏆 Meilleure punchline: {best_text}")
        logger.info(f"📊 Score global: {best_metadata['overall_score']:.2f}")
        
        results.append({
            "subject": subject,
            "text": best_text,
            "score": best_metadata['overall_score'],
            "evaluation": best_metadata['evaluation']
        })
    
    # Afficher les statistiques
    await test_stats()
    
    return results

async def main():
    parser = argparse.ArgumentParser(description='Test de la pipeline de qualité pour les punchlines (version mockée)')
    parser.add_argument('-s', '--subject', type=str, help='Sujet pour la génération de punchlines')
    parser.add_argument('-b', '--batch', type=str, help='Fichier JSON contenant une liste de sujets')
    parser.add_argument('-n', '--num-candidates', type=int, default=3, help='Nombre de punchlines candidates à générer')
    parser.add_argument('-t', '--threshold', type=float, default=0.7, help='Seuil de qualité (entre 0 et 1)')
    parser.add_argument('-e', '--economy', action='store_true', help='Activer le mode économie de tokens')
    parser.add_argument('--test-all', action='store_true', help='Exécuter tous les tests pour un sujet donné')
    parser.add_argument('--stats', action='store_true', help='Afficher les statistiques de la pipeline')
    
    args = parser.parse_args()
    
    if args.stats:
        await test_stats()
        return
    
    if args.batch:
        try:
            with open(args.batch, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if 'sujets_clivants' in data:
                subjects = data['sujets_clivants']
            elif isinstance(data, list):
                subjects = data
            else:
                logger.error("❌ Format de fichier JSON invalide. Doit contenir une clé 'sujets_clivants' ou être une liste.")
                return
            
            results = await test_batch_subjects(
                subjects=subjects,  # Pas de limite pour les tests mockés
                threshold=args.threshold,
                num_candidates=args.num_candidates,
                economy_mode=args.economy
            )
            
            # Sauvegarder les résultats dans un fichier JSON
            output_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                'output',
                'reports',
                'mock_test_results.json'
            )
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            
            logger.info(f"\n💾 Résultats sauvegardés dans: {output_path}")
            
        except Exception as e:
            logger.error(f"❌ Erreur lors du traitement du fichier batch: {str(e)}")
            return
    
    elif args.subject:
        if args.test_all:
            # Exécuter tous les tests pour le sujet donné
            await test_generate_and_evaluate(
                subject=args.subject,
                num_candidates=args.num_candidates,
                economy_mode=args.economy
            )
            
            await test_filter_quality(
                subject=args.subject,
                threshold=args.threshold,
                num_candidates=args.num_candidates,
                economy_mode=args.economy
            )
            
            await test_get_best_punchline(
                subject=args.subject,
                threshold=args.threshold,
                num_candidates=args.num_candidates,
                economy_mode=args.economy
            )
            
            await test_stats()
        else:
            # Exécuter uniquement le test de la meilleure punchline
            await test_get_best_punchline(
                subject=args.subject,
                threshold=args.threshold,
                num_candidates=args.num_candidates,
                economy_mode=args.economy
            )
    else:
        logger.error("❌ Veuillez spécifier un sujet (-s) ou un fichier batch (-b)")
        parser.print_help()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\n⚠️ Opération annulée par l'utilisateur")
        sys.exit(0)
    except Exception as e:
        logger.error(f"❌ Erreur fatale: {str(e)}")
        sys.exit(1) 