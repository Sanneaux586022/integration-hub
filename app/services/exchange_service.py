import httpx
import os
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.models import ExchangeData

class exchangeService:
    def __init__(self, db_session: AsyncSession):
        self.api_key = os.getenv("EXCHANGE_API_KEY")
        self.base_url = f"https://v6.exchangerate-api.com/v6/{self.api_key}/latest/"
        self.db = db_session

    async def get_and_save_rate(self, base: str, target:str):
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}{base.upper()}")
            response.raise_for_status()

            if response.status_code != 200:
                raise Exception(f"Errore API Exchange : {response.text}")

            data = response.json()

            rate_value = data.get("conversion_rates", {}).get(target.upper())

            if rate_value is None:
                raise ValueError(f"Tasso per {target} non trovato nell'API.")
            
            new_rate = ExchangeData(
                base_currency = base.upper(),
                target_currency = target.upper(),
                rate = rate_value
            )
            self.db.add(new_rate)
            await self.db.commit()
            await self.db.refresh(new_rate)

            return new_rate
        

