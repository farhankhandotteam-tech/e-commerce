from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from bson import ObjectId
from db import db
from models import ProductCreate
from deps import get_current_user, admin_required
from utils import oid_str
from datetime import datetime

router = APIRouter(prefix="/products", tags=["products"])

@router.post("/", dependencies=[Depends(admin_required)])
async def create_product(payload: ProductCreate):
    data = payload.dict()
    data.update({"created_at": datetime.utcnow(), "updated_at": datetime.utcnow()})
    res = await db.products.insert_one(data)
    return {"message": "Product created", "product_id": str(res.inserted_id)}

@router.get("/", response_model=List[dict])
async def list_products(q: Optional[str] = None, page: int = 1, limit: int = 20):
    skip = (page - 1) * limit
    query = {}
    if q:
        query = {"$text": {"$search": q}}
    cursor = db.products.find(query).skip(skip).limit(limit)
    items = []
    async for p in cursor:
        p["_id"] = str(p["_id"])
        items.append(p)
    return items

@router.get("/{product_id}")
async def get_product(product_id: str):
    p = await db.products.find_one({"_id": ObjectId(product_id)})
    if not p:
        raise HTTPException(404, "Product not found")
    p["_id"] = str(p["_id"])
    return p

@router.patch("/{product_id}", dependencies=[Depends(admin_required)])
async def update_product(product_id: str, payload: ProductCreate):
    data = {k: v for k, v in payload.dict().items() if v is not None}
    data["updated_at"] = datetime.utcnow()
    res = await db.products.update_one({"_id": ObjectId(product_id)}, {"$set": data})
    if res.matched_count == 0:
        raise HTTPException(404, "Product not found")
    return {"message": "Product updated"}

@router.delete("/{product_id}", dependencies=[Depends(admin_required)])
async def delete_product(product_id: str):
    res = await db.products.delete_one({"_id": ObjectId(product_id)})
    if res.deleted_count == 0:
        raise HTTPException(404, "Product not found")
    return {"message": "Product deleted"}
