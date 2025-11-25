from pydantic import BaseModel
from typing import Optional

class Product(BaseModel):
    name: str
    description: str
    price: float
    stock: int
    image_url: Optional[str] = None
