from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.db.database import AsyncSessionLocal
from app.services.weather_service import weatherService
from app.services.exchange_service import exchangeService
from app.services.news_service import newsService
from app.services.amazon_tracking_service import AmazonTrackingService
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)
scheduler = AsyncIOScheduler()

async def scheduled_update():
    async with AsyncSessionLocal() as db:
        logger.info("--- [SCHEDULER] Avvio aggiornamento dati ---")
        try:
            # 2. Aggiorna il meteo
            weather = weatherService(db)
            await weather.get_and_save_weather("Verona")

            # 2. Aggiorna Cambi
            exchange = exchangeService(db)
            await exchange.get_and_save_rate("EUR", "USD")

            # 3. Aggiorna News
            news = newsService(db)
            await news.fetch_and_save_news("tecnologia")
        except Exception as e:
            logger.info(f"--- [SCHEDULER] ERRORE: {str(e)}")

        logger.info("--- [SCHEDULER] Dati salvati con successo ---")

async def scheduled_ricerca_amazon():
    keywords = [kw.strip() for kw in settings.ARTICOLI_RICERCA.split(',')]
    if not keywords:
        return

    # Trucco: usiamo il numero di ore passate dal 1970 diviso 12 
    # per ottenere un indice che cambia ogni 12 ore
    import time
    indice_rotazione = int(time.time() // (12 * 3600)) % len(keywords)
    kw_da_cercare = keywords[indice_rotazione]

    async with AsyncSessionLocal() as db:
        try:
            logger.info(f"CONSUMO API: Ricerca rotativa per: {kw_da_cercare} (Indice {indice_rotazione})")
            tracker = AmazonTrackingService(db)
            await tracker.get_risultati_articoli(keyword=kw_da_cercare)
        except Exception as e:
            logger.error(f"Errore nella ricerca rotativa di '{kw_da_cercare}': {e}")