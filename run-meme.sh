#!/bin/bash

# Script pour faciliter l'utilisation du générateur de mèmes avec Docker ou Python directement

# Vérifier si Docker est installé
if ! command -v docker &> /dev/null; then
    echo "⚠️ Docker n'est pas installé. Utilisation de Python directement."
    USE_PYTHON=true
else
    USE_PYTHON=false
    # Vérifier si Docker Compose est disponible
    if ! docker compose version &> /dev/null; then
        echo "⚠️ Docker Compose n'est pas disponible. Utilisation de Python directement."
        USE_PYTHON=true
    fi
fi

# Fonction d'aide
show_help() {
    echo "Usage: ./run-meme.sh [OPTION]"
    echo ""
    echo "Options:"
    echo "  -h, --help                  Afficher cette aide"
    echo "  -g, --generate [SUJET]      Générer un mème avec un sujet spécifique"
    echo "  -t, --telegram [SUJET]      Générer un mème et l'envoyer sur Telegram"
    echo "  -a, --api                   Lancer l'API web"
    echo "  -j, --json [FICHIER] [LIMITE] Générer des mèmes par lots à partir d'un fichier JSON"
    echo "  -je, --json-economy [FICHIER] [LIMITE] Générer des mèmes par lots en mode économie"
    echo "  -s, --stats                 Afficher les statistiques des punchlines"
    echo "  -m, --meme-stats            Afficher les statistiques des mèmes générés"
    echo "  -e, --export [FICHIER]      Exporter les punchlines vers un fichier"
    echo "  -q, --test-quality [SUJET]  Tester la pipeline de qualité"
    echo "  -c, --test-mvc [SUJET]      Tester la nouvelle architecture MVC"
    echo "  -b, --batch [SUJETS]        Générer des mèmes par lots à partir d'une liste de sujets séparés par des virgules"
    echo "  -f, --full-test [SUJET]     Exécuter tous les tests MVC"
    echo ""
    echo "Exemples:"
    echo "  ./run-meme.sh --generate \"Les politiciens\" # Générer un mème sur les politiciens"
    echo "  ./run-meme.sh --telegram \"Les médias\"      # Générer un mème et l'envoyer sur Telegram"
    echo "  ./run-meme.sh --json json.json 5          # Générer 5 mèmes à partir du fichier json.json"
    echo "  ./run-meme.sh --json-economy json.json 5  # Générer 5 mèmes en mode économie"
    echo "  ./run-meme.sh --api                       # Lancer l'API web"
    echo "  ./run-meme.sh --stats                     # Afficher les statistiques des punchlines"
    echo "  ./run-meme.sh --meme-stats                # Afficher les statistiques des mèmes générés"
    echo "  ./run-meme.sh --export punchlines.jsonl   # Exporter les punchlines"
    echo "  ./run-meme.sh --test-quality \"Les médias\" # Tester la pipeline de qualité"
    echo "  ./run-meme.sh --test-mvc \"Les médias\"     # Tester la nouvelle architecture MVC"
    echo "  ./run-meme.sh --batch \"Sujet1,Sujet2,Sujet3\" # Générer des mèmes sur plusieurs sujets"
    echo "  ./run-meme.sh --full-test \"Les médias\"    # Exécuter tous les tests MVC"
}

# Vérifier si le fichier .env existe
if [ ! -f .env ]; then
    echo "⚠️ Le fichier .env n'existe pas. Création à partir de .env.example..."
    cp .env.example .env
    echo "✅ Fichier .env créé. Veuillez le modifier pour ajouter votre clé API OpenAI et vos paramètres Telegram."
fi

# Vérifier si Python est installé (pour le mode Python)
if [ "$USE_PYTHON" = true ] && ! command -v python &> /dev/null; then
    echo "❌ Python n'est pas installé. Veuillez l'installer avant de continuer."
    exit 1
fi

# Vérifier si le dossier src existe (pour le mode Python)
if [ "$USE_PYTHON" = true ] && [ ! -d "src" ]; then
    echo "❌ Le dossier src n'existe pas."
    exit 1
fi

