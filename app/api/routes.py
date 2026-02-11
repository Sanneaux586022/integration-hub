from fastapi import APIRouter , Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.services.weather_service import weatherService
from app.services.exchange_service import exchangeService
from app.services.news_service import newsService
from sqlalchemy import select
from app.models.models import *
# from app.models.models import WeatherData, ExchangeData, NewsArticle

router = APIRouter()

@router.get("/weather/update/{city}")
async def update_weather(city : str, db: AsyncSession=Depends(get_db)):
    service = weatherService(db)

    try:
        weather_record = await service.get_and_save_weather(city)
        return {
            "status": "success",
            "message": f"Dati meteo per {city}, salvati correttamente",
            "data": {
                "id": weather_record.id,
                "temp": weather_record.temperature,
                "desc": weather_record.description
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore durante l'aggiornamento della temperatura: {str(e)}")

@router.get("/exchange/update/{base}/{target}")
async def update_exchange(base: str , target: str, db: AsyncSession=Depends(get_db)):
    service = exchangeService(db)

    try:
        exchange_record = await service.get_and_save_rate(base, target)

        return {
            "status": "success",
            "message": f"Cambio {base.upper()}/{target.upper()} aggiornato.",
            "data": {
                "id": exchange_record.id,
                "rate": exchange_record.rate,
                "timestamp": exchange_record.timestamp

            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore durante l'aggiornamento del cambio: {str(e)}")
    
@router.get("/news/update/{topic}")
async def update_news(topic: str, db: AsyncSession=Depends(get_db)):

    service = newsService(db)

    try:
        articles = await service.fetch_and_save_news(topic)
        
        return {
            "status": "success",
            "count": len(articles),
            "articles": [{"title": article.title, "source": article.source} for article in articles]
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.get("/dashboard")
async def get_dashboard(db: AsyncSession=Depends(get_db)):
    # 1.Recuperiamo l'ultimo meteo
    weather_query = await db.execute(select(WeatherData).order_by(WeatherData.timestamp.desc()).limit(1))
    latest_weather = weather_query.scalar_one_or_none()

    # 2.Recuperiamo l'ultimo cambio EUR/USD
    exchange_query = (await db.execute(select(ExchangeData).filter_by(target_currency="USD")
                                       .order_by(ExchangeData.timestamp.desc()).limit(1)))
    latest_exchange = exchange_query.scalar_one_or_none()

    # 3.Recuperiamo le ultime 3 notizie
    news_query = await db.execute(select(NewsArticle).order_by(NewsArticle.timestamp.desc()).limit(3))
    latest_news = news_query.scalars().all()

    return {
        "weather": latest_weather,
        "exchange": latest_exchange,
        "news": latest_news
    }