from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Any
from datetime import datetime

# ---- Auth / User ----
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: str = Field(..., alias="_id")
    name: str
    email: EmailStr
    role: str = "user"

class UserInDB(UserOut):
    password: str

# ---- Product ----
class ProductBase(BaseModel):
    title: str
    description: Optional[str] = None
    price: float
    stock: int = 0
    images: Optional[List[str]] = []
    category: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class ProductCreate(ProductBase):
    pass

class ProductOut(ProductBase):
    id: str = Field(..., alias="_id")

# ---- Category ----
class CategoryBase(BaseModel):
    name: str
    slug: Optional[str] = None
    description: Optional[str] = None

class CategoryCreate(CategoryBase):
    pass

class CategoryOut(CategoryBase):
    id: str = Field(..., alias="_id")

# ---- Cart ----
class CartItem(BaseModel):
    product_id: str
    qty: int = 1

class CartOut(BaseModel):
    user_id: str
    items: List[dict] = []
    updated_at: Optional[datetime] = None

# ---- Orders ----
class OrderItem(BaseModel):
    product_id: str
    qty: int
    price: float

class OrderCreate(BaseModel):
    items: Optional[List[OrderItem]] = None  # or use server-side cart
    address: dict
    payment_method: str = "cod"  # cod or online

class OrderOut(BaseModel):
    id: str = Field(..., alias="_id")
    user_id: str
    items: List[Any]
    total: float
    payment_status: str
    order_status: str
    created_at: Optional[datetime] = None
