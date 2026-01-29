# Usiamo una versione stabile. La 3.13 è molto recente, la 3.11/3.12 è spesso più compatibile con MariaDB
FROM python:3.11-slim

# Installiamo i pacchetti necessari per compilare i driver mariaDB
# Aggiungiamo 'mariadb-client' utile per i healthcheck e debug
RUN apt-get update && apt-get install -y \
    gcc \
    libmariadb-dev \
    pkg-config \
    default-mysql-client \
    && rm -rf /var/lib/apt/lists/*

# Impostiamo la directory di lavoro
WORKDIR /app

# Copiamo i requirements per sfruttare la cache di Docker
COPY requirements.txt .
# Evita che Python generi file .pyc e forza l'output in tempo reale
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install --no-cache-dir --upgrade pip && \ 
pip install --no-cache-dir -r requirements.txt

# Copiamo tutto il contenuto del progetto nella cartella /app del container
COPY . .

# FONDAMENTALE: Aggiungiamo /app al PYTHONPATH così Python trova il modulo 'app'
ENV PYTHONPATH=/app

# Comando per avviare Uvicorn
# Usiamo la forma 'app.main:app' assumendo che main.py sia dentro la cartella /app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
# CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload", "reload-dir","app"]