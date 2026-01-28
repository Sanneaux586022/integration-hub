from fastapi import APIRouter , Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.services.weather_service import weatherService
from app.services.exchange_service import exchangeService
import time

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
        raise HTTPException(status_code=500, detail=f"Errore durante l'aggiornamento: {str(e)}")

@router.get("/exchange/update/{base}/{target}")
async def update_exchange(base: str , target: str, db: AsyncSession):
    service = exchangeService(db)

    try:
        exchange_record = await service.get_and_save_rate(base, target)

        return {
            "status": "success",
            "message": f"Cambio {base}/{target} aggiornato.",
            "data": {
                "id": exchange_record.id,
                "rate": exchange_record.rate,
                "timestamp": exchange_record.timestamp

            }
        }