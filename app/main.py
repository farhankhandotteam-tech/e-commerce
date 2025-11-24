# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import logging

# import routers (each router module should expose `router`)
from app.routers import users, products, admin, cart, orders

logger = logging.getLogger("uvicorn.error")

app = FastAPI(
    title="Ecommerce API",
    description="Simple e-commerce backend (FastAPI + MongoDB). Admin / user roles with JWT auth.",
    version="1.0.0",
)

# CORS - allow from anywhere for development; restrict this in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # change to specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# include routers
app.include_router(users.router)
app.include_router(products.router)
app.include_router(admin.router)
app.include_router(cart.router)
app.include_router(orders.router)


@app.get("/", tags=["health"])
async def root():
    """
    Health check / root endpoint.
    """
    return {"status": "ok", "message": "Ecommerce API up"}


@app.on_event("startup")
async def startup_event():
    logger.info("Starting Ecommerce API...")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down Ecommerce API...")
