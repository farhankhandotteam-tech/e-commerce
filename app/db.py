from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

MONGO_URL = os.getenv("MONGO_URL")
DB_NAME = os.getenv("MONGO_DB_NAME")

try:
    client = MongoClient(MONGO_URL)
    db = client[DB_NAME]
    print("MongoDB Connected Successfully")
except Exception as e:
    print("MongoDB Connection Error:", e)
    db = None

# Collections
users_col = db["users"]
products_col = db["products"]
orders_col = db["orders"]
cart_col = db["cart"]
