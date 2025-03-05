FROM python:3.12-slim

WORKDIR /app

# Installer les dépendances système nécessaires pour MoviePy
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsm6 \
    libxext6 \
    && rm -rf /var/lib/apt/lists/*

# Copier les fichiers de dépendances
COPY requirements.txt .

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Copier le reste du code
COPY . .

# Créer le dossier de sortie
RUN mkdir -p output

# Définir les variables d'environnement
ENV PYTHONPATH=/app
ENV TEMPLATE_VIDEO_PATH=/app/src/template.mp4
ENV OUTPUT_DIRECTORY=/app/output
ENV FONT_PATH=Arial
ENV FONT_SIZE=40
ENV TEXT_COLOR=white
ENV TEXT_POSITION_Y=0.35
ENV TEXT_MARGIN_X=0.01
ENV TEXT_BACKGROUND=black
ENV ECONOMY_MODE=false
ENV TELEGRAM_AUTO_SEND=false

# Exposer le port pour l'API (si nécessaire)
EXPOSE 8000

# Commande par défaut
CMD ["python", "src/generate_meme.py"]

# Pour utiliser l'API (si implémentée)
# CMD ["python", "src/main.py"] 