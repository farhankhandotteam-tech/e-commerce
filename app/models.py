from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional


class UserCreate(BaseModel):
 name: str
 email: EmailStr
 password: str


class UserOut(BaseModel):
 id: str = Field(...)
 name: str
 email: EmailStr
 role: str

class Token(BaseModel):
 access_token: str
 token_type: str = 'bearer'


class ProductIn(BaseModel):
 name: str
 description: Optional[str] = ''
 price: float
 stock: int
 category: Optional[str] = None

class ProductOut(ProductIn):
 id: str

class CartItem(BaseModel):
 product_id: str
 quantity: int = 1

class Cart(BaseModel):
 id: Optional[str]
 user_id: str
 items: List[CartItem] = []


class OrderItem(BaseModel):
 product_id: str
 quantity: int
 price: float


class Order(BaseModel):
 id: Optional[str]
 user_id: str
 items: List[OrderItem]
 total_amount: float
 status: str = 'pending'