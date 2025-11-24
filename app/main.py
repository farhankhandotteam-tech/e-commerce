from fastapi import FastAPI, HTTPException, Depends, File, UploadFile
from fastapi.security import OAuth2PasswordBearer
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime, timedelta
from jose import jwt, JWTError
from passlib.context import CryptContext
from pymongo import MongoClient
from bson import ObjectId
import shutil
import os

# -----------------------------
# FastAPI App
# -----------------------------
app = FastAPI()

# -----------------------------
# Password & Auth Setup
# -----------------------------
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = "YOUR_SECRET_KEY"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def hash_password(password: str):
    password_bytes = password.encode("utf-8")[:72]  # bcrypt max 72 bytes
    return pwd_context.hash(password_bytes)

def verify_password(plain_password: str, hashed_password: str):
    password_bytes = plain_password.encode("utf-8")[:72]  # same truncation
    return pwd_context.verify(password_bytes, hashed_password)

def create_access_token(data: dict, expires_delta=None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_access_token(token: str):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None

# -----------------------------
# Database Setup
# -----------------------------
client = MongoClient("mongodb+srv://commerce:commerce@cluster0.9sufkgb.mongodb.net/")
db = client["ecommerce_db"]
users_col = db["users"]
products_col = db["products"]
orders_col = db["orders"]

# -----------------------------
# Pydantic Models
# -----------------------------
class UserRegister(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: Optional[str] = "user"

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Product(BaseModel):
    name: str
    description: str
    price: float
    stock: int
    image_url: Optional[str] = None

class OrderProduct(BaseModel):
    product_id: str
    quantity: int

class Order(BaseModel):
    products: List[OrderProduct]

# -----------------------------
# Dependencies
# -----------------------------
def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid authentication")
    user = users_col.find_one({"_id": ObjectId(payload["_id"])})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user["_id"] = str(user["_id"])
    return user

def admin_required(user=Depends(get_current_user)):
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return user

# -----------------------------
# Serve Images
# -----------------------------
IMAGE_DIR = "images"
os.makedirs(IMAGE_DIR, exist_ok=True)
app.mount("/images", StaticFiles(directory=IMAGE_DIR), name="images")

# -----------------------------
# User Routes
# -----------------------------
@app.post("/register")
def register(user: UserRegister):
    if users_col.find_one({"email": user.email}):
        raise HTTPException(400, "User already exists")
    user_dict = user.dict()
    user_dict["password"] = hash_password(user.password)
    result = users_col.insert_one(user_dict)
    return {"msg": "User registered", "id": str(result.inserted_id)}

@app.post("/login")
def login(user: UserLogin):
    db_user = users_col.find_one({"email": user.email})
    if not db_user or not verify_password(user.password, db_user["password"]):
        raise HTTPException(401, "Invalid credentials")
    token = create_access_token({"_id": str(db_user["_id"]), "role": db_user["role"]})
    return {"access_token": token, "token_type": "bearer"}

# -----------------------------
# Product Routes
# -----------------------------
@app.get("/products")
def get_products():
    return [{"_id": str(p["_id"]), **p} for p in products_col.find()]

@app.get("/products/{id}")
def get_product(id: str):
    product = products_col.find_one({"_id": ObjectId(id)})
    if not product:
        raise HTTPException(404, "Product not found")
    product["_id"] = str(product["_id"])
    return product

@app.post("/products")
def create_product(product: Product, image: UploadFile = File(...), user=Depends(admin_required)):
    image_path = os.path.join(IMAGE_DIR, image.filename)
    with open(image_path, "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)
    product_dict = product.dict()
    product_dict["image_url"] = f"/images/{image.filename}"
    result = products_col.insert_one(product_dict)
    return {"msg": "Product created", "id": str(result.inserted_id), "image_url": product_dict["image_url"]}

@app.put("/products/{id}")
def update_product(id: str, product: Product, image: Optional[UploadFile] = None, user=Depends(admin_required)):
    update_data = product.dict()
    if image:
        image_path = os.path.join(IMAGE_DIR, image.filename)
        with open(image_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
        update_data["image_url"] = f"/images/{image.filename}"
    result = products_col.update_one({"_id": ObjectId(id)}, {"$set": update_data})
    if result.matched_count == 0:
        raise HTTPException(404, "Product not found")
    return {"msg": "Product updated"}

@app.delete("/products/{id}")
def delete_product(id: str, user=Depends(admin_required)):
    product = products_col.find_one({"_id": ObjectId(id)})
    if not product:
        raise HTTPException(404, "Product not found")
    if "image_url" in product:
        img_path = product["image_url"].replace("/images/", IMAGE_DIR + "/")
        if os.path.exists(img_path):
            os.remove(img_path)
    products_col.delete_one({"_id": ObjectId(id)})
    return {"msg": "Product deleted"}

# -----------------------------
# Order Routes
# -----------------------------
@app.post("/orders")
def create_order(order: Order, user=Depends(get_current_user)):
    total_price = 0
    order_items = []
    for item in order.products:
        prod = products_col.find_one({"_id": ObjectId(item.product_id)})
        if not prod:
            raise HTTPException(404, f"Product {item.product_id} not found")
        if prod["stock"] < item.quantity:
            raise HTTPException(400, f"Not enough stock for {prod['name']}")
        total_price += prod["price"] * item.quantity
        order_items.append({"product_id": item.product_id, "quantity": item.quantity})
        products_col.update_one({"_id": ObjectId(item.product_id)}, {"$inc": {"stock": -item.quantity}})
    order_doc = {"user_id": user["_id"], "products": order_items, "total_price": total_price, "status": "pending"}
    result = orders_col.insert_one(order_doc)
    return {"msg": "Order created", "id": str(result.inserted_id)}

@app.get("/orders")
def get_orders(user=Depends(get_current_user)):
    if user["role"] == "admin":
        orders = list(orders_col.find())
    else:
        orders = list(orders_col.find({"user_id": user["_id"]}))
    for o in orders:
        o["_id"] = str(o["_id"])
    return orders

@app.get("/orders/{id}")
def get_order(id: str, user=Depends(get_current_user)):
    order = orders_col.find_one({"_id": ObjectId(id)})
    if not order:
        raise HTTPException(404, "Order not found")
    if user["role"] != "admin" and order["user_id"] != user["_id"]:
        raise HTTPException(403, "Access denied")
    order["_id"] = str(order["_id"])
    return order

@app.put("/orders/{id}/status")
def update_order_status(id: str, status: str, user=Depends(admin_required)):
    result = orders_col.update_one({"_id": ObjectId(id)}, {"$set": {"status": status}})
    if result.matched_count == 0:
        raise HTTPException(404, "Order not found")
    return {"msg": "Order status updated"}
