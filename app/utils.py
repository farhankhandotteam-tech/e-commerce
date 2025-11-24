from pydantic import BaseModel
from typing import Optional

class ProductIn(BaseModel):
    name: str
    description: str
    price: float
    image_url: Optional[str] = None  # store image path or URL

class ProductOut(BaseModel):
    id: str
    name: str
    description: str
    price: float
    image_url: Optional[str]
