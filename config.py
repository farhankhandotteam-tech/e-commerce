from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    MONGO_URI: str = "mongodb+srv://commerce:commerce@cluster0.9sufkgb.mongodb.net/"
    DB_NAME: str = "ecommerce"

    class Config:
        env_file = ".env"

settings = Settings()
