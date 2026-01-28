from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func 
from app.db.database import Base

class WeatherData(Base):
    __tablename__ = "weather_records"

    id = Column(Integer, primary_key=True, index=True)
    city = Column(String(100))
    temperature = Column(Float)
    description = Column(String(255))
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

class ExchangeData(Base):
    __tablename__= "exchange_rates"

    id = Column(Integer, primary_key=True, index=True)
    base_currency = Column(String(3))
    target_currency = Column(String(3))
    rate = Column(Float)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

