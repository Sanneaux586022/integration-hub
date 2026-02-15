import httpx
import os
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.newsArticle import NewsArticle
from datetime import datetime
from app.core.config import settings


class newsService:
    def __init__(self, db_session: AsyncSession):
        self.api_key = settings.NEWS_API_KEY
        # self.base_url = "https://newsapi.org/v2/top-headlines"
        self.base_url = "https://newsapi.org/v2/everything"
        self.db = db_session


    async def fetch_and_save_news(self, query: str):

        async with httpx.AsyncClient() as client:
            response = await client.get(
                self.base_url,
                params={
                    "q": query, 
                    "apikey": self.api_key,
                    "language": "it",
                    "sortBy": "publishedAt"
                    }
            )            
            response.raise_for_status()
            data = response.json()
            articles = data.get("articles", [])[:5]
    
            new_records = []

            for art in articles:
                raw_date = art.get("publishedAt")
                clean_date = None

                if raw_date:
                    clean_date = datetime.fromisoformat(raw_date.replace("Z", "+00:00"))
                news_item = NewsArticle(
                    source=art["source"]["name"],
                    title=art["title"],
                    url=art["url"],
                    published_at=clean_date
                )
                self.db.add(news_item)
                new_records.append(news_item)
            
            await self.db.commit()
            return new_records