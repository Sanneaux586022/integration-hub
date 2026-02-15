from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func 
from app.db.database import Base

class NewsArticle(Base):
    __tablename__ = "news_articles"

    id = Column(Integer, primary_key=True, index=True)
    source = Column(String(100))
    title = Column(String(500))
    url = Column(String(500))
    published_at = Column(DateTime)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())