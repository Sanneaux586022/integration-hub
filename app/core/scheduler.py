from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.db.database import AsyncSessionLocal
from app.services.weather_service import weatherService
from app.services.exchange_service import exchangeService
from app.services.news_service import newsService

scheduler = AsyncIOScheduler()

async def scheduled_update():
    async with AsyncSessionLocal() as db:
        print("--- [SCHEDULER] Avvio aggiornamento dati ---")
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
            print(f"--- [SCHEDULER] ERRORE: {str(e)}")

        print("--- [SCHEDULER] Dati salvati con successo ---")

# Programmiamo il task : ogni 3 ore
scheduler.add_job(scheduled_update, "interval", hours=1)