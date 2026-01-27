import httpx
import os

class weatherService:
    def __init__(self):
        self.api_key = os.getenv("WEATHER_API_KEY")
        self.base_url = "https://api.openweathermap.org/data/2.5/weather"

    async def fetch_and_normalize(self, city):
        async with httpx.Asyncclient() as client:
            response = await client.get(
                self.base_url,
                params={"q": city, "appid":self.api_key,
                        "units":"metric", "lang": "it"}
            )
            data = response.json()

            return {
                "city": data["name"],
                "temperature": data["main"]["temp"],
                "description": data["weather"][0]["description"]
            }