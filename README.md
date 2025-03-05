# Générateur de Mèmes "L'ARROGANCE!" 🎬

Un générateur de mèmes vidéo qui utilise le template de Ludovic Magnin criant "L'ARROGANCE!". L'outil ajoute automatiquement un texte personnalisé ou généré par GPT-4 dans la partie supérieure de la vidéo, puis peut l'envoyer directement sur Telegram.

## 🚀 Fonctionnalités

- ✨ Génération automatique de punchlines humoristiques avec OpenAI GPT-4
- 📝 Ajout de texte personnalisé sur la vidéo template
- 🎥 Exportation de la vidéo avec le texte incrusté
- 💰 Mode économie de tokens (utilise GPT-3.5-turbo au lieu de GPT-4)
- 📦 Génération par lots à partir d'un fichier JSON de sujets
- 📱 Envoi automatique des mèmes sur Telegram
- 🏷️ Génération automatique de hashtags pertinents
- 📄 Génération de descriptions engageantes pour les réseaux sociaux

## 📋 Prérequis

- Python 3.12
- Clé API OpenAI (pour la génération de punchlines)
- Bot Telegram (pour l'envoi des mèmes sur Telegram)

## 🔧 Installation

1. Cloner ce dépôt
   ```bash
   git clone https://github.com/votre-username/arrogance-meme-creator.git
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

### Génération par lots

```bash
cd src
python generate_meme.py -b "sujets.json" -l 5
```

### Envoi sur Telegram

```bash
cd src
python generate_meme.py -s "Les médias" --telegram
```

## 📜 Licence

Ce projet est sous licence MIT - voir le fichier [LICENSE](LICENSE) pour plus de détails. 