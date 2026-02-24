# Fase 1: Usiamo l'immagine ufficiale di uv
FROM ghcr.io/astral-sh/uv:latest AS uv_bin

# Fase 2: Immagine Python finale
FROM python:3.11-slim

# Installiamo i pacchetti per MariaDB (come prima)
RUN apt-get update && apt-get install -y \
    gcc \
    libmariadb-dev \
    pkg-config \
    default-mysql-client \
    && rm -rf /var/lib/apt/lists/*

# Copiamo il binario di uv dall'immagine precedente
COPY --from=uv_bin /uv /uvx /bin/

# Directory di lavoro
WORKDIR /app

# Variabili d'ambiente per Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Copiamo i file delle dipendenze per sfruttare la cache
COPY pyproject.toml .

# Installiamo le dipendenze usando uv (senza creare un venv nel container per semplicità)
# --system installa nel path di sistema del container, --no-cache risparmia spazio
RUN uv pip install --system --no-cache -r pyproject.toml

# Copiamo il resto del progetto
COPY . .

# Comando di avvio (Uvicorn)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]