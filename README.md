# Integration Hub

Hub di automazione e monitoraggio pensato per girare su **Raspberry Pi 3 Model B**. Aggrega dati da API esterne (meteo, cambi valuta, notizie, tracciamento prezzi Amazon), li salva su database e li espone tramite dashboard web con autenticazione JWT.

---

## Indice

1. [Architettura](#architettura)
2. [Stack tecnologico](#stack-tecnologico)
3. [Prerequisiti e installazione](#prerequisiti-e-installazione)
4. [Variabili d'ambiente](#variabili-dambiente)
5. [Avvio](#avvio)
6. [API reference](#api-reference)
7. [Test](#test)
8. [Analisi critica e migliorie suggerite](#analisi-critica-e-migliorie-suggerite)

---

## Architettura

```
integration-hub/
├── app/
│   ├── api/routes.py          # Endpoint REST (prefisso /api/v1)
│   ├── core/
│   │   ├── config.py          # Configurazione (pydantic-settings + .env)
│   │   ├── security.py        # JWT, bcrypt, dependency get_current_user
│   │   └── scheduler.py       # Task automatici (APScheduler)
│   ├── db/database.py         # Engine SQLAlchemy async + get_db
│   ├── models/                # ORM: User, WeatherData, ExchangeData,
│   │                          #       NewsArticle, Articolo, Ricerca, …
│   ├── schemas/               # Pydantic: UserCreate, UserOut, Token, …
│   └── services/              # Business logic + chiamate HTTP esterne
│       ├── weather_service.py
│       ├── exchange_service.py
│       ├── news_service.py
│       ├── amazon_tracking_service.py
│       ├── user_service.py
│       └── system_service.py
├── static/js/                 # Frontend vanilla JS (login, register, dashboard)
├── templates/                 # HTML Jinja2
├── tests/                     # Suite pytest
├── docker-compose.yml         # MariaDB + app
├── Dockerfile                 # Multi-stage con UV
└── pyproject.toml
```

**Flusso dati**

```
APScheduler (ogni 3h) --> weatherService / exchangeService / newsService
                                |
                                v
                          MySQL / MariaDB
                                |
                                v
             FastAPI routes --> JSON response / Jinja2 dashboard
```

---

## Stack tecnologico

| Layer | Libreria |
|---|---|
| Framework | FastAPI + Uvicorn |
| ORM / DB | SQLAlchemy 2 async · aiomysql · MariaDB |
| Auth | python-jose (JWT HS256) · passlib[bcrypt] |
| HTTP client | httpx (async) |
| Scheduling | APScheduler |
| Frontend | Jinja2 · Chart.js · Vanilla JS |
| Config | pydantic-settings · python-dotenv |
| Package manager | uv |

---

## Prerequisiti e installazione

### Sviluppo locale

```bash
# 1. Clona il repository
git clone <repo-url> && cd integration-hub

# 2. Installa uv (se non presente)
curl -Ls https://astral.sh/uv/install.sh | sh

# 3. Crea virtualenv e installa dipendenze (prod + dev)
uv sync --extra dev

# 4. Copia e compila il file .env
cp .env.example .env
# modifica .env con le tue chiavi API e credenziali DB
```

### Docker (produzione / Raspberry Pi)

```bash
docker compose up -d
```

Il compose avvia MariaDB e l'applicazione. Il DB è esposto solo internamente.

---

## Variabili d'ambiente

Crea un file `.env` nella root del progetto (non committare mai questo file).

| Variabile | Descrizione | Obbligatoria |
|---|---|---|
| `DATABASE_URL` | Connection string async MySQL, es. `mysql+aiomysql://user:pass@db:3306/dbname` | Si |
| `SECRET_KEY` | Chiave HS256 per JWT (min 32 caratteri, generala con `openssl rand -hex 32`) | Si |
| `WEATHER_API_KEY` | API key OpenWeatherMap | Si |
| `EXCHANGE_API_KEY` | API key ExchangeRate-API v6 | Si |
| `NEWS_API_KEY` | API key NewsAPI | Si |
| `AXESSO_API_KEY` | API key Axesso Amazon Search | Si |
| `AXESSO_BASE_URL` | URL base Axesso | Si |
| `ARTICOLI_RICERCA` | Keyword Amazon separate da virgola, es. `laptop,mouse,tastiera` | Si |

---

## Avvio

```bash
# Sviluppo (reload automatico)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Produzione
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 1
```

Interfacce disponibili:

| URL | Descrizione |
|---|---|
| `http://localhost:8000/` | Status JSON |
| `http://localhost:8000/gui` | Dashboard pubblica (senza login) |
| `http://localhost:8000/dashboard` | Dashboard protetta |
| `http://localhost:8000/docs` | Swagger UI (FastAPI automatico) |
| `http://localhost:8000/redoc` | ReDoc |

---

## API reference

Tutti gli endpoint sotto `/api/v1`. Gli endpoint con il simbolo [auth] richiedono JWT (header `Authorization: Bearer <token>` oppure cookie `access_token`).

### Auth

| Metodo | Path | Descrizione |
|---|---|---|
| `POST` | `/api/v1/registrazione` | Crea nuovo utente |
| `POST` | `/api/v1/login` | Login, restituisce JWT |
| `GET` | `/api/v1/me` [auth] | Profilo utente corrente |

**Registrazione** — body JSON:
```json
{ "email": "user@example.com", "username": "mario", "password": "secret" }
```

**Login** — body JSON:
```json
{ "email": "user@example.com", "plain_password": "secret" }
```

### Dati

| Metodo | Path | Descrizione |
|---|---|---|
| `GET` | `/api/v1/dashboard` [auth] | Ultimo meteo, cambio EUR/USD, ultime 3 notizie |
| `GET` | `/api/v1/weather/update/{city}` [auth] | Aggiorna meteo per la città |
| `GET` | `/api/v1/weather/history` [auth] | Ultime 24 rilevazioni meteo |
| `GET` | `/api/v1/exchange/update/{base}/{target}` [auth] | Aggiorna tasso di cambio |
| `GET` | `/api/v1/news/update/{topic}` [auth] | Aggiorna notizie per topic |
| `GET` | `/api/v1/system-stats` [auth] | CPU temp, CPU%, RAM% |

---

## Test

### Installazione dipendenze di test

```bash
uv sync --extra dev
# oppure con pip
pip install pytest pytest-asyncio aiosqlite pytest-cov
```

### Eseguire i test

```bash
# Tutti i test
pytest

# Con report di copertura
pytest --cov=app --cov-report=term-missing

# Solo un modulo
pytest tests/test_security.py -v
```

### Struttura della suite

```
tests/
├── conftest.py              # Fixtures condivise: db_session, client, test_user, auth_headers
├── test_security.py         # hash, verify_password, create_token
├── test_user_service.py     # create_user, get_by_email, authenticate
├── test_routes.py           # Endpoint HTTP end-to-end
├── test_services.py         # weather/exchange/news service con httpx mockato
├── test_amazon_service.py   # retry logic, AmazonRepository
└── test_system_service.py   # CPU temp, fallback senza file thermal
```

I test usano **SQLite in-memory** (via `aiosqlite`) al posto di MySQL: nessun database reale necessario.

---

## Analisi critica e migliorie suggerite

### Vulnerabilita di sicurezza

#### Critiche

| # | Problema | Posizione | Fix |
|---|---|---|---|
| 1 | **`.env` tracciato nel repository** — chiavi API e password DB esposte | `.env` | Aggiungere `.env` a `.gitignore` e ruotare immediatamente tutte le credenziali |
| 2 | **`SECRET_KEY` con fallback hardcoded** | `app/core/config.py:13` | Rimuovere il default: `SECRET_KEY: str` senza valore — pydantic-settings farà crashare l'app se mancante |
| 3 | **JWT nel cookie senza flag `HttpOnly`** | `static/js/login.js` | Impostare il cookie server-side: `response.set_cookie("access_token", token, httponly=True, samesite="lax")` |
| 4 | **Password salvata in chiaro nel `localStorage`** | `static/js/register.js:63` | Rimuovere completamente `localStorage.setItem('userCredentials', ...)` |

#### Alte

| # | Problema | Posizione | Fix |
|---|---|---|---|
| 5 | **`echo=True` nel DB engine** — logga query SQL con parametri in produzione | `app/db/database.py:7` | `echo=os.getenv("SQL_ECHO", "false") == "true"` |
| 6 | **Nessun rate limiting su `/login`** — vulnerabile a brute force | `app/api/routes.py` | Aggiungere `slowapi` o un middleware con contatore per IP |
| 7 | **Stacktrace esposto al client** con `detail=str(e)` | `app/api/routes.py:43,80` | Loggare l'eccezione server-side e rispondere con messaggio generico |
| 8 | **Token JWT con durata 24h** — finestra di attacco troppo lunga | `app/core/config.py:15` | Ridurre a 15–30 min e aggiungere endpoint `/refresh` con refresh token |

---

### Bug nel codice

| # | Problema | Posizione | Fix |
|---|---|---|---|
| 9 | **Bug indentazione nel retry loop** — `backoff *= 2` e `continue` sono fuori dal blocco `except (ReadTimeout, ConnectError)` | `amazon_tracking_service.py:110–112` | Rientrare correttamente le due righe dentro il blocco `except` |
| 10 | **`print(email_query)` lasciato nel codice** di produzione | `user_service.py:15` | Rimuovere il print |

---

### Debito tecnico

| # | Problema | Posizione | Fix |
|---|---|---|---|
| 11 | **Typo `acces_token`** (manca una `s`) | `security.py:42`, `routes.py:18` | Rinominare in `create_access_token` (aggiornare tutti i riferimenti) |
| 12 | **Typo `sytemService`** (manca la `s`) | `system_service.py`, `routes.py`, `main.py` | Rinominare in `SystemService` |
| 13 | **Modelli duplicati in `models.py`** | `app/models/models.py` | Ridefinisce WeatherData, ExchangeData, NewsArticle — eliminare il file |
| 14 | **Codice commentato** | `app/api/routes.py:147–149` | Rimuovere il blocco `@router.get("/amazon")` commentato |
| 15 | **Docstring template non compilati** | `app/core/security.py:21–31` | Rimuovere o completare il template `:param Description` |

---

### Mancanze architetturali

| # | Cosa manca | Priorita | Soluzione consigliata |
|---|---|---|---|
| 16 | **Migrazioni DB** | Alta | Aggiungere Alembic — `create_all` al startup non gestisce modifiche allo schema |
| 17 | **Health check endpoint** | Media | `GET /health` che verifica la connessione DB — utile per Docker healthcheck e load balancer |
| 18 | **Logging strutturato** | Media | Configurare logging con file handler e rotation (`RotatingFileHandler`) oppure usare `structlog` |
| 19 | **Validazione parametri URL** | Media | `city`, `base`, `target`, `topic` non hanno limiti di lunghezza — usare `Path(..., max_length=50)` |
| 20 | **`response_model` sugli endpoint** | Bassa | Aggiungere `response_model=` alle route per validazione output e documentazione Swagger precisa |
| 21 | **CI/CD** | Media | GitHub Actions con `pytest --cov` + `docker build` ad ogni push su `main` |

---

### Riepilogo priorita

```
CRITICA  -->  1, 2, 3, 4          (sicurezza — agire subito, ruotare le chiavi)
ALTA     -->  5, 6, 7, 8, 9, 16
MEDIA    -->  10, 17, 18, 19, 21
BASSA    -->  11, 12, 13, 14, 15, 20
```

Il progetto ha una base solida (tutto async/await, ORM corretto, service layer separato, JWT + bcrypt). Prima di esporre il servizio pubblicamente occorre risolvere almeno i punti 1–4.
