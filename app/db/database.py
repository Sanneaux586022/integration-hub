from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
import os
from app.core.config import settings


# Creazione del motore asincrono
engine = create_async_engine(settings.DATABASE_URL, echo=True, pool_recycle=3600)

# Sessione per le query
AsyncSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session