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

class NewsArticle(Base):
    __tablename__ = "news_articles"

    id = Column(Integer, primary_key=True, index=True)
    source = Column(String(100))
    title = Column(String(500))
    url = Column(String(500))
    published_at = Column(DateTime)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())