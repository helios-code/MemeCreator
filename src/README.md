# Structure du projet

Ce dossier contient le code source du générateur de mèmes "L'ARROGANCE!". Voici la structure du projet:

## Organisation des dossiers

- `core/`: Contient les classes principales du générateur de mèmes
  - `meme_generator.py`: Classe principale du générateur de mèmes
  - `quality_pipeline.py`: Pipeline de qualité pour les punchlines
  - `video_processor.py`: Traitement vidéo avec MoviePy

- `clients/`: Contient les clients pour les API externes
  - `openai_client.py`: Client pour l'API OpenAI
  - `telegram_client.py`: Client pour l'API Telegram

- `data/`: Contient les données utilisées par le générateur
  - `template.mp4`: Vidéo template "L'ARROGANCE!"
  - `test_subjects.json`: Exemples de sujets pour la génération
  - `json.json`: Fichier JSON par défaut pour la génération par lots

- `utils/`: Contient des utilitaires divers
  - `export_punchlines.py`: Utilitaire pour exporter les punchlines
  - `punchlines_stats.py`: Utilitaire pour afficher des statistiques sur les punchlines

- `tests/`: Contient les tests unitaires
  - `test_quality_pipeline.py`: Tests pour la pipeline de qualité
  - `test_quality_pipeline_mock.py`: Tests avec des mocks pour la pipeline de qualité

## Fichiers principaux

- `main.py`: Point d'entrée principal pour l'API web
- `generate_meme.py`: Script principal pour générer des mèmes
- `__init__.py`: Initialisation du package

## Utilisation

Pour générer un mème, utilisez le script `generate_meme.py`:

```bash
python generate_meme.py -s "Les politiciens"
```

Pour plus d'options, consultez l'aide:

```bash
python generate_meme.py -h
```

Pour lancer l'API web, utilisez le script `main.py`:

```bash
python main.py
```

Pour plus de détails sur l'utilisation, consultez le README.md à la racine du projet. 