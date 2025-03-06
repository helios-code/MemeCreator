# Générateur de Mèmes "L'ARROGANCE!" 🎬

Un générateur de mèmes vidéo qui utilise le template de Ludovic Magnin criant "L'ARROGANCE!". L'outil ajoute automatiquement un texte personnalisé ou généré par GPT-4 dans la partie supérieure de la vidéo, puis peut l'envoyer directement sur Telegram.

![Exemple de mème](docs/images/example.jpg)

## 📑 Table des matières

- [Fonctionnalités](#-fonctionnalités)
- [Structure du projet](#-structure-du-projet)
- [Prérequis](#-prérequis)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Utilisation](#-utilisation)
- [Pipeline de qualité](#-pipeline-de-qualité)
- [Génération par lots](#-génération-par-lots)
- [API](#-api)
- [Dépannage](#-dépannage)

## 🚀 Fonctionnalités

- ✨ Génération automatique de punchlines humoristiques avec OpenAI GPT-4
- 🔍 Pipeline de qualité pour évaluer et sélectionner les meilleures punchlines
- 📝 Ajout de texte personnalisé sur la vidéo template
- 🎥 Exportation de la vidéo avec le texte incrusté
- 💰 Mode économie de tokens (utilise GPT-3.5-turbo au lieu de GPT-4)
- 📦 Génération par lots à partir d'un fichier JSON de sujets
- 📱 Envoi automatique des mèmes sur Telegram
- 🏷️ Génération automatique de hashtags pertinents
- 📄 Génération de descriptions engageantes pour les réseaux sociaux
- 📊 Analyse et statistiques sur la qualité des punchlines générées

## 📂 Structure du projet

```
arrogance-meme-creator/
├── .env                  # Variables d'environnement (à créer à partir de .env.example)
├── .env.example          # Exemple de fichier de variables d'environnement
├── README.md             # Documentation du projet
├── requirements.txt      # Dépendances Python
├── run-meme.sh           # Script shell pour exécuter le générateur de mèmes
├── data/                 # Données persistantes
│   └── quality_data.db   # Base de données des punchlines et évaluations
├── docs/                 # Documentation supplémentaire
│   └── images/           # Images pour la documentation
├── output/               # Dossier où sont stockés les fichiers générés
│   ├── videos/           # Vidéos mèmes générées
│   ├── reports/          # Rapports de génération par lots et tests
│   └── exports/          # Fichiers exportés (punchlines, etc.)
└── src/                  # Code source
    ├── __init__.py       # Initialisation du package
    ├── main.py           # Point d'entrée principal
    ├── generate_meme.py  # Script de génération de mèmes
    ├── core/             # Classes principales
    │   ├── meme_generator.py # Classe principale du générateur de mèmes
    │   ├── quality_pipeline.py # Pipeline de qualité pour les punchlines
    │   └── video_processor.py # Traitement vidéo avec MoviePy
    ├── clients/          # Clients pour les API externes
    │   ├── openai_client.py  # Client pour l'API OpenAI
    │   └── telegram_client.py # Client pour l'API Telegram
    ├── data/             # Données utilisées par le générateur
    │   ├── template.mp4      # Vidéo template "L'ARROGANCE!"
    │   ├── test_subjects.json # Exemples de sujets pour la génération
    │   └── json.json         # Fichier JSON par défaut pour la génération par lots
    ├── utils/            # Utilitaires divers
    │   ├── export_punchlines.py # Utilitaire pour exporter les punchlines
    │   └── punchlines_stats.py # Utilitaire pour afficher des statistiques sur les punchlines
    └── tests/            # Tests unitaires
        ├── test_quality_pipeline.py # Tests pour la pipeline de qualité
        └── test_quality_pipeline_mock.py # Tests avec des mocks pour la pipeline de qualité
```

## 📋 Prérequis

- Python 3.12
- Clé API OpenAI (pour la génération de punchlines)
- Bot Telegram (pour l'envoi des mèmes sur Telegram, optionnel)

## 🔧 Installation

1. Cloner ce dépôt
   ```bash
   git clone https://github.com/helios-code/arrogance-meme-creator.git
   cd arrogance-meme-creator
   ```

2. Installer les dépendances:
   ```bash
   pip install -r requirements.txt
   ```

3. Copier le fichier d'exemple d'environnement:
   ```bash
   cp .env.example .env
   ```

4. Modifier le fichier `.env` et ajouter votre clé API OpenAI et vos paramètres Telegram.

## ⚙️ Configuration

Le fichier `.env` contient toutes les configurations nécessaires pour le générateur de mèmes. Voici les principales options:

### Configuration générale
```
SERVICE_PORT=8000
SERVICE_HOST=0.0.0.0
LOG_LEVEL=info
```

### API OpenAI
```
OPENAI_API_KEY=your_openai_api_key_here
```

### Configuration du générateur de mèmes
```
TEMPLATE_VIDEO_PATH=src/template.mp4
OUTPUT_DIRECTORY=output
FONT_PATH=Arial
FONT_SIZE=40
TEXT_COLOR=white
TEXT_POSITION_Y=0.35  # 35% du haut (environ 250px sur une vidéo 720p)
TEXT_MARGIN_X=0.01    # 1% de marge de chaque côté
TEXT_BACKGROUND=black
```

### Mode économie de tokens
```
ECONOMY_MODE=false  # Utilise GPT-3.5-turbo au lieu de GPT-4
```

### Configuration Telegram
```
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
TELEGRAM_CHAT_ID=your_telegram_chat_id_here
TELEGRAM_AUTO_SEND=false
```

### Configuration de la pipeline de qualité
```
USE_QUALITY_PIPELINE=true
QUALITY_THRESHOLD=0.7
NUM_PUNCHLINE_CANDIDATES=3
```

## 🎮 Utilisation

### Génération simple

```bash
cd src
python generate_meme.py
```

### Avec un texte personnalisé

```bash
cd src
python generate_meme.py -t "Quand le stagiaire push en prod un vendredi à 17h"
```

### Avec un sujet spécifique

```bash
cd src
python generate_meme.py -s "Les banques suisses"
```

### Mode économie de tokens

```bash
cd src
python generate_meme.py -e
```

### Envoi sur Telegram

```bash
cd src
python generate_meme.py -s "Les médias" --telegram
```

### Utilisation du script shell

Le script `run-meme.sh` facilite l'utilisation du générateur:

```bash
./run-meme.sh --help
```

## 🔍 Pipeline de qualité

La pipeline de qualité améliore considérablement la pertinence et l'impact des punchlines générées en suivant ces étapes:

1. **Génération multiple**: Génère plusieurs punchlines candidates pour chaque sujet
2. **Évaluation automatique**: Analyse chaque punchline selon 5 critères clés:
   - **Originalité**: Unicité et fraîcheur de la punchline
   - **Humour**: Potentiel comique et impact humoristique
   - **Pertinence**: Adéquation avec le sujet demandé
   - **Concision**: Formulation optimale et longueur appropriée
   - **Impact**: Potentiel viral et mémorable
3. **Filtrage intelligent**: Élimine les punchlines qui ne dépassent pas un seuil de qualité configurable
4. **Sélection optimale**: Choisit la meilleure punchline pour la génération du mème
5. **Analyse continue**: Stocke les évaluations dans une base de données pour améliorer les futures générations

### Configuration de la pipeline

Vous pouvez configurer la pipeline de qualité dans le fichier `.env`:

```
# Activer/désactiver la pipeline de qualité
USE_QUALITY_PIPELINE=true

# Seuil de qualité (entre 0 et 1)
QUALITY_THRESHOLD=0.7

# Nombre de punchlines candidates à générer
NUM_PUNCHLINE_CANDIDATES=3
```

## 📦 Génération par lots

Vous pouvez générer plusieurs mèmes à partir d'un fichier JSON contenant des sujets:

```bash
cd src
python generate_meme.py -b "test_subjects.json" -l 5
```

Format du fichier JSON:

```json
{
  "sujets": [
    "Les politiciens",
    "Les influenceurs",
    "Les développeurs"
  ]
}
```

## 🌐 API

Le projet inclut une API simple pour générer des mèmes via des requêtes HTTP:

```bash
cd src
python main.py
```

L'API sera disponible à l'adresse `http://localhost:8000`.

### Endpoints

- `POST /generate`: Génère un mème
  ```json
  {
    "subject": "Les politiciens",
    "custom_text": "Texte personnalisé (optionnel)",
    "economy_mode": false,
    "send_to_telegram": false
  }
  ```

## 🔧 Dépannage

### Problèmes courants

1. **Erreur d'API OpenAI**: Vérifiez que votre clé API est valide et que vous avez des crédits disponibles.

2. **Erreur de génération vidéo**: Assurez-vous que le fichier template.mp4 existe dans le dossier src.

3. **Erreur d'envoi Telegram**: Vérifiez que votre token de bot et l'ID de chat sont corrects.

### Logs

Les logs sont disponibles dans la console et peuvent aider à diagnostiquer les problèmes.

---

Créé par Loic Mancino - [GitHub](https://github.com/loicmancino) 