FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

# Installation des dépendances système
# Modifie cette section dans ton Dockerfile
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    libjpeg-dev \
    zlib1g-dev \
    libpng-dev \
    && rm -rf /var/lib/apt/lists/*

# Installation des librairies Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copie du projet
COPY . .

EXPOSE 8000

# Utilisation de python au lieu de python3 pour plus de compatibilité sur l'image slim
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]