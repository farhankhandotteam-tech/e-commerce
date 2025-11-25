# app/database.py
from pymongo import MongoClient
from app.database import users_collection

# Connect to MongoDB
client = MongoClient("mongodb+srv://commerce:commerce@cluster0.9sufkgb.mongodb.net/")
db = client["ecommerce"]  # your database name

# Collections
users_col = db["users"]
products_col = db["products"]
orders_col = db["orders"]
cart_col = db["cart"]
