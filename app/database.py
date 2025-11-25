from pymongo import MongoClient
from config import MONGO_URI

client = MongoClient(MONGO_URI)
db = client["ecommerce_db"]

users_col = db["users"]
products_col = db["products"]
orders_col = db["orders"]
