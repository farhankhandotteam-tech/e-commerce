from motor.motor_asyncio import AsyncIOMotorClient
from .config_old import settings

client = AsyncIOMotorClient("mongodb+srv://commerce:commerce@cluster0.9sufkgb.mongodb.net/")
db = client[settings.db]
