from pydantic import BaseSettings, AnyHttpUrl
from typing import List, Optional

class Settings(BaseSettings):
    MONGO_URI: str = "mongodb+srv://commerce:commerce@cluster0.9sufkgb.mongodb.net/"
    DB_NAME: str = "ecom_db"
    SECRET_KEY: str = "change-me-to-a-strong-secret"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    BACKEND_CORS_ORIGINS: Optional[List[AnyHttpUrl]] = None

    class Config:
        env_file = ".env"

settings = Settings()
