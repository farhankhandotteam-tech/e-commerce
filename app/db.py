from dotenv import load_dotenv
import os

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))

MONGO_URI = os.getenv("MONGO_URI")
if not MONGO_URI:
    raise Exception("MONGO_URI not found in .env file")

# MongoDB client setup
from pymongo import MongoClient
client = MongoClient(MONGO_URI)
db = client["mydatabase"]
products_col = db["products"]
