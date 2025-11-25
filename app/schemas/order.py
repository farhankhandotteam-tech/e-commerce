# app/schemas/order.py
from pydantic import BaseModel
from typing import List

class OrderItem(BaseModel):
    product_id: str
    quantity: int

class OrderCreateModel(BaseModel):
    items: List[OrderItem]
