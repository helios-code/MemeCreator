#!/bin/bash

# Script pour faciliter l'utilisation du générateur de mèmes avec Docker ou Python directement

# Force Python mode for testing
USE_PYTHON=true

# Vérifier si Docker est installé (skipped due to forced Python mode)
# if ! command -v docker &> /dev/null; then
#     echo "⚠️ Docker n'est pas installé. Utilisation de Python directement."
#     USE_PYTHON=true
# else
#     USE_PYTHON=false
#     # Vérifier si Docker Compose est disponible
#     if ! docker compose version &> /dev/null; then
#         echo "⚠️ Docker Compose n'est pas disponible. Utilisation de Python directement."
#         USE_PYTHON=true
#     fi
# fi

# Vérifier si l'image Docker existe, sinon la construire
check_docker_image() {
    if [ "$USE_PYTHON" = false ]; then
        if ! docker images | grep -q "arrogance-meme-creator"; then
            echo "🔄 Construction de l'image Docker..."
            docker compose build
        fi
    fi
}

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
    echo "  -s, --stats                 Afficher les statistiques des punchlines"
    echo "  -e, --export [FICHIER]      Exporter les punchlines vers un fichier"
    echo "  -q, --test-quality [SUJET]  Tester la pipeline de qualité"
    echo "  -b, --build                 Reconstruire l'image Docker"
    echo ""
    echo "Exemples:"
    echo "  ./run-meme.sh --generate \"Les politiciens\" # Générer un mème sur les politiciens"
    echo "  ./run-meme.sh --telegram \"Les médias\"      # Générer un mème et l'envoyer sur Telegram"
    echo "  ./run-meme.sh --json json.json 5          # Générer 5 mèmes à partir du fichier json.json"
    echo "  ./run-meme.sh --api                       # Lancer l'API web"
    echo "  ./run-meme.sh --stats                     # Afficher les statistiques des punchlines"
    echo "  ./run-meme.sh --export punchlines.jsonl   # Exporter les punchlines"
    echo "  ./run-meme.sh --test-quality \"Les médias\" # Tester la pipeline de qualité"
    echo "  ./run-meme.sh --build                     # Reconstruire l'image Docker"
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

# Traiter les arguments
case "$1" in
    -h|--help)
        show_help
        ;;
    -b|--build)
        if [ "$USE_PYTHON" = true ]; then
            echo "❌ Docker n'est pas installé. Impossible de construire l'image."
            exit 1
        fi
        echo "🔄 Construction de l'image Docker..."
        docker compose build
        echo "✅ Image Docker construite avec succès."
        ;;
    -g|--generate)
        if [ -z "$2" ]; then
            echo "❌ Veuillez spécifier un sujet pour la génération du mème."
            exit 1
        fi
        echo "🎬 Génération d'un mème sur le sujet: $2"
        if [ "$USE_PYTHON" = true ]; then
            cd src && python generate_meme.py -s "$2"
        else
            check_docker_image
            docker compose run --rm meme-generator python src/generate_meme.py -s "$2"
        fi
        echo "✅ Mème généré avec succès. Vérifiez le dossier output."
        ;;
    -t|--telegram)
        if [ -z "$2" ]; then
            echo "❌ Veuillez spécifier un sujet pour la génération du mème."
            exit 1
        fi
        echo "📱 Génération d'un mème et envoi sur Telegram sur le sujet: $2"
        if [ "$USE_PYTHON" = true ]; then
            cd src && python generate_meme.py -s "$2" --telegram
        else
            check_docker_image
            docker compose run --rm meme-generator python src/generate_meme.py -s "$2" --telegram
        fi
        echo "✅ Mème généré et envoyé sur Telegram avec succès."
        ;;
    -j|--json)
        if [ -z "$2" ]; then
            echo "❌ Veuillez spécifier un fichier JSON pour la génération par lots."
            exit 1
        fi
        
        # Vérifier si le fichier existe
        if [ ! -f "$2" ]; then
            echo "❌ Le fichier $2 n'existe pas."
            exit 1
        fi
        
        # Vérifier si l'option --telegram est spécifiée
        TELEGRAM_OPTION=""
        if [ "$4" = "--telegram" ] || [ "$4" = "-t" ]; then
            TELEGRAM_OPTION="--telegram"
            echo "📱 Envoi sur Telegram activé pour la génération par lots."
        fi
        
        # Construire la commande avec ou sans limite
        if [ -z "$3" ] || [[ ! "$3" =~ ^[0-9]+$ ]]; then
            # Si $3 n'est pas un nombre ou est vide, générer un seul mème
            echo "📦 Génération aléatoire d'un mème à partir du fichier: $2"
            if [ "$USE_PYTHON" = true ]; then
                cd src && python generate_meme.py -b "../$2" -l 1 $TELEGRAM_OPTION
            else
                check_docker_image
                docker compose run --rm meme-generator python src/generate_meme.py -b "$2" -l 1 $TELEGRAM_OPTION
            fi
        else
            echo "📦 Génération aléatoire de $3 mèmes à partir du fichier: $2"
            if [ "$USE_PYTHON" = true ]; then
                cd src && python generate_meme.py -b "../$2" -l "$3" $TELEGRAM_OPTION
            else
                check_docker_image
                docker compose run --rm meme-generator python src/generate_meme.py -b "$2" -l "$3" $TELEGRAM_OPTION
            fi
        fi
        
        echo "✅ Mèmes générés avec succès. Vérifiez le dossier output."
        ;;
    -a|--api)
        echo "🌐 Lancement de l'API web..."
        if [ "$USE_PYTHON" = true ]; then
            cd src && python main.py
        else
            check_docker_image
            docker compose up meme-generator
        fi
        echo "✅ API web lancée avec succès."
        ;;
    -s|--stats)
        echo "📊 Affichage des statistiques des punchlines..."
        if [ "$USE_PYTHON" = true ]; then
            cd src && python -c "from utils.punchlines_stats import get_punchlines_stats; get_punchlines_stats()"
        else
            check_docker_image
            docker compose run --rm meme-generator python -c "from src.utils.punchlines_stats import get_punchlines_stats; get_punchlines_stats()"
        fi
        echo "✅ Statistiques affichées avec succès."
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
            check_docker_image
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
            check_docker_image
            docker compose run --rm meme-generator python -c "import asyncio; from src.tests.test_quality_pipeline import test_get_best_punchline; asyncio.run(test_get_best_punchline('$2'))"
        fi
        echo "✅ Test de la pipeline de qualité terminé avec succès."
        ;;
    *)
        echo "❌ Option non reconnue: $1"
        show_help
        exit 1
        ;;
esac

exit 0 