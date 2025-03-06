FROM python:3.12-slim

WORKDIR /app

# Installer les dépendances système nécessaires
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsm6 \
    libxext6 \
    libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*

# Copier les fichiers de dépendances
COPY requirements.txt .

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Copier le reste du code
COPY . .

# Définir les variables d'environnement
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Exposer le port pour l'API web
EXPOSE 8000

# Commande par défaut
CMD ["python", "src/main.py"] 