from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

MONGO_URL = os.getenv("mongodb+srv://commerce:commerce@cluster0.9sufkgb.mongodb.net/")

try:
    client = MongoClient(MONGO_URL)
    db = client.get_default_database()
except Exception as e:
    print("MongoDB Connection Error:", e)
    db = None

# Collections
users_col = db["users"]
products_col = db["products"]
orders_col = db["orders"]
cart_col = db["cart"]
