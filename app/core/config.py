import os 
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # Parametri Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "mariadb+aiomysql://user:pass@db:3306/dbname")

    # Parametri Sicurezza

    SECRET_KEY: str = os.getenv("SECRET_KEY", "una_chiave_segreta_molto_lunga")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24

    # Parametri API
    EXCHANGE_API_KEY: str = os.getenv("EXCHANGE_API_KEY")
    NEWS_API_KEY: str = os.getenv("NEWS_API_KEY")
    WEATHER_API_KEY: str = os.getenv("WEATHER_API_KEY")

settings = Settings()