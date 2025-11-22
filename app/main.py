from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .db import db, client
from .routers import auth, products, categories, cart, orders

app = FastAPI(title="Ecom API", version="0.1")

# CORS - change origins for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# include routers
app.include_router(auth.router)
app.include_router(products.router)
app.include_router(categories.router)
app.include_router(cart.router)
app.include_router(orders.router)


@app.on_event("startup")
async def startup_event():
    # create any needed indexes (text index for products search example)
    await db.products.create_index([("title", "text"), ("description", "text")])
    await db.users.create_index("email", unique=True)
    print("Startup: DB indexes ensured.")


@app.on_event("shutdown")
async def shutdown_event():
    client.close()
