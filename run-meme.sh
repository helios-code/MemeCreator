#!/bin/bash

# Script pour faciliter l'utilisation du générateur de mèmes sans Docker

# Fonction d'aide
show_help() {
    echo "Usage: ./run-meme.sh [OPTION]"
    echo ""
    echo "Options:"
    echo "  -h, --help                  Afficher cette aide"
    echo "  -g, --generate [SUJET]      Générer un mème avec un sujet spécifique"
    echo "  -t, --telegram [SUJET]      Générer un mème et l'envoyer sur Telegram"
    echo "  -j, --json [FICHIER] [LIMITE] Générer des mèmes par lots à partir d'un fichier JSON"
    echo "  -a, --api                   Lancer l'API web"
    echo ""
    echo "Exemples:"
    echo "  ./run-meme.sh --generate \"Les politiciens\" # Générer un mème sur les politiciens"
    echo "  ./run-meme.sh --telegram \"Les médias\"      # Générer un mème et l'envoyer sur Telegram"
    echo "  ./run-meme.sh --json json.json 5          # Générer 5 mèmes à partir du fichier json.json"
    echo "  ./run-meme.sh --api                       # Lancer l'API web"
}

# Vérifier si le fichier .env existe
if [ ! -f .env ]; then
    echo "⚠️ Le fichier .env n'existe pas. Création à partir de .env.example..."
    cp .env.example .env
    echo "✅ Fichier .env créé. Veuillez le modifier pour ajouter votre clé API OpenAI et vos paramètres Telegram."
fi

# Vérifier si Python est installé
if ! command -v python &> /dev/null; then
    echo "❌ Python n'est pas installé. Veuillez l'installer avant de continuer."
    exit 1
fi

# Vérifier si les dépendances sont installées
if [ ! -f "requirements.txt" ]; then
    echo "❌ Le fichier requirements.txt n'existe pas."
    exit 1
fi

# Vérifier si le dossier src existe
if [ ! -d "src" ]; then
    echo "❌ Le dossier src n'existe pas."
    exit 1
fi

# Traiter les arguments
case "$1" in
    -h|--help)
        show_help
        ;;
    -g|--generate)
        if [ -z "$2" ]; then
            echo "❌ Veuillez spécifier un sujet pour la génération du mème."
            exit 1
        fi
        echo "🎬 Génération d'un mème sur le sujet: $2"
        cd src && python generate_meme.py -s "$2"
        echo "✅ Mème généré avec succès. Vérifiez le dossier output."
        ;;
    -t|--telegram)
        if [ -z "$2" ]; then
            echo "❌ Veuillez spécifier un sujet pour la génération du mème."
            exit 1
        fi
        echo "📱 Génération d'un mème et envoi sur Telegram sur le sujet: $2"
        cd src && python generate_meme.py -s "$2" --telegram
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
        
        # Construire la commande avec ou sans limite
        if [ -z "$3" ]; then
            echo "📦 Génération de mèmes par lots à partir du fichier: $2"
            cd src && python generate_meme.py -b "../$2"
        else
            echo "📦 Génération de $3 mèmes par lots à partir du fichier: $2"
            cd src && python generate_meme.py -b "../$2" -l "$3"
        fi
        
        echo "✅ Mèmes générés avec succès. Vérifiez le dossier output."
        ;;
    -a|--api)
        echo "🌐 Lancement de l'API web..."
        cd src && python main.py
        echo "✅ API web lancée avec succès."
        ;;
    *)
        echo "❌ Option non reconnue: $1"
        show_help
        exit 1
        ;;
esac

exit 0 