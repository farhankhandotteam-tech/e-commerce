from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import os
from config import IMAGE_DIR
from routers import users, products, orders

app = FastAPI()

# Create images folder if not exists
os.makedirs(IMAGE_DIR, exist_ok=True)

# Mount static files
app.mount("/images", StaticFiles(directory=IMAGE_DIR), name="images")

# Include routers
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(products.router, prefix="/products", tags=["Products"])
app.include_router(orders.router, prefix="/orders", tags=["Orders"])
