from pydantic import BaseModel
from typing import List
#from app.database import orders_collection, products_collection
from fastapi import APIRouter, Depends, HTTPException
from app.dependencies import get_current_user
from app.models.order import OrderCreateModel
from bson import ObjectId

class OrderProduct(BaseModel):
    product_id: str
    quantity: int

class Order(BaseModel):
    products: List[OrderProduct]
