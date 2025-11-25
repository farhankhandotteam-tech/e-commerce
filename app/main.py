import sys
import os

# Add current folder to sys.path so config.py can be imported
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from config import IMAGE_DIR
from routers import users, products, orders, admin, cart

app = FastAPI()

# Create images folder if not exists
os.makedirs(IMAGE_DIR, exist_ok=True)

# Mount static files
app.mount("/images", StaticFiles(directory=IMAGE_DIR), name="images")

# Include routers
app.include_router(users.router, prefix="/users")
app.include_router(products.router, prefix="/products")
app.include_router(orders.router, prefix="/orders")
app.include_router(admin.router, prefix="/admin")
app.include_router(cart.router, prefix="/cart")