# Traitement des arguments
case "$1" in
    -h|--help)
        show_help
        ;;
    -g|--generate)
        if [ -z "$2" ]; then
            echo "❌ Veuillez spécifier un sujet pour le mème."
            exit 1
        fi
        echo "🎬 Génération d'un mème sur le sujet: $2"
        if [ "$USE_PYTHON" = true ]; then
            cd src && python generate_meme.py --subject "$2"
        else
            docker compose run --rm meme-generator python src/generate_meme.py --subject "$2"
        fi
        echo "✅ Mème généré avec succès. Vérifiez le dossier output."
        ;;
    -t|--telegram)
        if [ -z "$2" ]; then
            echo "❌ Veuillez spécifier un sujet pour le mème."
            exit 1
        fi
        echo "📱 Génération et envoi d'un mème sur Telegram avec le sujet: $2"
        if [ "$USE_PYTHON" = true ]; then
            cd src && python generate_meme.py --subject "$2" --telegram
        else
            docker compose run --rm meme-generator python src/generate_meme.py --subject "$2" --telegram
        fi
        echo "✅ Mème généré et envoyé sur Telegram avec succès."
        ;;
    -a|--api)
        echo "🌐 Lancement de l'API web..."
        if [ "$USE_PYTHON" = true ]; then
            cd src && python api.py
        else
            docker compose up
        fi
        ;;
    -j|--json)
        if [ -z "$2" ]; then
            echo "❌ Veuillez spécifier un fichier JSON pour la génération par lots."
            exit 1
        fi
        LIMIT=${3:-10}
        echo "📦 Génération de $LIMIT mèmes à partir du fichier: $2"
        if [ "$USE_PYTHON" = true ]; then
            cd src && python -c "import asyncio; from utils.json_generator import generate_from_json; asyncio.run(generate_from_json('../$2', $LIMIT))"
        else
            docker compose run --rm meme-generator python -c "import asyncio; from src.utils.json_generator import generate_from_json; asyncio.run(generate_from_json('$2', $LIMIT))"
        fi
        echo "✅ Mèmes générés avec succès. Vérifiez le dossier output."
        ;;
    -je|--json-economy)
        if [ -z "$2" ]; then
            echo "❌ Veuillez spécifier un fichier JSON pour la génération par lots."
            exit 1
        fi
        LIMIT=${3:-10}
        echo "📦 Génération de $LIMIT mèmes en mode économie à partir du fichier: $2"
        if [ "$USE_PYTHON" = true ]; then
            cd src && python -c "import asyncio; from utils.json_generator import generate_from_json; asyncio.run(generate_from_json('../$2', $LIMIT, True))"
        else
            docker compose run --rm meme-generator python -c "import asyncio; from src.utils.json_generator import generate_from_json; asyncio.run(generate_from_json('$2', $LIMIT, True))"
        fi
        echo "✅ Mèmes générés avec succès. Vérifiez le dossier output."
        ;;
    -s|--stats)
        echo "📊 Affichage des statistiques des punchlines..."
        if [ "$USE_PYTHON" = true ]; then
            cd src && python -c "from utils.punchlines_stats import get_punchlines_stats; get_punchlines_stats()"
        else
            docker compose run --rm meme-generator python -c "from src.utils.punchlines_stats import get_punchlines_stats; get_punchlines_stats()"
        fi
        echo "✅ Statistiques affichées avec succès."
        ;;
    -m|--meme-stats)
        echo "📊 Affichage des statistiques des mèmes générés..."
        if [ "$USE_PYTHON" = true ]; then
            cd src && python -c "from utils.meme_stats import get_meme_stats; get_meme_stats()"
        else
            docker compose run --rm meme-generator python -c "from src.utils.meme_stats import get_meme_stats; get_meme_stats()"
        fi
        echo "✅ Statistiques des mèmes affichées avec succès."
        ;;
    -e|--export)
        if [ -z "$2" ]; then
            echo "❌ Veuillez spécifier un fichier de sortie pour l'exportation des punchlines."
            exit 1
        fi
        echo "📤 Exportation des punchlines vers: $2"
        if [ "$USE_PYTHON" = true ]; then
            cd src && python -c "from utils.export_punchlines import export_punchlines; export_punchlines('../output/exports/$2')"
        else
            docker compose run --rm meme-generator python -c "from src.utils.export_punchlines import export_punchlines; export_punchlines('output/exports/$2')"
        fi
        echo "✅ Punchlines exportées avec succès."
        ;;
    -q|--test-quality)
        if [ -z "$2" ]; then
            echo "❌ Veuillez spécifier un sujet pour tester la pipeline de qualité."
            exit 1
        fi
        echo "🧪 Test de la pipeline de qualité sur le sujet: $2"
        if [ "$USE_PYTHON" = true ]; then
            cd src && python -c "import asyncio; from tests.test_quality_pipeline import test_get_best_punchline; asyncio.run(test_get_best_punchline('$2'))"
        else
            docker compose run --rm meme-generator python -c "import asyncio; from src.tests.test_quality_pipeline import test_get_best_punchline; asyncio.run(test_get_best_punchline('$2'))"
        fi
        echo "✅ Test de la pipeline de qualité terminé avec succès."
        ;;
    -c|--test-mvc)
        if [ -z "$2" ]; then
            echo "❌ Veuillez spécifier un sujet pour tester l'architecture MVC."
            exit 1
        fi
        echo "🧪 Test de l'architecture MVC sur le sujet: $2"
        if [ "$USE_PYTHON" = true ]; then
            cd src && python test_simple_mvc.py "$2"
        else
            docker compose run --rm meme-generator python src/test_simple_mvc.py "$2"
        fi
        echo "✅ Test de l'architecture MVC terminé avec succès."
        ;;
    -b|--batch)
        if [ -z "$2" ]; then
            echo "❌ Veuillez spécifier une liste de sujets séparés par des virgules."
            exit 1
        fi
        echo "📦 Génération de mèmes par lots sur les sujets: $2"
        if [ "$USE_PYTHON" = true ]; then
            cd src && python generate_meme.py --batch --subject "$2"
        else
            docker compose run --rm meme-generator python src/generate_meme.py --batch --subject "$2"
        fi
        echo "✅ Mèmes générés avec succès. Vérifiez le dossier output."
        ;;
    -f|--full-test)
        SUBJECT="${2:-L\'arrogance des développeurs}"
        ESCAPED_SUBJECT=$(echo "$SUBJECT" | sed "s/'/\\\'/g")
        echo "🧪 Exécution de tous les tests MVC sur le sujet: $SUBJECT"
        if [ "$USE_PYTHON" = true ]; then
            cd src && python tests/test_mvc.py "$ESCAPED_SUBJECT"
        else
            docker compose run --rm meme-generator python src/tests/test_mvc.py "$ESCAPED_SUBJECT"
        fi
        echo "✅ Tous les tests MVC terminés avec succès."
        ;;
    *)
        echo "❌ Option non reconnue: $1"
        show_help
        exit 1
        ;;
esac

exit 0 