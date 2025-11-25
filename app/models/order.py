from pydantic import BaseModel
from typing import List

class OrderProduct(BaseModel):
    product_id: str
    quantity: int

class Order(BaseModel):
    products: List[OrderProduct]
