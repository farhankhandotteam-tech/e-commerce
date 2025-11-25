# app/database.py
from pymongo import MongoClient

client = MongoClient("mongodb+srv://commerce:commerce@cluster0.9sufkgb.mongodb.net/")
db = client["ecommerce"]

# Collections
users_collection = db["users"]
products_collection = db["products"]
orders_collection = db["orders"]
cart_collection = db["cart"]
