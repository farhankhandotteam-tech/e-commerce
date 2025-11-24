from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

MONGO_URI = os.getenv("mongodb+srv://commerce:commerce@cluster0.9sufkgb.mongodb.net/ecommerce")

client = None
db = None

try:
    client = MongoClient(MONGO_URI)
    db = client.get_default_database()

    if db is None:
        raise Exception("Database not found in URI!")

    print("MongoDB Connected Successfully")

except Exception as e:
    print("MongoDB Connection Error:", e)

# Collections
if db:
    users_col = db["users"]
    products_col = db["products"]
    orders_col = db["orders"]
else:
    users_col = None
    products_col = None
    orders_col = None
