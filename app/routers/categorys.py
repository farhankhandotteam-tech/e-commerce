from fastapi import APIRouter, HTTPException, Depends
from typing import List
from bson import ObjectId
from db import db
from models import CategoryCreate
from deps import admin_required
from datetime import datetime

router = APIRouter(prefix="/categories", tags=["categories"])

@router.post("/", dependencies=[Depends(admin_required)])
async def create_category(payload: CategoryCreate):
    data = payload.dict()
    data.update({"created_at": datetime.utcnow()})
    res = await db.categories.insert_one(data)
    return {"message": "Category created", "category_id": str(res.inserted_id)}

@router.get("/", response_model=List[dict])
async def list_categories():
    cats = []
    async for c in db.categories.find():
        c["_id"] = str(c["_id"])
        cats.append(c)
    return cats

@router.patch("/{cat_id}", dependencies=[Depends(admin_required)])
async def update_category(cat_id: str, payload: CategoryCreate):
    res = await db.categories.update_one({"_id": ObjectId(cat_id)}, {"$set": payload.dict()})
    if res.matched_count == 0:
        raise HTTPException(404, "Category not found")
    return {"message": "Category updated"}

@router.delete("/{cat_id}", dependencies=[Depends(admin_required)])
async def delete_category(cat_id: str):
    res = await db.categories.delete_one({"_id": ObjectId(cat_id)})
    if res.deleted_count == 0:
        raise HTTPException(404, "Category not found")
    return {"message": "Category deleted"}
