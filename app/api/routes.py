import os
from fastapi import APIRouter , Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.services.weather_service import weatherService
from app.services.exchange_service import exchangeService
from app.services.news_service import newsService
from app.services.system_service import sytemService
from app.services.user_service import userService
from sqlalchemy import select
from app.models.exchangeData import ExchangeData
from app.models.newsArticle import NewsArticle
from app.models.weatherData import WeatherData
from app.models.user import User
from zoneinfo import ZoneInfo
from app.schemas.users import UserOut, UserCreate, UserLogin, Token
from app.core.security import create_acces_token
from datetime import datetime, timedelta
from app.core.security import get_current_user
from app.core.config import settings


router = APIRouter()

@router.get("/weather/update/{city}")
async def update_weather(city : str, db: AsyncSession=Depends(get_db), current_user: User = Depends(get_current_user)):
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
            },
            "user": current_user.username
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore durante l'aggiornamento della temperatura: {str(e)}")

@router.get("/exchange/update/{base}/{target}")
async def update_exchange(base: str , target: str, db: AsyncSession=Depends(get_db), current_user: User = Depends(get_current_user)):
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
async def update_news(topic: str, db: AsyncSession=Depends(get_db), current_user: User = Depends(get_current_user)):

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
async def get_dashboard(db: AsyncSession=Depends(get_db), current_user: User = Depends(get_current_user)):
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

@router.get("/weather/history")
async def last_24_hours_temperatures(db: AsyncSession=Depends(get_db), current_user: User = Depends(get_current_user)):
    weather_query = await db.execute(select(WeatherData).order_by(WeatherData.timestamp.desc()).limit(24))
    history = weather_query.scalars().all()

    history.reverse()

    return [

        {"time": h.timestamp.astimezone(ZoneInfo("Europe/Rome")).strftime("%H:%M"), "temp": h.temperature}
        for h in history
    ]

@router.get("/system-stats")
async def get_stats(current_user: User = Depends(get_current_user)):  
    stats = sytemService.get_syst_stats()
    return stats

@router.post("/registrazione", response_model=UserOut)
async def registra_utente(user_in: UserCreate, db: AsyncSession=Depends(get_db)):
    service_user = userService(db)

    return await service_user.create_user(user_in)

@router.post("/login", response_model=Token)
# async def effettua_login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession=Depends(get_db)):
async def effettua_login(login_data: UserLogin, db: AsyncSession=Depends(get_db)):
    
    service_user = userService(db)

    user =  await service_user.authenticate_user(email= login_data.email, password=login_data.plain_password)
    access_token_expires = timedelta(minutes= settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    access_token = create_acces_token(
        data= {"sub": user.email},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model= UserOut)
async def leggi_mio_profilo(current_user: User = Depends(get_current_user)):
    return current_user