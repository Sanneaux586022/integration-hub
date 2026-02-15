import httpx
import os
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.weatherData import WeatherData
from app.core.config import settings

class weatherService:
    def __init__(self, db_session: AsyncSession):
        self.api_key = settings.WEATHER_API_KEY
        self.base_url = "https://api.openweathermap.org/data/2.5/weather"
        self.db = db_session

    async def get_and_save_weather(self, city:str):
        async with httpx.AsyncClient() as client:
            response = await client.get(
                self.base_url,
                params={"q": city, "appid":self.api_key,
                        "units":"metric", "lang": "it"}
            )
            response.raise_for_status()
            data = response.json()

        new_record = WeatherData(
            city=data["name"],
            temperature=data["main"]["temp"],
            description=data["weather"][0]["description"]
        )

        self.db.add(new_record)
        await self.db.commit()
        await self.db.refresh(new_record)

        return new_record
    