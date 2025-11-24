import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv


load_dotenv()
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017')


client = AsyncIOMotorClient(MONGO_URI)
# Use db name from URI if provided or fallback
try:
db = client.get_default_database()
except Exception:
db = client['ecommerce_db']


users_col = db['users']
products_col = db['products']
carts_col = db['carts']
orders_col = db['orders']