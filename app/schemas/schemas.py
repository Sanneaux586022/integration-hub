from pydantic import BaseModel
from datetime import datetime

class WeatherBase(BaseModel):
    city: str
    temperature: float
    description: str

class WeatherCreate(WeatherBase):
    pass

class WeatherResponse(WeatherBase):
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True